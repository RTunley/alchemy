import sqlalchemy
import flask
from flask import g
import urllib
from alchemy import db, models, auth_manager

bp_paper = flask.Blueprint('paper', __name__)

@bp_paper.url_value_preprocessor
def url_value_preprocessor(endpoint, values):
    paper_id = int(values.pop('paper_id', 0))
    if paper_id ==  0:
        g.paper = None  # We are creating a new paper
    else:
        g.paper = models.Paper.query.get_or_404(paper_id)

@bp_paper.url_defaults
def url_defaults(endpoint, values):
    if 'paper_id' not in values:
        values['paper_id'] = g.paper.id if 'paper' in g else 0

@bp_paper.before_request
def before_request():
    if g.paper is None:
        g.html_title = f'{g.course.name} - New assessment'
    else:
        g.html_title = f'{g.course.name} - {g.paper.title}'

@bp_paper.route('/', methods = ['GET', 'POST'])
@auth_manager.require_group
def index():
    if g.paper is None:
        # Create a new paper
        paper_title = flask.request.form['paper_create_modal_new_title']
        paper = models.Paper(title = paper_title, course_id = g.course.id)
        db.session.add(paper)
        db.session.commit()
        g.paper = paper
        return render_edit_paper(paper)
    else:
        # Show the paper home page
        return flask.render_template('course/paper/index.html')

@bp_paper.route('/edit_title', methods = ['POST'])
@auth_manager.require_group
def edit_title():
    new_title = flask.request.form['paper_edit_modal_new_title']
    g.paper.title = new_title
    db.session.commit()
    return render_edit_paper(g.paper)

@bp_paper.route('/remove')
@auth_manager.require_group
def remove():
    for paper_question in g.paper.paper_questions:
        db.session.delete(paper_question)
    db.session.delete(g.paper)
    db.session.commit()
    return flask.redirect(flask.url_for('course.index'))

@bp_paper.route('/printable', methods = ['GET'])
@auth_manager.require_group
def printable():
    return flask.render_template('course/paper/printable.html')
    # #css = [''] #any css files you want to include
    # pdf = pdfkit.from_string(rendered, False)
    # response = make_response(pdf)
    # response.headers['Content-Type'] = 'application/pdf'
    # response.headers['Content-Disposition'] = 'inline; filename = paper.pdf'
    # return response

@bp_paper.route('/solutions_printable')
@auth_manager.require_group
def solutions_printable():
    return flask.render_template('course/paper/solutions_printable.html')
    #css = [''] #any css files you want to include
    # pdf = pdfkit.from_string(rendered, False)
    # response = make_response(pdf)
    # response.headers['Content-Type'] = 'application/pdf'
    # response.headers['Content-Disposition'] = 'inline; filename = paper.pdf'
    # return response

def questions_filtered_by_tag_filter(tag_filter):
    # Find the questions that do not have any of the tags in the tag_filter
    filtered_questions_tags = db.session.query(models.questions_tags).filter(models.questions_tags.c.tag_id.notin_(tag_filter)).all()
    filtered_question_ids = set()
    for question_tag in filtered_questions_tags:
        filtered_question_ids.add(question_tag.questions_id)

    # Get a list of questions based on the filtered question ids.
    # Probably should be using a db join instead.
    return models.Question.query.filter(models.Question.id.in_(filtered_question_ids)).all()

@bp_paper.route('/filter_questions_by_tag')
@auth_manager.require_group
def filter_questions_by_tag():
    tag_filter = flask.request.args.get('tag_filter')
    filtered_questions = questions_filtered_by_tag_filter(tag_filter.split(','))

    if g.paper is None:
        # Return all matching questions in the entire course
        return flask.jsonify(question_accordion_html = render_question_accordion_html(filtered_questions))
    else:
        # Return all matching questions in this paper
        available_questions = questions_available_for_paper(g.paper, filtered_questions)
        return flask.jsonify(question_accordion_html = render_question_accordion_html(available_questions))

