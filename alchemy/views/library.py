import flask
from flask import g
import sqlalchemy
from alchemy import db, models, views, auth_manager
from alchemy.views import forms
import secrets
import os, base64, json, io

bp_library = flask.Blueprint('library', __name__)

@bp_library.before_request
def before_request():
    g.html_title = f'{g.course.name} - Question Library'

@bp_library.route('/')
@auth_manager.require_group
def index():
    form = forms.NewQuestionForm()
    form.init_fields(g.course)
    all_tags = db.session.query(models.Tag).order_by(models.Tag.name).all()

    return flask.render_template('course/library/index.html', new_question_form = form, all_course_tags = all_tags, tab=flask.request.args.get('tab'))

def add_image(form_field):
    form_field.data.stream.seek(0)
    image_data = base64.b64encode(form_field.data.read())
    new_image = models.Image(content = image_data)
    db.session.add(new_image)
    return new_image

def build_multiple_choice_solution(mcq_choices, correct_solution_label):
    mcq_choices_result = []
    correct_solution_index = -1
    for i in range(len(mcq_choices)):
        mcq_choice = mcq_choices[i]
        choice_label = mcq_choice['choice_label']
        choice_text = mcq_choice['choice_text']
        solution = models.Solution(content=choice_text)
        mcq_choices_result.append(solution)
        if choice_label == correct_solution_label:
            correct_solution_index = i
    return mcq_choices_result, correct_solution_index

def set_question_properties_from_form(question, form):
    # Set simple properties
    question.content = form.content.data
    question.points = form.points.data
    question.tags = build_question_tags(form.hidden_question_tags.data, question.q_course, db)

    # Set image
    if form.image.data:
        if question.image:
            db.session.delete(question.image)
        question.image = add_image(form.image)

    mcq_choices = json.loads(form.hidden_mcq_choices.data) if form.hidden_mcq_choices.data else []
    # print(mcq_choices)
    # Update solution. Simplify by just replacing properties instead of updating them.
    new_mcq_choices, correct_solution_index = build_multiple_choice_solution(
            mcq_choices,
            form.hidden_correct_mcq_choice_label.data)
    # print(new_mcq_choices)
    if not new_mcq_choices:
        # this is an open answer question rather than multiple choice
        new_mcq_choices = [models.Solution(content=form.solution.data)]
    if question.all_solutions:
        for choice in question.all_solutions:
            db.session.delete(choice)
    question.all_solutions = new_mcq_choices
    question.correct_solution_index = correct_solution_index

@bp_library.route('/add_question', methods=['POST'])
@auth_manager.require_group
def add_question():
    new_question_form = forms.NewQuestionForm()
    if new_question_form.validate_on_submit():
        question = models.Question.create(q_course = g.course)
        set_question_properties_from_form(question, new_question_form)
        db.session.add(question)
        db.session.commit()
        flask.flash('New question has been added to the library!', 'success')
        return flask.redirect(flask.url_for('course.library.index', course_id = g.course.id))
    return '<html><body>Invalid form data!</body></html>'

@bp_library.route('/edit_question_submit', methods=['POST'])
@auth_manager.require_group
def edit_question_submit():
    edit_question_form = forms.EditQuestionForm()
    if edit_question_form.validate_on_submit():
        question_id = int(flask.request.form.get('question_id'))
        question = models.Question.query.get_or_404(question_id)
        set_question_properties_from_form(question, edit_question_form)
        db.session.commit()
        tab = 'mcq' if question.is_multiple_choice() else 'open_answer'
        return flask.redirect(flask.url_for('course.library.index', course_id = question.q_course.id, tab=tab))
    return '<html><body>Invalid form data!</body></html>'

@bp_library.route('/edit_question_render_form')
@auth_manager.require_group
def edit_question_render_form():
    question_id = int(flask.request.args.get('question_id'))
    question = models.Question.query.get_or_404(question_id)
    edit_question_form = forms.EditQuestionForm()
    edit_question_form.init_fields(question.q_course, question)

    template_string = '''
    {% import 'course/library/question_form_macro.html' as question_form %}
    '''
    template_string += '''
    {{ question_form.render_question_form(edit_question_form, 'edit_question_', '/course/%d/library/edit_question_submit', %d) }}
    ''' % (g.course.id, question.id)

    return flask.jsonify(edit_question_html = flask.render_template_string(template_string, edit_question_form = edit_question_form))

@bp_library.route('/delete_question')
@auth_manager.require_group
def delete_question():
    question_id = int(flask.request.args.get('question_id'))
    question = models.Question.query.get_or_404(question_id)
    if question.papers:
        flask.flash('Questions that are contained in Assessments cannot be deleted', 'danger')
    else:
        db.session.delete(question)
        db.session.commit()
    return flask.redirect(flask.url_for('course.library.index', course_id = g.course.id))

def build_question_tags(tag_string, course, db):
    tag_list = tag_string.split(',')
    tag_obj_list = []
    for course_tag in course.tags:
        for tag in tag_list:
            if tag == course_tag.name:
                tag_obj_list.append(course_tag)
                tag_list.remove(tag)
    for tag in tag_list:
        if tag != '':
            new_tag = models.Tag(name = tag, tag_course = course)
            tag_obj_list.append(new_tag)
            db.session.add(new_tag)
    return tag_obj_list
