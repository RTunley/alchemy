import flask
from flask import g
from werkzeug.utils import secure_filename
from alchemy import db, models, auth_manager, summary_profiles, file_input, file_output
import os

bp_cohort = flask.Blueprint('cohort', __name__)

def get_cohort_size(course):
    num_students = 0
    for clazz in course.clazzes:
        num_students+=len(clazz.students)
    return num_students

@bp_cohort.before_request
def before_request():
    g.html_title = f'{{{ g.course.name }}} - Current Cohort'

@bp_cohort.route('/index')
@auth_manager.require_group
def index():
    return flask.render_template('course/cohort/index.html', num_students = get_cohort_size(g.course), profile_tuples = get_all_student_profiles(g.course))

def get_all_student_profiles(course):
    clazz_profile_tuples = []
    for clazz in course.clazzes:
        student_course_profile_list = []
        for student in clazz.students:
            new_course_profile = summary_profiles.make_student_course_profile(student, course)
            student_course_profile_list.append(new_course_profile)

        clazz_profile_tuples.append((clazz,student_course_profile_list))
    return clazz_profile_tuples

@bp_cohort.route('/add_student', methods=['POST'])
@auth_manager.require_group
def add_student():
    new_given_name = flask.request.form['given_name']
    new_family_name = flask.request.form['family_name']
    clazz_id = flask.request.form['clazz_id']
    student_id = flask.request.form['student_id']
    email = flask.request.form['student_email']
    clazz = models.Clazz.query.get_or_404(clazz_id)
    new_aws_user = models.AwsUser(given_name = new_given_name, family_name= new_family_name, username = new_given_name+new_family_name+str(student_id), group = 'student')## TODO create student group?
    new_student = models.Student(clazzes = [clazz], aws_user = new_aws_user, id = student_id) ## TODO might need to append clazz to student.clazzes rather than create it
    db.session.add(new_aws_user)
    db.session.add(new_student)
    db.session.commit()
    return flask.redirect(flask.url_for('course.cohort.index', num_students = get_cohort_size(g.course), profile_tuples = get_all_student_profiles(g.course)))

@bp_cohort.route('/upload_excel', methods=['POST'])
@auth_manager.require_group
def upload_class_data():
    if flask.request.method == 'POST':
        if 'file' not in flask.request.files:
            flask.flash('No File Found.')

        file = flask.request.files['file']

        if file.filename == '':
            flask.flash('No File Selected For Upload')

        if file_input.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            extension = file_input.get_extension(filename)
            temp_dir = file_input.get_temp_directory()
            file.save(os.path.join(temp_dir.name, filename))
            flask.flash('File successfully uploaded')
            if extension == '.xlsx':
                file_path = os.path.join(temp_dir.name, filename)
                csv_filename = file_input.convert_to_csv(file_path)
                csv_file_path = os.path.join(temp_dir.name, csv_filename)
            else:
                csv_file_path = os.path.join(temp_dir.name, filename)

            new_clazz_code = flask.request.form['clazz_code']
            new_clazz = models.Clazz(course = g.course, code = new_clazz_code)
            db.session.add(new_clazz)
            file_input.add_new_clazz(db, csv_file_path, new_clazz)
            file_input.delete_temp_directory(temp_dir)

        else:
            flask.flash('Allowed File Type Is .xlxs or .csv')

    return flask.redirect(flask.url_for('course.cohort.index', num_students = get_cohort_size(g.course), profile_tuples = get_all_student_profiles(g.course)))

@bp_cohort.route('/download_excel', methods = ['GET', 'POST'])
@auth_manager.require_group
def download_class_template():
    temp_dir = file_output.get_temp_directory()
    template_filename = file_output.make_class_template(temp_dir)
    try:
        return flask.send_from_directory(temp_dir.name, template_filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)
