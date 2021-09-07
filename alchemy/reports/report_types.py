from alchemy.reports import student_paper_sections, clazz_paper_sections, cohort_paper_sections

class StudentPaperReport(object):
    def __init__(self, student, clazz, paper, section_types=['OverviewSection', 'AdjacentGradesSection', 'ClazzSummarySection', 'CohortSummarySection', 'HighlightsSection']):
        self.title = None
        self.subtitle = None
        self.student = student
        self.clazz = clazz
        self.paper = paper
        self.sections = []
        self.build_self(section_types)

    def build_self(self, section_types):
        self.title = f"{self.student.aws_user.family_name}, {self.student.aws_user.given_name} - Achievment Report"
        self.subtitle = f"{self.clazz.course.name} ({self.clazz.code}): {self.paper.title}"

        for section_type in section_types:
            section_class = getattr(student_paper_sections, section_type)
            section = section_class(student = self.student, paper = self.paper, clazz = self.clazz)
            self.sections.append(section)

class ClazzPaperReport(object):
    def __init__(self, clazz, paper, section_types = ['OverviewSection', 'OverviewPlotSection', 'OverviewDetailsSection', 'GradeOverviewSection', 'TagOverviewSection', 'QuestionOverviewSection', 'TagDetailsSection', 'QuestionDetailsSection']):
        self.title = None
        self.subtitle = None
        self.clazz = clazz
        self.paper = paper
        self.sections = []
        self.build_self(section_types)

    def build_self(self, section_types):
        self.title = f"{self.clazz.code} - Achievment Report"
        self.subtitle = f"{self.clazz.course.name}: {self.paper.title}"

        for section_type in section_types:
            section_class = getattr(clazz_paper_sections, section_type)
            section = section_class(paper = self.paper, clazz = self.clazz)
            self.sections.append(section)

class CohortPaperReport(object):
    def __init__(self, paper, section_types = ['OverviewSection', 'OverviewPlotSection', 'OverviewDetailsSection', 'GradeOverviewSection']):
        self.title = None
        self.subtitle = None
        self.clazzes = []
        self.paper = paper
        self.sections = []
        self.build_self(section_types)

    def build_self(self, section_types):
        self.title = f"{self.paper.course.name} - Cohort Achievment Report"
        self.subtitle = f"Assessment: {self.paper.title}"
        self.clazzes = [clazz for clazz in self.paper.course.clazzes]

        for section_type in section_types:
            section_class = getattr(cohort_paper_sections, section_type)
            section = section_class(paper = self.paper)
            self.sections.append(section)
