import flask
from flask import g
import sqlalchemy
from sam import db, models
from sam.views import forms

bp_library = flask.Blueprint('library', __name__)

@bp_library.before_request
def before_request():
    g.html_title = f'{g.course.name} - Question Library'

@bp_library.route('/')
def index():
    form = forms.NewQuestionForm()
    form.init_fields(g.course)
    all_tags = db.session.query(models.Tag).order_by(models.Tag.name).all()
    return flask.render_template('course/library/index.html', new_question_form = form, all_course_tags = all_tags)

@bp_library.route('/add_question', methods=['POST'])
def add_question():
    new_question_form = forms.NewQuestionForm(flask.request.form)
    if new_question_form.validate_on_submit():
        question = models.Question(
            content = new_question_form.content.data,
            solution = new_question_form.solution.data,
            points = new_question_form.points.data,
            q_course = g.course,
            tags = build_question_tags(new_question_form.hidden_question_tags.data, g.course, db))
        db.session.add(question)
        db.session.commit()
        flask.flash('New question has been added to the library!', 'success')
        return flask.redirect(flask.url_for('course.library.index', course_id = g.course.id))
    return '<html><body>Invalid form data!</body></html>'

@bp_library.route('/edit_question_submit', methods=['POST'])
def edit_question_submit():
    edit_question_form = forms.EditQuestionForm(flask.request.form)
    if edit_question_form.validate_on_submit():
        question_id = int(flask.request.form.get('question_id'))
        question = models.Question.query.get_or_404(question_id)
        question.content = edit_question_form.content.data
        question.solution = edit_question_form.solution.data
        question.points = edit_question_form.points.data
        question.tags = build_question_tags(edit_question_form.hidden_question_tags.data, question.q_course, db)
        db.session.commit()
        return flask.redirect(flask.url_for('course.library.index', course_id = question.q_course.id))
    return '<html><body>Invalid form data!</body></html>'

@bp_library.route('/edit_question_render_form')
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
        for t in tag_list:
            if t == course_tag.name:
                tag_obj_list.append(course_tag)
                tag_list.remove(t)
    for t in tag_list:
        new_tag = models.Tag(name = t, tag_course = course)
        tag_obj_list.append(new_tag)
        db.session.add(new_tag)
    return tag_obj_list
