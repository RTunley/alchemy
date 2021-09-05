from alchemy import models
from alchemy.reports import data_manager

class StudentReportSection:
    def __init__(self, html_macro, student, clazz, paper):
        self.html_macro = html_macro
        self.student = student
        self.clazz = clazz
        self.paper = paper
        self.build_self()

class OverviewSection(StudentReportSection):
    def __init__(self, html_macro, student, clazz, paper):
        super().__init__('student/report_section_macros/overview.html', student, clazz, paper)

    def build_self(self):
        self.tally = data_manager.PaperScoreTally.from_student(self.student, self.paper)

class AdjacentGradesSection(StudentReportSection):
    def __init__(self, html_macro, student, clazz, paper):
        super().__init__('student/report_section_macros/adjacent_grades.html', student, clazz, paper)

    def build_self(self):
        tally = data_manager.PaperScoreTally.from_student(self.student, self.paper)
        self.adjacent_grades = data_manager.AdjacentGrades(self.paper.course.grade_levels, tally.percent_total, tally.grade, tally.paper_total)

class ClazzSummarySection(StudentReportSection):
    def __init__(self, html_macro, student, clazz, paper):
        self.html_macro = 'student/report_section_macros/clazz_summary.html'
        self.paper = paper
        self.clazz = clazz
        self.build_self()

    def build_self(self):
        self.tally = data_manager.PaperMultiScoreTally.from_clazz(self.clazz, self.paper)

class CohortSummarySection(StudentReportSection):
    def __init__(self, html_macro, student, clazz, paper):
        self.html_macro = 'student/report_section_macros/cohort_summary.html'
        self.paper = paper
        self.build_self()

    def build_self(self):
        self.tally = data_manager.PaperMultiScoreTally.from_cohort(self.paper)

## Strengths and Weaknesses = Highlights

class HighlightsSection(StudentReportSection):
    def __init__(self, html_macro, student, clazz, paper):
        super().__init__('student/report_section_macros/highlights_section.html', student, clazz, paper)

    def build_self(self):
        raw_scores = models.Score.query.filter_by(student_id = self.student.id, paper_id = self.paper.id).all()
        self.question_highlights = data_manager.QuestionHighlightSets(self.student, self.paper)
        self.tag_highlights = data_manager.TagHighlightSets(self.student, self.paper, raw_scores)
