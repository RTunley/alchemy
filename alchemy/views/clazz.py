import flask
from flask import g
from alchemy import db, models, auth_manager, score_manager, file_input, file_output
from alchemy.reports import report_types, data_manager
import os

bp_clazz = flask.Blueprint('clazz', __name__)

@bp_clazz.url_value_preprocessor
def url_value_preprocessor(endpoint, values):
    g.clazz = models.Clazz.query.get_or_404(values.pop('clazz_id'))

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
    for paper in g.course.papers:
        paper.check_clazz_scores(g.clazz)
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
        ordered_paper_questions = paper.ordered_paper_questions()
        if len(question_cols) != len(ordered_paper_questions):
            print('Error! Received', len(question_cols), 'question columns for student', student_id, 'but found', len(ordered_paper_questions), 'questions for paper', paper_id, 'in database')
            continue
        for i, paper_question in enumerate(ordered_paper_questions):
            new_value = question_cols[i]
            if type(new_value) == 'str' and new_value.strip() == '':
                new_value = None    # clear the score value
            else:
                try:
                    new_value = float(question_cols[i])
                except ValueError:
                    print('Bad score value:', question_cols[i])
                    continue
            score = models.Score.query.filter_by(paper_id = paper_id, user_id = student_id, question_id = paper_question.question_id).first()
            if score:
                score.value = new_value
            else:
                score = models.Score(paper_id = paper_id, question_id = paper_question.question_id, user_id = student_id, value = new_value)
                db.session.add(score)
    db.session.commit()
    score_set_list = score_manager.make_student_scoreset_list(g.clazz, paper)

    # Make an array of the complete table data to be shown in the HTML table,
    # i.e. in the same format as the student_scores array that was received.
    all_score_set_lists = []
    for score_set in score_set_list:
        # add student id and name
        score_set_list = [score_set.student.id, score_set.student.aws_user.given_name, score_set.student.aws_user.family_name]
        # add values for all questions, or an empty string if there is no score
        score_set_list.extend([score.value if score else '' for score in score_set.score_list])
        # add other score details
        score_set_list.extend([score_set.total, score_set.percentage, score_set.grade])
        all_score_set_lists.append(score_set_list)
    # Return the table data in JSON form
    return flask.jsonify(scores_table_json = all_score_set_lists)

# @bp_clazz.route('/paper_results')
# @auth_manager.require_group
# def paper_results():
#     paper = models.Paper.query.get_or_404(flask.request.args.get('paper_id'))
#     paper.paper_questions = sorted(paper.paper_questions, key=lambda x: x.order_number)
#     score_set_list = score_manager.make_student_scoreset_list(g.clazz, paper)
#     return flask.render_template('course/clazz/paper_results.html', paper = paper, score_sets = score_set_list)

@bp_clazz.route('/paper_results')
@auth_manager.require_group
def paper_results():
    paper = models.Paper.query.get_or_404(flask.request.args.get('paper_id'))
    paper.paper_questions = sorted(paper.paper_questions, key=lambda x: x.order_number)
    clazz_paper_profile = data_manager.ClazzPaperProfile(g.clazz, paper)
    return flask.render_template('course/clazz/paper_results.html', clazz_paper_profile = clazz_paper_profile)

@bp_clazz.route('/paper_report/<int:paper_id>')
@auth_manager.require_group
def paper_report(paper_id=0):
    paper = models.Paper.query.get_or_404(paper_id)
    paper.paper_questions = sorted(paper.paper_questions, key=lambda x: x.order_number)
    clazz_report = report_types.ClazzPaperReport(g.clazz, paper)
    return flask.render_template('course/clazz/paper_report.html', clazz_report = clazz_report)
