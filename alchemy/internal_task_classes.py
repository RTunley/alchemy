## TODO this is pseudocode - not implemented anywhere, just an idea for how to organize this type of assessment task

class Paper(db.Model):
    __tablename__ = 'paper'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    scores = db.relationship('Score', backref='paper')
    paper_questions = db.relationship('PaperQuestion', back_populates='paper')
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

class InternalTask(db.Model):
    __tablename__ = 'internal_task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    # scores = db.relationship('Score', backref='paper')
    # TODO need something like scores - the achievement associated with each criteria section (see below)
    matrix_id = db.Column(db.Integer, db.ForeignKey('criteria_matrix.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

class CriteriaMatrix(object):
    def __init__(self, title, max_points, sections):
        self.title = title
        self.max_points = max_points
        self.sections = sections

class CriteriaSection(object):
    def __init__(self, title, max_points, criterion):
        self.title = title
        self.max_points = max_points
        self.criterion = criterion

    def set_criterion_max_points(self, criterion_max_is_same):
        if criterion_max_is_same:
            for criteria in self.criterion:
                criteria.max_points = self.max_points
        else:
            pass
            ## TODO Need some method to set individual criteria maximums

class Criteria(object):
    def __init__(self, title, max_points, descriptors):
        self.max_points = max_points
        self.descriptors = descriptors

class Descriptor(object):
    def __init__(self, content, min_points, max_points):
        self.content = content
        self.min_points = min_points
        self.max_points = max_points
        # TODO The max_points of the critteria will be the same as the largest max_points of the descriptors.

## Example - IB Science Criteria (Biology, Physics, Chemistry) ##

## Communication Descriptors and Section ##

comm_1_1 = Descriptor("The presentation of the investigation is unclear, making it difficult to understand the focus, process and outcomes.", 1, 2)
comm_1_2 = Descriptor("The presentation of the investigation is clear. Any errors do not hamper understanding of the focus, process and outcomes.", 3, 4)
comm_2_1 = Descriptor("The report is not well structured and is unclear: the necessary information on focus, process and outcomes is missing or is presented in an incoherent or disorganized way.", 1, 2)
comm_2_2 = Descriptor("The report is well structured and clear: the necessary information on focus, process and outcomes is present and presented in a coherent way.", 3, 4)
comm_3_1 = Descriptor("The understanding of the focus, process and outcomes of the investigation is obscured by the presence of inappropriate or irrelevant information.", 1, 2)
comm_3_2 = Descriptor("The report is relevant and concise thereby facilitating a ready understanding of the focus, process and outcomes of the investigation.", 3, 4)
comm_4_1 = Descriptor("There are many errors in the use of subject specific terminology and conventions.", 1, 2)
comm_4_2 = Descriptor("The use of subject-specific terminology and conventions is appropriate and correct. Any errors do not hamper understanding.", 3, 4)

communication_criteria_1 = Criteria(4, [comm_1_1, comm_1_2])
communication_criteria_2 = Criteria(4, [comm_2_1, comm_2_2])
communication_criteria_3 = Criteria(4, [comm_3_1, comm_3_2])
communication_criteria_4 = Criteria(4, [comm_4_1, comm_4_2])

communication_section = CriteriaSection("Communication", 4, [communication_criteria_1, communication_criteria_2, communication_criteria_3, communication_criteria_4])
