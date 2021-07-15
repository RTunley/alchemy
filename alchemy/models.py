import sqlalchemy
from alchemy import db
import alchemy.views.profile as paper_profile
import base64
import io

## Database Models ##

class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    courses = db.relationship('Course', backref='account')

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    questions = db.relationship('Question', backref = 'q_course')
    tags = db.relationship('Tag', backref='tag_course')
    clazzes = db.relationship('Clazz', backref='course')
    papers = db.relationship('Paper', backref='course')
    grade_levels = db.relationship('GradeLevel', backref='grade_levels')

    def order_grade_levels(self):
        self.grade_levels.sort(key=lambda x: x.lower_bound,  reverse = True)

clazzes_students = db.Table('clazzes_students',
    db.Column('clazz_id', db.Integer, db.ForeignKey('clazz.id')),
    db.Column('student_id', db.Integer, db.ForeignKey('student.aws_id'))
    )

class GradeLevel(db.Model):
    __tablename__ = 'grade_level'
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String())
    lower_bound = db.Column(db.Integer)
    upper_bound = db.Column(db.Integer)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

class Clazz(db.Model):
    __tablename__ = 'clazz'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    students = db.relationship('Student', secondary=clazzes_students, back_populates='clazzes')

# TODO rename this table to 'Student' that just has attributes:
#   clazz, scores
# and also a ref to the 'AwsUser' for the student.

class Student(db.Model):
    __tablename__ = 'student'
    clazzes = db.relationship('Clazz', secondary=clazzes_students, back_populates='students')
    scores = db.relationship('Score', backref='student')
    aws_id = db.Column(db.Integer, db.ForeignKey('aws_user.id'))
    aws_user = db.relationship('AwsUser', backref='student')

    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint(aws_id),
    )

class AwsUser(db.Model):
    __tablename__ = 'aws_user'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), unique=True, nullable=False) # UUID string
    username = db.Column(db.String(64), nullable=False)
    group = db.Column(db.String(64), nullable=False) # Would we support multiple groups per user?
    # Other attributes
    given_name = db.Column(db.String(32))
    family_name = db.Column(db.String(32))
    email = db.Column(db.String(64))


questions_tags = db.Table('questions_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('questions_id', db.Integer, db.ForeignKey('question.id'))
    )

class PaperQuestion(db.Model):
    __tablename__ = 'paper_question'
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    order_number = db.Column(db.Integer)
    question = db.relationship('Question', back_populates='papers')
    paper = db.relationship('Paper', back_populates='paper_questions')

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(), nullable=False)
    solution = db.Column(db.String(), nullable=False)
    points = db.Column(db.Float(), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    tags = db.relationship('Tag', secondary=questions_tags, back_populates='questions')
    papers = db.relationship('PaperQuestion', back_populates='question')
    scores = db.relationship('Score', backref='question')
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    image = db.relationship("Image", back_populates='questions')

    def decode_image(self):
            img_str = self.q_image.content.decode('ascii')
            return img_str

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.LargeBinary, nullable=False)
    questions = db.relationship('Question', backref='q_image')

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    questions = db.relationship('Question', secondary=questions_tags, back_populates='tags')

class Paper(db.Model):
    __tablename__ = 'paper'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    scores = db.relationship('Score', backref='paper')
    paper_questions = db.relationship('PaperQuestion', back_populates='paper')
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __init__(self, **kwargs):
        super(Paper, self).__init__(**kwargs)
        self.__paper_construct__()

    @sqlalchemy.orm.reconstructor
    def __paper_construct__(self):
        self.build_profile()

    def question_objects(self):
        question_objects_list = []
        for question in self.ordered_paper_questions():
            question_objects_list.append(question.question)
        return question_objects_list

    def ordered_paper_questions(self):
        return db.session.query(PaperQuestion).filter_by(paper_id=self.id).order_by(PaperQuestion.order_number).all()

    def new_question(self, question):
        existing_paper_questions = self.ordered_paper_questions()
        paper_question = PaperQuestion(paper_id=self.id, question_id=question.id, order_number=len(existing_paper_questions)+1)
        return paper_question

    def remove_question(self, question_id):
        ordered_questions = sorted(self.paper_questions, key=lambda x: x.order_number)
        question = None
        removal_index = -1
        for i in range(0, len(ordered_questions)):
            if ordered_questions[i].question_id == question_id:
                removal_index = i
                break
        if removal_index < 0:
            return None
        for i in range(removal_index + 1, len(ordered_questions)):
            ordered_questions[i].order_number -= 1
        return ordered_questions[removal_index]

    def reorder_questions(self, new_question_ordering):
        if len(self.paper_questions) != len(new_question_ordering):
            print('Cannot reorder, bad lengths', len(self.paper_questions), len(new_question_ordering))
            return False
        paper_question_associations = self.ordered_paper_questions()
        for paper_question in paper_question_associations:
            try:
                # question order_number starts from 1
                new_question_order_number = new_question_ordering.index(paper_question.question_id) + 1
            except IndexError:
                print('Cannot find question to re-order:', paper_question.question_id)
                return False
            else:
                paper_question.order_number = new_question_order_number
        return True

    def build_profile(self):
        self.profile = paper_profile.PaperProfile()
        self.profile.total_questions = len(self.paper_questions)
        tag_list = []
        for paper_question in self.paper_questions:
            self.profile.total_points += paper_question.question.points
            for t in paper_question.question.tags:
                if t not in tag_list:
                    tag_list.append(t)

        for t in tag_list:
            new_tag_profile = paper_profile.build_tag_profile(self, t)
            new_tag_profile.calculate_q_percentage(self.profile)
            new_tag_profile.calculate_p_percentage(self.profile)
            self.profile.tag_profile_list.append(new_tag_profile)

    # TODO rename function, it mutates
    def check_clazz_scores(self, clazz):
        clazz_id = clazz.id
        scores = Score.query.filter_by(paper_id = self.id).all()
        clazz_scores = []
        for s in scores:
            student_id = s.student_id
            student = Student.query.get_or_404(student_id)
            if clazz in student.clazzes:
                clazz_scores.append(s)
        for s in clazz_scores:
            if s == None:
                self.has_all_scores = False
            else:
                self.has_all_scores = True

class Score(db.Model):
    __tablename__ = 'score'
    value = db.Column(db.Float)
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.aws_id'), nullable=False)

    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint(paper_id, question_id, student_id),
    )
