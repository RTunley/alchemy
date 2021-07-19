import flask
from flask import g
from alchemy import db, models, auth_manager, summary_profiles

bp_cohort = flask.Blueprint('cohort', __name__)

@bp_cohort.before_request
def before_request():
    g.html_title = f'{{g.course.name}} - Current Cohort'

@bp_cohort.route('/cohort/index')
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