@bp_paper.route('/filter_questions_by_text')
@auth_manager.require_group
def filter_questions_by_text():
    search_text = flask.request.args.get('search_text').strip()
    if len(search_text) > 0:
        # Find question content or solution values for this course that contain this search text
        search_query = '%{}%'.format(search_text)
        filtered_questions = models.Question.query.filter(
                models.Question.course_id == g.course.id,
                sqlalchemy.or_(
                    models.Question.content.like(search_query),
                    # models.Question.solution.content.like(search_query)
                )).all()
    else:
        # Return all questions for this course
        filtered_questions = models.Question.query.filter_by(course_id = g.course.id).all()

    if g.paper is None:
        # Return all matching questions in the entire course
        return flask.jsonify(question_accordion_html = render_question_accordion_html(filtered_questions))
    else:
        # Return all matching questions in this paper
        available_questions = questions_available_for_paper(g.paper, filtered_questions)
        return flask.jsonify(question_accordion_html = render_question_accordion_html(available_questions))

def questions_available_for_paper(paper, from_question_list):
    available_questions = []
    paper_current_questions = paper.question_objects()
    for question in from_question_list:
        # Inject a temporary variable that can be checked when loading the html. A bit hacky and not recommended in the general case.
        question.__question_added_to_paper = (question in paper_current_questions)
        available_questions.append(question)
    return available_questions

def render_question_accordion_html(questions):
    paper_id = g.paper.id if g.paper else 0
    return flask.render_template_string(
        '''
        {% import 'course/question_tabs_macro.html' as question_tabs %}
        {{ question_tabs.render_question_tabs(course_id, paper_id, questions) }}
        ''', course_id = g.course.id, paper_id = paper_id, questions = questions)

@bp_paper.route('/edit')
@auth_manager.require_group
def edit():
    return render_edit_paper(g.paper)

def render_edit_paper(paper):
    course = paper.course
    paper.paper_questions = sorted(paper.paper_questions, key = lambda x: x.order_number)

    course = models.Course.query.get(paper.course_id)

    available_questions = questions_available_for_paper(paper, course.questions)

    all_tags = db.session.query(models.Tag).order_by(models.Tag.name).all()

    return flask.render_template('course/paper/edit.html', available_questions = available_questions, all_course_tags = all_tags, show_editing_controls = True)

def paper_editing_json_response(paper, tag_filter = None):
    course = models.Course.query.get(paper.course_id)

    if tag_filter:
        filtered_questions = questions_filtered_by_tag_filter(tag_filter)
        available_questions = questions_available_for_paper(paper, filtered_questions)
    else:
        available_questions = questions_available_for_paper(paper, course.questions)

    # return the updated list of available questions and paper questions
    return flask.jsonify(
        available_questions_html = render_question_accordion_html(available_questions), paper_questions_html = flask.render_template('course/paper/questions_list.html',
            show_editing_controls = True), stats_sidebar_html = flask.render_template('course/paper/profile.html'))

@bp_paper.route('/reorder_questions')
@auth_manager.require_group
def reorder_questions():
    question_id_list = urllib.parse.parse_qsl(flask.request.args.get('sorted_question_ids'))
    if len(question_id_list) > 0:
        new_question_order = [int(question_id) for dummy, question_id in question_id_list]
        if g.paper.reorder_questions(new_question_order):
            db.session.commit()
    return paper_editing_json_response(g.paper)

@bp_paper.route('/add_question')
@auth_manager.require_group
def add_question():
    question_id = int(flask.request.args.get('question_id'))
    question = models.Question.query.get_or_404(question_id)
    tag_filter = flask.request.args.get('tag_filter')

    paper_question = g.paper.new_question(question)
    db.session.add(paper_question)
    db.session.commit()
    g.paper.build_profile()
    return paper_editing_json_response(g.paper, tag_filter)

@bp_paper.route('/remove_question')
@auth_manager.require_group
def remove_question():
    question_id = int(flask.request.args.get('question_id'))
    question = models.Question.query.get_or_404(question_id)
    tag_filter = flask.request.args.get('tag_filter')

    paper_question = g.paper.remove_question(question.id)
    if paper_question:
        db.session.delete(paper_question)
    else:
        return flask.Response(status = 404)
    db.session.commit()
    g.paper.build_profile()
    return paper_editing_json_response(g.paper, tag_filter)

@bp_paper.route('/duplicate')
@auth_manager.require_group
def duplicate():
    old_paper = g.paper
    new_paper = models.Paper(title = old_paper.title + ' (duplicate)', course_id = g.course.id)
    db.session.add(new_paper)
    db.session.commit()
    for paper_question in old_paper.paper_questions:
        question = paper_question.question
        paper_question = new_paper.new_question(question)
        db.session.add(paper_question)

    db.session.commit()
    return flask.redirect(flask.url_for('course.index'))
