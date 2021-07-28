import flask
from flask import g
import random
from alchemy import application, db, models, auth_manager, summary_profiles

bp_student = flask.Blueprint('student', __name__)

@application.template_filter('shuffle')
def filter_shuffle(seq):
    try:
        result = list(seq)
        random.shuffle(result)
        return result
    except:
        return seq

@bp_student.url_value_preprocessor
def url_value_preprocessor(endpoint, values):
    g.student = models.Student.query.get_or_404(values.pop('student_id'))

@bp_student.url_defaults
def url_defaults(endpoint, values):
    if 'student_id' not in values:
        values['student_id'] = g.student.id

@bp_student.route('/index')
@auth_manager.require_group
def index():
    return flask.render_template('account/student/index.html')

@bp_student.route('/view_course/<int:course_id>')
@auth_manager.require_group
def course_view(course_id):
    course = Course.query.filter_by(id = course_id).first()
    for clazz in g.student.clazzes:
        if clazz.course.id == course.id:
            student_clazz = clazz
    course_profile = summary_profiles.make_student_course_profile(g.student, course)
    return flask.render_template('account/student/{}/course_view.html'.format(g.student.id), profile = course_profile, clazz = clazz)
