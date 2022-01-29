import flask
from flask import g
from alchemy import db, models, auth_manager

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
@auth_manager.require_group
def index():
    g.course.order_grade_levels()
    return flask.render_template('course/index.html')

@bp_course.route('/edit_grade_levels', methods=['POST'])
@auth_manager.require_group
def edit_grade_levels():
    post_data = flask.request.get_json()
    course_id = post_data['course_id']
    grade_level_list = post_data['grade_levels']
    course = models.Course.query.get_or_404(course_id)
    if course.grade_levels:
        for g in course.grade_levels:
            db.session.delete(g)

    for i in range(len(grade_level_list)):
        if i == 0:
            upper_bound = 100
        elif i % 2 == 0:
            upper_bound = grade_level_list[i-1]
        else:
            continue
        new_grade = models.GradeLevel(grade = grade_level_list[i], lower_bound = grade_level_list[i+1], upper_bound = upper_bound, course_id = course.id)
        db.session.add(new_grade)

    db.session.commit()
    course.order_grade_levels()
    return flask.render_template('course/index.html')

@bp_course.route('/edit_categories', methods=['POST'])
@auth_manager.require_group
def edit_categories():
    print("Made it to edit_categories!!")
    post_data = flask.request.get_json()
    course_id = post_data['course_id']
    category_ids = post_data['category_ids']
    category_list = post_data['categories']
    course = models.Course.query.get_or_404(course_id)
    print("Categories:", category_list)
    existing_ids = [category.id for category in course.assessment_categories]

    ## Delete unwanted categories ##
    for id in existing_ids:
        if id not in category_ids:
            category = models.AssessmentCategory.query.get_or_404(id)
            db.session.delete(category)
    ## Edit existing categories ##
    for i in range(len(category_list)):
        if i % 3 == 0:
            category_id = int(category_list[i])
            if category_id == 0:
                new_category = models.AssessmentCategory(name = category_list[i+1], weight = float(category_list[i+2]), course_id = course_id)
                db.session.add(new_category)
            else:
                for category in course.assessment_categories:
                    if category.id == category_id:
                        category.name = category_list[i+1]
                        category.weight = float(category_list[i+2])
        else:
            pass
    db.session.commit()
    course.order_assessment_categories()
    return flask.render_template('course/index.html')
