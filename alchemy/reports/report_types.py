from alchemy.reports import student_paper_sections, clazz_paper_sections, cohort_paper_sections
from alchemy.reports import student_checkpoint_sections, checkpoint_data_manager, clazz_checkpoint_sections, cohort_checkpoint_sections

class StudentPaperReport(object):
    def __init__(self, student, clazz, paper, section_types):
        self.title = None
        self.subtitle = None
        self.student = student
        self.clazz = clazz
        self.paper = paper
        self.sections = []
        self.build_self(section_types)

    def build_self(self, section_types):
        self.title = f"{self.student.aws_user.family_name}, {self.student.aws_user.given_name} - Achievement Report"
        self.subtitle = f"{self.clazz.course.name} ({self.clazz.code}): {self.paper.title}"

        for section_type in section_types:
            section_class = getattr(student_paper_sections, section_type)
            section = section_class(student = self.student, paper = self.paper, clazz = self.clazz)
            self.sections.append(section)

class ClazzPaperReport(object):
    def __init__(self, clazz, paper, section_types):
        self.title = None
        self.subtitle = None
        self.clazz = clazz
        self.paper = paper
        self.sections = []
        self.build_self(section_types)

    def build_self(self, section_types):
        self.title = f"{self.clazz.code} - Achievement Report"
        self.subtitle = f"{self.clazz.course.name}: {self.paper.title}"

        for section_type in section_types:
            section_class = getattr(clazz_paper_sections, section_type)
            section = section_class(paper = self.paper, clazz = self.clazz)
            self.sections.append(section)

class CohortPaperReport(object):
    def __init__(self, paper, section_types) :
        self.title = None
        self.subtitle = None
        self.clazzes = []
        self.paper = paper
        self.sections = []
        self.build_self(section_types)

    def build_self(self, section_types):
        self.title = f"{self.paper.course.name} - Cohort Achievement Report"
        self.subtitle = f"Assessment: {self.paper.title}"
        self.clazzes = [clazz for clazz in self.paper.course.clazzes]

        for section_type in section_types:
            section_class = getattr(cohort_paper_sections, section_type)
            section = section_class(paper = self.paper)
            self.sections.append(section)

class StudentCheckpointReport(object):
    def __init__(self, student, clazz, checkpoint, section_types):
        self.title = None
        self.subtitle = None
        self.student = student
        self.clazz = clazz
        self.checkpoint = checkpoint
        self.sections = []
        self.build_self(section_types)

    def build_self(self, section_types):
        self.title = f"{self.student.aws_user.family_name}, {self.student.aws_user.given_name} - Achievement Report"
        self.subtitle = f"{self.clazz.course.name} ({self.clazz.code}): {self.checkpoint.snapshot.name}"

        for section_type in section_types:
            section_class = getattr(student_checkpoint_sections, section_type)
            section = section_class(student = self.student, checkpoint = self.checkpoint, clazz = self.clazz)
            self.sections.append(section)

class ClazzCheckpointReport(object):
    def __init__(self, clazz, checkpoint, section_types):
        self.title = None
        self.subtitle = None
        self.clazz = clazz
        self.checkpoint = checkpoint
        self.sections = []
        self.build_self(section_types)

    def build_self(self, section_types):
        self.title = f"{self.clazz.code} - Achievement Report"
        self.subtitle = f"{self.clazz.course.name}: {self.checkpoint.snapshot.name}"

        for section_type in section_types:
            section_class = getattr(clazz_checkpoint_sections, section_type)
            section = section_class(checkpoint = self.checkpoint, clazz = self.clazz)
            self.sections.append(section)

class CohortCheckpointReport(object):
    def __init__(self, checkpoint, section_types):
        self.title = None
        self.subtitle = None
        self.checkpoint = checkpoint
        self.sections = []
        self.build_self(section_types)

    def build_self(self, section_types):
        self.title = "Full Cohort - Achievement Report"
        self.subtitle = f"{self.checkpoint.course.name}: {self.checkpoint.snapshot.name}"

        for section_type in section_types:
            section_class = getattr(cohort_checkpoint_sections, section_type)
            section = section_class(checkpoint = self.checkpoint)
            self.sections.append(section)

class SnapshotReport(object):
    def __init__(self, student, snapshot):
        self.title = None
        self.subtitle = None
        self.student = student
        self.snapshot = snapshot
        self.checkpoint_sections = []
        self.build_self()

    def build_self(self):
        self.title = f"{self.student.aws_user.family_name}, {self.student.aws_user.given_name} - Summary Report"
        self.subtitle = f"{self.snapshot.name}"

        for clazz in self.student.clazzes:
            course = clazz.course
            for checkpoint in course.checkpoints:
                if checkpoint.snapshot == self.snapshot:
                    section = checkpoint_data_manager.StudentSnapshotSection(self.student, checkpoint)
                    self.checkpoint_sections.append(section)
