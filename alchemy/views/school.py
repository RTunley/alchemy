import flask
from flask import g
from alchemy import models, auth_manager

bp_school = flask.Blueprint('school', __name__)

@bp_school.url_value_preprocessor
def bp_department_endpoints(endpoint, values):
    g.school = models.School.query.get_or_404(values.pop('school_id'))
    g.html_title = f'School - {g.school.name}'

@bp_school.url_defaults
def bp_school_url_defaults(endpoint, values):
    if 'school_id' not in values:
        values['school_id'] = g.school.id

@bp_school.route('/')
@auth_manager.require_group
def index():
    return flask.render_template('school/index.html')

@bp_school.route('/departments')
@auth_manager.require_group
def departments():
    return flask.render_template('school/departments.html')

@bp_school.route('/snapshots')
@auth_manager.require_group
def snapshots():
    return flask.render_template('school/snapshots.html')

@bp_school.route('/new_snapshot')
@auth_manager.require_group
def new_snapshot(name):
    courses = get_snapshot_courses(g.school)
    new_snapshot = models.Snapshot(name, courses)
    return new_snapshot


## Default for now is all courses, but in future need some way to group courses so that snapshots can be taken for some courses but not others ##
def get_snapshot_courses(school):
    snapshot_courses = []
    for department in school.departments:
        for course in department.courses:
            snapshot_courses.append(course)
    return snapshot_courses
