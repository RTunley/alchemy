import flask
from flask import g
from werkzeug.utils import secure_filename
from alchemy import db, models, auth_manager, score_manager, summary_profiles, file_input, file_output
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
    for p in g.course.papers:
        p.check_clazz_scores(g.clazz)
    return flask.render_template('course/clazz/index.html', profiles = get_student_profiles(g.clazz))

@bp_clazz.route('/upload_excel', methods=['POST'])
@auth_manager.require_group
def upload_excel():
    if flask.request.method == 'POST':
        if 'file' not in flask.request.files:
            flask.flash('No File Found.')
            return flask.redirect(flask.url_for('clazz.index'))

        file = flask.request.files['file']

        if file.filename == '':
            flask.flash('No File Selected For Upload')
            return flask.redirect(flask.url_for('clazz.index'))

        if file and file_input.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = file_input.get_upload_directory(g.clazz)
            file.save(os.path.join(upload_dir, filename))
            flask.flash('File successfully uploaded')
            file_input.delete_current_clazzlist(g.clazz, db)
            excel_file_path = os.path.join(upload_dir, filename)
            new_user_list = file_input.parse_clazz_excel(excel_file_path, g.clazz)
            file_input.write_users_to_db(db, new_user_list)
            return flask.redirect(flask.url_for('clazz.index'))

        else:
            flask.flash('Allowed File Type Is .xlxs or .ods')
            return flask.redirect(flask.url_for('clazz.index'))

@bp_clazz.route('/download_excel', methods = ['GET', 'POST'])
@auth_manager.require_group
def download_excel():
    # TODO should not save files into the code repo.
    cwd = os.getcwd()
    alchemy = os.path.join(cwd, 'alchemy')
    downloads = os.path.join(alchemy, 'downloads')
    filename = 'clazz_template.xlsx'

    try:
        return flask.send_from_directory(downloads, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@bp_clazz.route('/add_student', methods=['POST'])
@auth_manager.require_group
def add_student():
    new_given_name = flask.request.form['given_name']
    new_family_name = flask.request.form['family_name']
    student_access = models.AccessLevel.query.get(3)
    new_asw_user = models.AwsUser(given_name = new_given_name, family_name= new_family_name, username = new_given_name+'.'+new_family_name, group = 'student')## TODO create student group?
    new_student = models.Student(clazzes = [g.clazz], aws_user = new_aws_user)
    db.session.add(new_student)
    db.session.commit()
    return flask.render_template('course/clazz/index.html', profiles = get_student_profiles(g.clazz))

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

@bp_clazz.route('/download_results_excel')
@auth_manager.require_group
def download_results_excel():
    paper = models.Paper.query.get_or_404(flask.request.args.get('paper_id'))
    paper.paper_questions = sorted(paper.paper_questions, key=lambda x: x.order_number)
    cwd = os.getcwd()
    alchemy = os.path.join(cwd, 'alchemy')
    downloads = os.path.join(alchemy, 'downloads')
    filename = file_output.output_results_excel(paper, g.clazz, downloads)
    try:
        return flask.send_from_directory(downloads, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@bp_clazz.route('/upload_results_excel', methods=['POST'])
@auth_manager.require_group
def upload_results_excel():
    paper = models.Paper.query.get_or_404(flask.request.args.get('paper_id'))
    if flask.request.method == 'POST':
        if 'file' not in flask.request.files:
            flask.flash('No File Found.')
            return flask.redirect(flask.url_for('clazz.paper_results', paper_id = paper.id))

        file = flask.request.files['file']

        if file.filename == '':
            flask.flash('No File Selected For Upload')
            return flask.redirect(flask.url_for('clazz.paper_results', paper_id = paper.id))

        if file and file_input.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = file_input.get_upload_directory(g.clazz)
            file.save(os.path.join(upload_dir, filename))
            flask.flash('File successfully uploaded')
            excel_file_path = os.path.join(upload_dir, filename)
            scores_list = file_input.parse_results_excel(excel_file_path, g.clazz, paper)
            file_input.write_scores_to_db(db, scores_list)
            return flask.redirect(flask.url_for('clazz.paper_results', paper_id = paper.id))

        else:
            flask.flash('Allowed File Type Is .xlxs or .ods')
            return flask.redirect(flask.url_for('clazz.paper_results', paper_id = paper.id))

@bp_clazz.route('/paper_results')
@auth_manager.require_group
def paper_results():
    paper = models.Paper.query.get_or_404(flask.request.args.get('paper_id'))
    paper.paper_questions = sorted(paper.paper_questions, key=lambda x: x.order_number)
    score_set_list = score_manager.make_student_scoreset_list(g.clazz, paper)
    return flask.render_template('course/clazz/paper_results.html', paper = paper, score_sets = score_set_list)

@bp_clazz.route('/paper_report')
@auth_manager.require_group
def paper_report():
    paper = models.Paper.query.get_or_404(flask.request.args.get('paper_id'))
    paper.paper_questions = sorted(paper.paper_questions, key=lambda x: x.order_number)
    course = paper.course
    account = course.account
    student_scoreset_list = score_manager.make_student_scoreset_list(g.clazz, paper)
    tag_totalset_list = score_manager.make_tag_totalset_list(g.clazz, paper)
    question_scoreset_list = score_manager.make_question_scoreset_list(g.clazz, paper)
    clazz_report = score_manager.ClassReport(paper, student_scoreset_list, tag_totalset_list, question_scoreset_list)
    return flask.render_template('course/clazz/clazz_paper.html', paper = paper, clazz_report = clazz_report)

@bp_clazz.route('/student_paper_report')
@auth_manager.require_group
def student_paper_report():
    student = models.Student.query.get_or_404(flask.request.args.get('student_id'))
    paper = models.Paper.query.get_or_404(flask.request.args.get('paper_id'))
    paper.paper_questions = sorted(paper.paper_questions, key=lambda x: x.order_number)
    student_scoreset_list = score_manager.make_student_scoreset_list(g.clazz, paper)
    tag_totalset_list = score_manager.make_tag_totalset_list(g.clazz, paper)
    question_scoreset_list = score_manager.make_question_scoreset_list(g.clazz, paper)
    student_report = score_manager.StudentReport(student, paper, student_scoreset_list, tag_totalset_list, question_scoreset_list)
    return flask.render_template('course/clazz/student_paper.html', paper = paper, student_report = student_report)

def get_student_profiles(clazz):
    student_course_profile_list = []
    for s in clazz.students:
        new_course_profile = summary_profiles.make_student_course_profile(s, clazz.course)
        student_course_profile_list.append(new_course_profile)
    return student_course_profile_list
