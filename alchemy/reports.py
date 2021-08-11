from alchemy import student_paper_sections, clazz_paper_sections

class StudentPaperReport(object):
    def __init__(self, student, clazz, paper):
        self.title = None
        self.subtitle = None
        self.student = student
        self.clazz = clazz
        self.paper = paper
        self.sections = []
        self.build_self()

    # TODO a list of selected sections should be an input to this class -> worry about this later. For now we will add them manually below:
    def build_self(self):
        self.title = f"{self.student.aws_user.family_name}, {self.student.aws_user.given_name} - Achievment Report"
        self.subtitle = f"{self.clazz.course.name} ({self.clazz.code}): {self.paper.title}"
        overview_section = student_paper_sections.OverviewSection('student/report_section_macros/overview.html', self.student, self.paper)
        self.sections.append(overview_section)

        adjacent_grades_section = student_paper_sections.AdjacentGradesSection('student/report_section_macros/adjacent_grades.html', self.student, self.paper)
        self.sections.append(adjacent_grades_section)

        cohort_summary_section = student_paper_sections.CohortSummarySection('student/report_section_macros/cohort_summary.html', self.paper)
        self.sections.append(cohort_summary_section)

        clazz_summary_section = student_paper_sections.ClazzSummarySection('student/report_section_macros/clazz_summary.html', self.paper, self.clazz)
        self.sections.append(clazz_summary_section)

        highlights_section = student_paper_sections.HighlightsSection('student/report_section_macros/highlights_section.html', self.student, self.paper)
        self.sections.append(highlights_section)

class ClazzPaperReport(object):
    def __init__(self, clazz, paper):
        self.title = None
        self.subtitle = None
        self.clazz = clazz
        self.paper = paper
        self.sections = []
        self.build_self()

    # TODO a list of selected sections should be an input to this class -> worry about this later. For now we will add them manually below:
    def build_self(self):
        self.title = f"{self.clazz.code} - Achievment Report"
        self.subtitle = f"{self.clazz.course.name}: {self.paper.title}"
        overview_section = clazz_paper_sections.OverviewSection('course/clazz/report_section_macros/overview.html', self.clazz, self.paper)
        self.sections.append(overview_section)
