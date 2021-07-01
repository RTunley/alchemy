import flask
from flask import g
from alchemy import db, models

bp_course = flask.Blueprint('course', __name__)

@bp_course.url_value_preprocessor
def url_value_preprocessor(endpoint, values):
    g.course = models.Course.query.get_or_404(values.pop('course_id'))
    g.account = models.Account.query.get_or_404(g.course.account_id)

@bp_course.url_defaults
def url_defaults(endpoint, values):
    if 'course_id' not in values:
        values['course_id'] = g.course.id

@bp_course.before_request
def before_request():
    # only set title if not already set in a blueprint child
    if 'html_title' not in g:
        g.html_title = f'Course - {g.course.name}'

@bp_course.route('/')
def index():
    g.course.order_grade_levels()
    return flask.render_template('course/index.html')

@bp_course.route('/edit_grade_levels')
def edit_grade_levels():
    course_id = int(flask.request.args.get('course_id'))
    course = models.Course.query.get_or_404(course_id)
    if course.grade_levels:
        for g in course.grade_levels:
            db.session.delete(g)

    grade_level_string = str(flask.request.args.get('grade_levels'))
    grade_level_list = grade_level_string.split(',')
    for i in range(len(grade_level_list)):
        if i == 0:
            new_grade = models.GradeLevel(grade = grade_level_list[i], lower_bound = grade_level_list[i+1], upper_bound = 100, course_id = course.id)
            db.session.add(new_grade)
        elif i % 2 == 0:
            new_grade = models.GradeLevel(grade = grade_level_list[i], lower_bound = grade_level_list[i+1], upper_bound = grade_level_list[i-1], course_id = course.id)
            db.session.add(new_grade)

    db.session.commit()
    course.order_grade_levels()
    return flask.render_template('course/index.html')
