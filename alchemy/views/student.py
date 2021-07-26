import flask
from flask import g
import random
from alchemy import application, db, models, auth_manager

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
