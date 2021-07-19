import flask
from flask import g
from alchemy import db, models, auth_manager

bp_cohort = flask.Blueprint('cohort', __name__)

@bp_cohort.before_request
def before_request():
    g.html_title = f'{{g.course.name}} - Current Cohort'

@bp_cohort.route('/cohort/index')
def index():
    return flask.render_template('course/cohort/index.html')
