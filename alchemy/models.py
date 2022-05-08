import sqlalchemy
from alchemy import db
from sqlalchemy.ext.orderinglist import ordering_list
import alchemy.views.profile as paper_profile
import base64, string

## Database Models ##

class School(db.Model):
    __tablename__ = 'school'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    departments = db.relationship('Department', backref='school')
    snapshots = db.relationship('Snapshot', backref='school')

class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    courses = db.relationship('Course', backref='department')

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    questions = db.relationship('Question', backref = 'q_course')
    tags = db.relationship('Tag', backref='tag_course')
    clazzes = db.relationship('Clazz', backref='course')
    papers = db.relationship('Paper', backref='course')
    #TODO should the backref on grade_levels be 'course' instead of 'grade_levels'?
    grade_levels = db.relationship('GradeLevel', backref='grade_levels')
    assessment_categories = db.relationship('AssessmentCategory', backref='assessment_categories')

    def order_grade_levels(self):
        self.grade_levels.sort(key=lambda x: x.lower_bound,  reverse = True)

    def order_assessment_categories(self):
        self.assessment_categories.sort(key=lambda x: x.weight,  reverse = True)

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

class AssessmentCategory(db.Model):
    __tablename__ = 'assessment_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    weight = db.Column(db.Float)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    papers = db.relationship('Paper', back_populates='category')

