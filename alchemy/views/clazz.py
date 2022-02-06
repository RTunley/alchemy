import flask
from flask import g
from alchemy import db, models, auth_manager, file_input, file_output
from alchemy.reports import report_types, data_manager
import urllib
import os

bp_clazz = flask.Blueprint('clazz', __name__)

@bp_clazz.url_value_preprocessor
def url_value_preprocessor(endpoint, values):
    g.clazz = models.Clazz.query.get_or_404(values.pop('clazz_id'))
    g.student_paper_report_sections_string = 'OverviewSection,AdjacentGradesSection,ClazzSummarySection,CohortSummarySection,HighlightsSection'
    g.clazz_paper_report_sections_string = 'OverviewSection,OverviewPlotSection,OverviewDetailsSection,GradeOverviewSection,TagOverviewSection,QuestionOverviewSection,TagDetailsSection,QuestionDetailsSection'

@bp_clazz.url_defaults
def url_defaults(endpoint, values):
    if 'clazz_id' not in values:
        values['clazz_id'] = g.clazz.id

@bp_clazz.before_request
def before_request():
    g.html_title = f'Class - {g.clazz.code}'

@bp_clazz.route('/')
@auth_manager.require_group
def index():
    # for paper in g.course.papers:
    #     paper.check_clazz_scores(g.clazz)
    student_course_profiles = data_manager.make_student_course_profiles(g.course, g.clazz.students)
    return flask.render_template('course/clazz/index.html', profiles = student_course_profiles)

@bp_clazz.route('/student_scores_update', methods=['POST'])
@auth_manager.require_group
def student_scores_update():
    update_data = flask.request.get_json()
    paper_id = update_data['paper_id']
    student_scores = update_data['student_scores']
    modified_students = update_data['modified_students']

    # Expected columns are:
    # student id, given name, family name, [question 1, question 2, ...], total raw, total percent, grade

    if len(modified_students) == 0:
        print('No student scores were modified')
        return {}
    paper = models.Paper.query.get_or_404(paper_id)

    question_col_start = 3
    for score_row in student_scores:
        question_col_end = len(score_row) - 3
        student_id, given_name, family_name = score_row[:question_col_start]
        if str(student_id) not in modified_students:
            continue
        question_cols = score_row[question_col_start:question_col_end]
        total_raw, total_percent, grade = score_row[question_col_end:]
        if len(question_cols) != len(paper.paper_questions):
            print('Error! Received', len(question_cols), 'question columns for student', student_id, 'but found', len(paper.paper_questions), 'questions for paper', paper_id, 'in database')
            continue
        for i, paper_question in enumerate(paper.paper_questions):
            new_value = question_cols[i]
            if type(new_value) == 'str' and new_value.strip() == '':
                new_value = None    # clear the score value
            else:
                try:
                    new_value = float(question_cols[i])
                except ValueError:
                    print('Bad score value:', question_cols[i])
                    continue
            score = models.Score.query.filter_by(paper_id = paper_id, student_id = student_id, question_id = paper_question.question_id).first()
            if score:
                score.value = new_value
            else:
                score = models.Score(paper_id = paper_id, question_id = paper_question.question_id, student_id = student_id, value = new_value)
                db.session.add(score)
    db.session.commit()
    clazz_paper_profile = data_manager.ClazzPaperProfile(g.clazz, paper)
    # Make an array of the complete table data to be shown in the HTML table,
    # i.e. in the same format as the student_scores array that was received.
    tally_list_array = []
    for tally in clazz_paper_profile.paper_score_tallies:
        # add student id and name
        tally_list = [tally.student.id, tally.student.aws_user.given_name, tally.student.aws_user.family_name]
        # add values for all questions, or an empty string if there is no score
        tally_list.extend([score.value if score else '' for score in tally.scores])
        # add other tally details
        tally_list.extend([tally.raw_total, tally.percent_total, tally.grade])
        tally_list_array.append(tally_list)
    # Return the table data in JSON form
    return flask.jsonify(scores_table_json = tally_list_array)

@bp_clazz.route('/paper_results')
@auth_manager.require_group
def paper_results():
    paper = models.Paper.query.get_or_404(flask.request.args.get('paper_id'))
    clazz_paper_profile = data_manager.ClazzPaperProfile(g.clazz, paper)
    return flask.render_template('course/clazz/paper_results.html', clazz_paper_profile = clazz_paper_profile)

@bp_clazz.route('/mc_results_input')
@auth_manager.require_group
def mc_results_input():
    clazz = models.Clazz.query.get_or_404(flask.request.args.get('clazz_id'))
    paper = models.Paper.query.get_or_404(flask.request.args.get('paper_id'))
    student = models.Student.query.get_or_404(flask.request.args.get('student_id'))

    mc_input_macro = '''
          {% import "course/clazz/student_mc_input_macro.html" as mc_input %}
          {{ mc_input.render_mc_results(paper, student) }}
    '''

    return flask.jsonify(mc_input_html = flask.render_template_string(mc_input_macro, paper = paper, student = student))

@bp_clazz.route('/paper_report/<int:paper_id>/')
@auth_manager.require_group
def paper_report(paper_id):
    paper = models.Paper.query.get_or_404(paper_id)
    section_selection_string = flask.request.args.get('section_selection_string_get')
    section_selections = section_selection_string.split(',')
    clazz_report = report_types.ClazzPaperReport(g.clazz, paper, section_selections)
    return flask.render_template('course/clazz/paper_report.html', clazz_report = clazz_report)
