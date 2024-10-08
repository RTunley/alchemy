import flask
from flask import g
from alchemy import models, auth_manager, db

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

@bp_school.route('/publish_snapshot/<int:snapshot_id>')
@auth_manager.require_group
def publish_snapshot(snapshot_id):
    snapshot = models.Snapshot.query.get_or_404(snapshot_id)
    snapshot.is_published = True
    db.session.commit()
    return flask.render_template('school/snapshots.html')

@bp_school.route('/new_snapshot', methods = ['POST'])
@auth_manager.require_group
def new_snapshot():
    post_data = flask.request.get_json()
    school_id = post_data['school_id']
    school = models.School.query.get_or_404(school_id)
    new_snapshot_name = post_data['snapshot_name']
    new_snapshot = models.Snapshot(name = new_snapshot_name, school_id = school_id, is_published = False)
    db.session.add(new_snapshot)

    # Commit the snapshot now, because the code below searches for snapshots from the db
    db.session.commit()

    all_courses = get_all_courses(school)
    print(all_courses)
    new_snapshot.create_checkpoints(all_courses)
    for checkpoint in new_snapshot.checkpoints:
        checkpoint.course = models.Course.query.get_or_404(checkpoint.course_id)
        checkpoint.snapshot = models.Snapshot.query.get_or_404(checkpoint.snapshot_id)
    db.session.commit() ##This will commit the checkpoints created
    print("The Snapshot is ready?")
    print(new_snapshot.is_ready())
    return flask.render_template('school/snapshots.html')

## Default for now is all courses, but in future need some way to group courses so that snapshots can be taken for some courses but not others ##
def get_all_courses(school):
    courses = []
    for department in school.departments:
        for course in department.courses:
            courses.append(course)
    return courses
