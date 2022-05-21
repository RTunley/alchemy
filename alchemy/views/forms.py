import json
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, FloatField, HiddenField, FieldList, RadioField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired, NumberRange
from alchemy import models

def build_course_tag_string(course):
    return ','.join([tag.name for tag in course.tags if len(tag.name) > 0])


class NewQuestionForm(FlaskForm):
    content = TextAreaField('Question Content', validators = [DataRequired(),])
    solution = TextAreaField('Question Solution')
    points = FloatField('Points (1, by default)', validators = [InputRequired(), NumberRange(min = 1, max = 50)], default = 1)
    hidden_mcq_choices = HiddenField(id='new_question_hidden_mcq_choices')
    hidden_correct_mcq_choice_label = HiddenField(id='new_question_hidden_correct_mcq_choice_label')
    hidden_course_tags = HiddenField(id='new_question_hidden_course_tags')
    hidden_question_tags = HiddenField(id='new_question_hidden_question_tags')
    new_tag = StringField('New Tag', id='new_question_new_tag')
    image = FileField('Add Image')
    submit = SubmitField('Add New Question', id='new_question_submit')

    def init_fields(self, course):
        self.hidden_course_tags.data = build_course_tag_string(course)

        # show 4 empty options by default
        self.hidden_mcq_choices.data = json.dumps([ {'choice_label': choice_label, 'choice_text': choice_text } for (choice_label, choice_text) in models.Question.mcq_choice_prefixes(4) ])

class EditQuestionForm(FlaskForm):
    content = TextAreaField('Question Content', validators = [DataRequired(),])
    solution = TextAreaField('Question Solution')
    points = FloatField('Points', validators = [InputRequired(), NumberRange(min = 1, max = 50)])
    hidden_mcq_choices = HiddenField(id='edit_question_hidden_mcq_choices')
    hidden_correct_mcq_choice_label = HiddenField(id='edit_question_hidden_correct_mcq_choice_label')
    hidden_course_tags = HiddenField(id='edit_question_hidden_course_tags')
    hidden_question_tags = HiddenField(id='edit_question_hidden_question_tags')
    new_tag = StringField('New Tag', id='edit_question_new_tag')
    image = FileField('Add Image')
    submit = SubmitField('Update Question', id='edit_question_submit')

    def init_fields(self, course, question):
        self.hidden_course_tags.data = build_course_tag_string(course)
        self.content.data = question.content
        self.hidden_mcq_choices.data = '[]'
        self.hidden_correct_mcq_choice_label.data = ''

        if question.is_multiple_choice():
            mcq_choices = []
            for i in range(len(question.all_solutions)):
                choice = question.all_solutions[i]
                choice_label = models.Question.mcq_choice_prefix(i)
                params = {'choice_label': choice_label, 'choice_text': choice.content}
                mcq_choices.append(params)
            self.hidden_mcq_choices.data = json.dumps(mcq_choices)
            if question.correct_solution_index is not None and question.correct_solution_index >= 0:
                self.hidden_correct_mcq_choice_label.data = mcq_choices[question.correct_solution_index]['choice_label']
        else:
            self.solution.data = question.all_solutions[0].content

        self.points.data = question.points
        tag_name_list = []
        for tag in question.tags:
            tag_name_list.append(tag.name)
        self.hidden_question_tags.data = ','.join(tag_name_list)
