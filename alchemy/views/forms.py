import json
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, FloatField, HiddenField, FieldList, RadioField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired, NumberRange
from alchemy import models

def build_course_tag_string(course):
    return ','.join([tag.name for tag in course.tags if len(tag.name) > 0])


class NewQuestionForm(FlaskForm):
    content = TextAreaField('Question Content')
    solution = TextAreaField('Question Solution')
    points = FloatField('Points',validators = [InputRequired(), NumberRange(min = 1, max = 50)])
    hidden_solution_choices = HiddenField(id='new_question_hidden_solution_choices')
    hidden_solution_correct_label = HiddenField(id='new_question_hidden_solution_correct_label')
    hidden_course_tags = HiddenField(id='new_question_hidden_course_tags')
    hidden_question_tags = HiddenField(id='new_question_hidden_question_tags')
    new_tag = StringField('New Tag', id='new_question_new_tag')
    image = FileField('Add Image')
    submit = SubmitField('Add New Question', id='new_question_submit')

    def init_fields(self, course):
        self.hidden_course_tags.data = build_course_tag_string(course)

        # show 4 empty options by default
        self.hidden_solution_choices.data = json.dumps([ {'choice_label': choice_label, 'choice_text': choice_text } for (choice_label, choice_text) in models.Question.solution_prefixes(4) ])

class EditQuestionForm(FlaskForm):
    # TODO support editing of multiple choice questions
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

        self.solution_choices = []
        if question.solution_choices:
            for i in range(len(question.solution_choices)):
                choice_label = string.ascii_uppercase[i]
                choice_text = question.solution_choices[i].content
                self.solution_choices.append((choice_label, choice_text))
        else:
            self.solution.data = question.solution.content

        self.points.data = question.points
        tag_name_list = []
        for tag in question.tags:
            tag_name_list.append(tag.name)
        self.hidden_question_tags.data = ','.join(tag_name_list)
