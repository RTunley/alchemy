import flask
from flask import g
from alchemy import db, models, auth_manager

bp_course = flask.Blueprint('course', __name__)

@bp_course.url_value_preprocessor
def url_value_preprocessor(endpoint, values):
    g.course = models.Course.query.get_or_404(values.pop('course_id'))
    g.department = models.Department.query.get_or_404(g.course.department_id)
    g.school = models.School.query.get_or_404(g.department.school_id)

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
    post_data = flask.request.get_json()
    course_id = post_data['course_id']
    category_ids = post_data['category_ids']
    category_list = post_data['categories']
    course = models.Course.query.get_or_404(course_id)
    existing_ids = [category.id for category in course.assessment_categories]

    ## Delete unwanted categories ##
    for id in existing_ids:
        if id not in category_ids:
            category = models.AssessmentCategory.query.get_or_404(id)
            db.session.delete(category)
    ## Edit existing categories ##
    for i in range(len(category_list)):
        ## category_list contains (id, name, weight) for each category so every third element is a category id ##
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
    db.session.commit()
    course.order_assessment_categories()
    return flask.render_template('course/index.html')

@bp_course.route('/get_checkpoint_paper_ids/<int:checkpoint_id>', methods = ['POST'])
@auth_manager.require_group
def get_checkpoint_paper_ids(checkpoint_id):
    checkpoint = models.Checkpoint.query.get_or_404(checkpoint_id)
    checkpoint_paper_ids = []
    for paper in checkpoint.papers:
        checkpoint_paper_ids.append(paper.id)
    return flask.jsonify(paper_ids_json = checkpoint_paper_ids)

@bp_course.route('/edit_checkpoint', methods = ['POST'])
@auth_manager.require_group
def edit_checkpoint():
    post_data = flask.request.get_json()
    course_id = post_data['course_id']
    # paper_id_string = post_data['']

    # school = models.School.query.get_or_404(school_id)
    # new_snapshot_name = post_data['snapshot_name']
    # new_snapshot = models.Snapshot(name = new_snapshot_name, school_id = school_id, is_published = False)
    # db.session.add(new_snapshot)
    # all_courses = get_all_courses(school)
    # new_snapshot.create_checkpoints(all_courses)
    # for checkpoint in new_snapshot.checkpoints:
    #     checkpoint.course = models.Course.query.get_or_404(checkpoint.course_id)
    #     checkpoint.snapshot = models.Snapshot.query.get_or_404(checkpoint.snapshot_id)
    # db.session.commit() ##This will commit both the snapshot and the checkpoints created
    # return flask.render_template('school/snapshots.html')
