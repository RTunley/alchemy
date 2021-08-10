from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, FloatField, HiddenField, FieldList
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired, NumberRange

def build_course_tag_string(course):
    return ','.join([tag.name for tag in course.tags if len(tag.name) > 0])

class NewQuestionForm(FlaskForm):
    content = TextAreaField('Question Content', validators = [DataRequired(),])
    solution = TextAreaField('Question Solution', validators = [DataRequired(),])
    points = FloatField('Points',validators = [InputRequired(), NumberRange(min = 1, max = 50])
    hidden_course_tags = HiddenField(id='new_question_hidden_course_tags')
    hidden_question_tags = HiddenField(id='new_question_hidden_question_tags')
    new_tag = StringField('New Tag', id='new_question_new_tag')
    image = FileField('Add Image')
    submit = SubmitField('Add New Question', id='new_question_submit')

    def init_fields(self, course):
        self.hidden_course_tags.data = build_course_tag_string(course)

class EditQuestionForm(FlaskForm):
    content = TextAreaField('Question Content', validators = [DataRequired(),])
    solution = TextAreaField('Question Solution', validators = [DataRequired(),])
    points = FloatField('Points',validators = [InputRequired(),])
    hidden_course_tags = HiddenField(id='edit_question_hidden_course_tags')
    hidden_question_tags = HiddenField(id='edit_question_hidden_question_tags')
    new_tag = StringField('New Tag', id='edit_question_new_tag')
    image = FileField('Add Image')
    submit = SubmitField('Update Question', id='edit_question_submit')

    def init_fields(self, course, question):
        self.hidden_course_tags.data = build_course_tag_string(course)
        self.content.data = question.content
        self.solution.data = question.solution
        self.points.data = question.points
        tag_name_list = []
        for tag in question.tags:
            tag_name_list.append(tag.name)
        self.hidden_question_tags.data = ','.join(tag_name_list)
