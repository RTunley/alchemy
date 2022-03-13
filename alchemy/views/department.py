import flask
from flask import g
from alchemy import models, auth_manager

bp_department = flask.Blueprint('department', __name__)

@bp_department.url_value_preprocessor
def bp_department_endpoints(endpoint, values):
    g.department = models.Department.query.get_or_404(values.pop('department_id'))
    g.html_title = f'Department - {g.department.name}'

@bp_department.url_defaults
def bp_department_url_defaults(endpoint, values):
    if 'department_id' not in values:
        values['department_id'] = g.department.id

@bp_department.route('/')
@auth_manager.require_group
def index():
    return flask.render_template('department/index.html')
