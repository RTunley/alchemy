import flask
from flask import g
from alchemy import db, models, auth_manager, summary_profiles

bp_cohort = flask.Blueprint('cohort', __name__)

@bp_cohort.before_request
def before_request():
    g.html_title = f'{{{ g.course.name }}} - Current Cohort'

@bp_cohort.route('/cohort/index')
@auth_manager.require_group
def index():
    return flask.render_template('course/cohort/index.html', profile_tuples = get_all_student_profiles(g.course))

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
    new_aws_user = models.AwsUser(given_name = new_given_name, family_name= new_family_name, username = new_given_name+'.'+new_family_name, group = 'student')## TODO create student group?
    new_student = models.Student(clazzes = [clazz], aws_user = new_aws_user, id = student_id) ## TODO might need to append clazz to student.clazzes rather than create it
    db.session.add(new_aws_user)
    db.session.add(new_student)
    db.session.commit()
    return flask.render_template('course/cohort/index.html', profile_tuples = get_all_student_profiles(g.course))
