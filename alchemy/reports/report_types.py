from alchemy.reports import student_paper_sections, clazz_paper_sections, cohort_paper_sections

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
        print(self.sections)


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
