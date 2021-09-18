import sqlalchemy
from alchemy import db
import alchemy.views.profile as paper_profile
import base64, string

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
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'))
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

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    aws_id = db.Column(db.Integer, db.ForeignKey('aws_user.id'))
    aws_user = db.relationship('AwsUser')
    clazzes = db.relationship('Clazz', secondary=clazzes_students, back_populates='students')
    scores = db.relationship('Score', backref='student')

    @staticmethod
    def create(**properties):
        'Creates a Student and its accompanying AwsUser from the specified properties.'
        clazzes = properties.pop('clazzes', [])
        scores = properties.pop('scores', [])
        aws_user = AwsUser.create('student', **properties)
        return Student(id=aws_user.id, aws_user=aws_user, clazzes=clazzes, scores=scores)

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    aws_id = db.Column(db.Integer, db.ForeignKey('aws_user.id'))
    aws_user = db.relationship('AwsUser')

    @staticmethod
    def create(**properties):
        'Creates a Admin and its accompanying AwsUser from the specified properties.'
        aws_user = AwsUser.create('admin', **properties)
        return Admin(id=aws_user.id, aws_user=aws_user)

class AwsUser(db.Model):
    __tablename__ = 'aws_user'
    id = db.Column(db.Integer, primary_key=True)
    sub = db.Column(db.String(64), unique=True) # UUID string
    username = db.Column(db.String(64), nullable=False)
    group = db.Column(db.String(64), nullable=False) # Would we support multiple groups per user?

    # Additional user attributes in the user pool
    email = db.Column(db.String(64))
    given_name = db.Column(db.String(32))
    family_name = db.Column(db.String(32))

    USER_ATTRIBUTES = ('given_name', 'family_name', 'email')

    def update_user_attributes(self, user_attrs):
        updated = False
        for field_key in AwsUser.USER_ATTRIBUTES:
            if type(user_attrs) == dict:
                field_value = user_attrs.get(field_key)
            else:
                field_value = getattr(user_attrs, field_key)
            if field_value is not None and field_value != getattr(self, field_key, ''):
                setattr(self, field_key, field_value)
                updated = True
        return updated

    def matches_user_attributes(self, user_attrs):
        for field_key in AwsUser.USER_ATTRIBUTES:
            field_value = user_attrs.get(field_key, '')
            if field_value != getattr(self, field_key, ''):
                return False
        return True

    @staticmethod
    def create(group, **properties):
        if not group:
            raise ValueError('No AwsUser group specified')
        if not properties.get('email'):
            raise ValueError('No AwsUser email specified')
        email = properties['email'].lower() # avoid casing issues with email and username, AWS will auto-lowercase the username
        user_id = properties.pop('id', None)    # optional, will auto-generate if not specified
        unexpected_keys = [key for key in properties.keys() if key not in AwsUser.USER_ATTRIBUTES]
        if unexpected_keys:
            raise ValueError('Unexpected AwsUser properties specified:', unexpected_keys)
        aws_user = AwsUser(id=user_id, group=group, username=email)
        aws_user.update_user_attributes(properties)
        return aws_user

    @staticmethod
    def from_jwt(jwt_payload):
        sub = jwt_payload.get('sub')
        username = jwt_payload.get('username')
        for field in (sub, username):
            if not field:
                raise ValueError(f'Error: field {field} not found in JWT payload: {jwt_payload}')
        groups = jwt_payload.get('cognito:groups')
        if not groups:
            raise ValueError(f'Error: user is not in a group! JWT payload: {jwt_payload}')
        if len(groups) > 1:
            raise ValueError('Error: only 1 group supported, but user {username} has multiple groups: {groups}')
        aws_user = AwsUser.query.filter_by(sub = sub).first()
        if aws_user is None:
            aws_user = AwsUser.query.filter_by(username = username).first()
            if aws_user:
                # This user was created locally, so now assign it the sub found on the server
                # that matches the same username.
                aws_user.sub = sub
                db.session.commit()
        if aws_user is None:
            print(f'Creating new user from payload', jwt_payload)
            aws_user = AwsUser(sub = sub, username = username, group = groups[0])
        return aws_user


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

question_solution_choices = db.Table('question_solution_choices', db.Model.metadata,
    db.Column('question_id', db.ForeignKey('question.id'), primary_key=True),
    db.Column('solution_id', db.ForeignKey('solution.id'), primary_key=True)
)

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(), nullable=False)

    solution_id = db.Column(db.Integer, db.ForeignKey('solution.id'))
    solution = db.relationship('Solution')
    solution_choices = db.relationship('Solution', secondary=question_solution_choices)

    points = db.Column(db.Float(), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    tags = db.relationship('Tag', secondary=questions_tags, back_populates='questions')
    papers = db.relationship('PaperQuestion', back_populates='question')
    scores = db.relationship('Score', backref='question')
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    image = db.relationship("Image", back_populates='questions')

    def is_multiple_choice(self):
        return self.solution_choices is not None and len(self.solution_choices) > 0

    def decode_image(self):
        return self.image.content.decode('ascii')

    def solution_choice_index(self):
        'Returns the index of the correct solution choice.'
        for i in range(len(self.solution_choices)):
            if self.solution_choices[i] == self.solution:
                return i
        return -1

    def describe_solution(self, solution):
        '''Returns a text description of the solution.
           E.g. "A) The answer" if this matches the first solution for a multiple
           choice question, otherwise just returns "The answer".'''
        for i in range(len(self.solution_choices)):
            if self.solution_choices[i] == solution:
                label = string.ascii_uppercase[i]
                return f'{label}) {solution.content}'
        return solution.content

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    @staticmethod
    def solution_prefixes(prefixes_range):
        prefixes = []
        for i in range(prefixes_range):
            prefixes.append((string.ascii_uppercase[i], ''))
        return prefixes


class Solution(db.Model):
    __tablename__ = 'solution'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(), nullable=False)

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.LargeBinary, nullable=False)
    questions = db.relationship('Question', back_populates='image')

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
        if not new_question_ordering:
            return False
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
            for tag in paper_question.question.tags:
                if tag not in tag_list:
                    tag_list.append(tag)

        for tag in tag_list:
            new_tag_profile = paper_profile.build_tag_profile(self, tag)
            new_tag_profile.calculate_q_percentage(self.profile)
            new_tag_profile.calculate_p_percentage(self.profile)
            self.profile.tag_profile_list.append(new_tag_profile)

    # TODO rename function, it mutates
    def check_clazz_scores(self, clazz):
        clazz_id = clazz.id
        scores = Score.query.filter_by(paper_id = self.id).all()
        clazz_scores = []
        for score in scores:
            student_id = score.student_id
            student = Student.query.get_or_404(student_id)
            if clazz in student.clazzes:
                clazz_scores.append(score)
        for score in clazz_scores:
            if score == None:
                self.has_all_scores = False
            else:
                self.has_all_scores = True

class Score(db.Model):
    __tablename__ = 'score'
    value = db.Column(db.Float)
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint(paper_id, question_id, student_id),
    )

class JwtBlocklist(db.Model):
    __tablename__ = 'jwt_blocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    issued_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
