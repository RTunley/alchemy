import flask
from flask import g
from alchemy import db, models, auth_manager, summary_profiles, file_input, file_output

bp_student = flask.Blueprint('student', __name__)

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
    return flask.render_template('/student/index.html')