class Clazz(db.Model):
    __tablename__ = 'clazz'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    students = db.relationship('Student', secondary=clazzes_students, back_populates='clazzes',
        order_by='Student.id')

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    aws_id = db.Column(db.Integer, db.ForeignKey('aws_user.id'))
    aws_user = db.relationship('AwsUser')
    clazzes = db.relationship('Clazz', secondary=clazzes_students, back_populates='students')
    scores = db.relationship('Score', backref='student')

    def has_results_for_all_mc_questions(self, paper):
        count_paper_mc_questions = db.session.query(PaperQuestion
            ).filter(PaperQuestion.question_id == Question.id,
                     Question.correct_solution_index != None
            ).filter_by(paper_id = paper.id
            ).count()
        count_student_mc_scores = db.session.query(Score
            ).filter(Score.question_id == Question.id,
                     Question.correct_solution_index != None
            ).filter_by(student_id = self.id, paper_id = paper.id
            ).count()
        return count_paper_mc_questions == count_student_mc_scores

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

    def selected_solution_id(self, student_id):
        score = Score.query.filter_by(paper_id = self.paper_id, question_id = self.question_id,
                student_id = student_id).first()
        if score:
            return score.selected_solution_id
        return -1

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(), nullable=False)

    all_solutions = db.relationship('Solution',
            backref="question",
            order_by='Solution.order_number',
            collection_class=ordering_list('order_number'))
    correct_solution_index = db.Column(db.Integer)

    points = db.Column(db.Float(), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    tags = db.relationship('Tag', secondary=questions_tags, back_populates='questions')
    papers = db.relationship('PaperQuestion', back_populates='question')
    scores = db.relationship('Score', backref='question')
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    image = db.relationship("Image", back_populates='questions')

    def get_solution(self):
        if len(self.all_solutions) == 0:
            raise ValueError('all_solutions should never be empty')
        if len(self.all_solutions) == 1:
            return self.all_solutions[0]
        if self.correct_solution_index is None:
            print(f'Error, question {self.id} has multiple solution but no correct_solution_index')
            return None
        if self.correct_solution_index >= len(self.all_solutions):
            print(f'Error, question {self.id} has correct_solution_index={correct_solution_index} but only {len(self.all_solutions)} solutions')
            return None
        return self.all_solutions[self.correct_solution_index]

    def is_multiple_choice(self):
        return len(self.all_solutions) > 1

    def decode_image(self):
        return self.image.content.decode('ascii')

    def get_mc_solution_label(self):
        for i in range(len(self.all_solutions)):
            if self.all_solutions[i] == self.get_solution():
                solution_label = self.mcq_choice_prefix(i)
                return solution_label

    def describe_solution(self, solution):
        '''Returns a text description of the solution.
           E.g. "A) The answer" if this matches the first solution for a multiple
           choice question, otherwise just returns "The answer".'''
        for i in range(len(self.all_solutions)):
            if len(self.all_solutions)>1:
                if self.all_solutions[i] == solution:
                    label = string.ascii_uppercase[i]
                    return f'{label}) {solution.content}'
            else:
                if self.all_solutions[i] == solution:
                    return f'{solution.content}'
        return solution.content

    def get_solution_label(self, solution):
        for i in range(len(self.all_solutions)):
            if self.all_solutions[i] == solution:
                label = string.ascii_uppercase[i]
                return f'{label}'
        return ''

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    @staticmethod
    def create(**kwargs):
        correct_solution_index = kwargs.get('correct_solution_index', None)
        all_solutions = kwargs.get('all_solutions', None)
        if all_solutions and len(all_solutions) > 1:
            if correct_solution_index is None or not (0 <= correct_solution_index < len(all_solutions)):
                raise ValueError(f'correct_solution_index={correct_solution_index} is not valid index in solutions list of size {len(all_solutions)}')
        return Question(**kwargs)

    @staticmethod
    def mcq_choice_prefix(i):
        return string.ascii_uppercase[i]

    @staticmethod
    def mcq_choice_prefixes(prefixes_range):
        prefixes = []
        for i in range(prefixes_range):
            prefixes.append((string.ascii_uppercase[i], ''))
        return prefixes


class Solution(db.Model):
    __tablename__ = 'solution'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    content = db.Column(db.String(), nullable=False)
    order_number = db.Column(db.Integer)

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
    paper_questions = db.relationship('PaperQuestion',
            order_by='PaperQuestion.order_number',
            collection_class=ordering_list('order_number', count_from=1))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('assessment_category.id'), nullable=False)
    category = db.relationship('AssessmentCategory', back_populates='papers')

    def __init__(self, **kwargs):
        super(Paper, self).__init__(**kwargs)
        self.__paper_construct__()

    @sqlalchemy.orm.reconstructor
    def __paper_construct__(self):
        self.build_profile()

    def question_objects(self):
        question_objects_list = []
        for question in self.paper_questions:
            question_objects_list.append(question.question)
        return question_objects_list

    def has_mc_questions(self):
        has_mc_questions = False
        for question in self.question_objects():
            if question.is_multiple_choice():
                return True
        else:
            return False

    def has_oa_questions(self):
        has_oa_questions = False
        for question in self.question_objects():
            if not question.is_multiple_choice():
                return True
        else:
            return False

    def get_mc_paper_questions(self):
        return [paper_question for paper_question in self.paper_questions if paper_question.question.is_multiple_choice()]

    def get_oa_paper_questions(self):
        return [paper_question for paper_question in self.paper_questions if not paper_question.question.is_multiple_choice()]

    def new_question(self, question):
        # Place multiple-choice questions before open-answer questions
        insertion_index = len(self.paper_questions)
        if question.is_multiple_choice():
            # insert it before the first open answer question
            insertion_index = self.open_answer_questions_start_index()
        paper_question = PaperQuestion(paper_id=self.id, question_id=question.id)
        self.paper_questions.insert(insertion_index, paper_question)
        return paper_question

    def remove_question(self, question_id):
        for question in self.paper_questions:
            if question.question_id == question_id:
                self.paper_questions.remove(question)
                return question
        return None

    ## TODO eliminate this so that indexing continues from MC section into OA section
    def open_answer_questions_start_index(self):
        for i in range(len(self.paper_questions)):
            if not self.paper_questions[i].question.is_multiple_choice():
                return i
        return 0

    def reorder_questions(self, new_question_ordering):
        if not new_question_ordering:
            return False
        # Place multiple-choice questions before open-answer questions
        open_answer_questions_start_index = self.open_answer_questions_start_index()
        mcqs = self.paper_questions[:open_answer_questions_start_index]
        open_answer_questions = self.paper_questions[open_answer_questions_start_index:]

        first_question = Question.query.get_or_404(new_question_ordering[0])
        questions_to_reorder = mcqs if first_question.is_multiple_choice() else open_answer_questions

        if len(questions_to_reorder) != len(new_question_ordering):
            print('Cannot reorder, bad lengths', len(questions_to_reorder), len(new_question_ordering))
            return False
        reordered_questions = sorted(questions_to_reorder, key=lambda paper_question: new_question_ordering.index(paper_question.question_id))

        if first_question.is_multiple_choice():
            self.paper_questions = reordered_questions + open_answer_questions
        else:
            self.paper_questions = mcqs + reordered_questions
        self.paper_questions.reorder()
        return True

    def build_profile(self):
        self.profile = paper_profile.PaperProfile()
        self.profile.total_questions = len(self.paper_questions)
        tag_list = []
        for pq in self.paper_questions:
            if len(pq.question.all_solutions) > 1:
                self.profile.total_mc_questions += 1
                self.profile.total_mc_points += pq.question.points
            elif len(pq.question.all_solutions) == 1:
                self.profile.total_oa_questions += 1
                self.profile.total_oa_points += pq.question.points
            else:
                pass
            ## TODO do we need this else? Are there checks in place to ensure that there are ONLY questions with 1 or multiple solutions?
            self.profile.total_points += pq.question.points
            for tag in pq.question.tags:
                if tag not in tag_list:
                    tag_list.append(tag)
        if self.profile.total_mc_questions > 0:
            self.profile.has_mc_questions = True
        if self.profile.total_points != 0:
            self.profile.mcq_points_norm_ratio = round(self.profile.total_mc_points/self.profile.total_points*100, 1)
            self.profile.oaq_points_norm_ratio = round(self.profile.total_oa_points/self.profile.total_points*100, 1)

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
                return False
            else:
                return True

    def has_all_scores(self):
        scores = Score.query.filter_by(paper_id = self.id).all()
        for score in scores:
            if score == None:
                return False
            else:
                return True

    def has_all_student_scores(self, student):
        scores = Score.query.filter_by(paper_id = self.id, student_id = student.id).all()
        for score in scores:
            if score == None:
                return False
            else:
                return True

class Score(db.Model):
    __tablename__ = 'score'
    value = db.Column(db.Float)
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    # null if an open-answer question, or the selected solution hasn't been entered into db
    selected_solution_id = db.Column(db.Integer, db.ForeignKey('solution.id'), nullable=True)

    __table_args__ = (
        sqlalchemy.PrimaryKeyConstraint(paper_id, question_id, student_id),
    )

class Snapshot(db.Model):
    __tablename__ = 'snapshot'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))

    def make_checkpoints(self, course_list):
        self.courses = course_list
        for course in self.courses:
            new_checkpoint = None
            self.checkpoints.append(new_checkpoint)

    def is_ready(self):
        if not self.checkpoints:
            return False
        else:
            for checkpoint in self.checkpoints:
                if not checkpoint.check_if_ready():
                    return False
                else:
                    return True

class JwtBlocklist(db.Model):
    __tablename__ = 'jwt_blocklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    issued_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
