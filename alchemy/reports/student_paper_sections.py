from alchemy import models
from alchemy.reports import data_manager

class StudentReportSection:
    def __init__(self, html_macro, student, paper):
        self.html_macro = html_macro
        self.student = student
        self.paper = paper
        self.build_self()

class OverviewSection(StudentReportSection):
    def __init__(self, html_macro, student, paper):
        super().__init__(html_macro, student, paper)

    def build_self(self):
        self.tally = data_manager.PaperScoreTally.from_student(self.student, self.paper)

class AdjacentGradesSection(StudentReportSection):
    def __init__(self, html_macro, student, paper):
        super().__init__(html_macro, student, paper)

    def build_self(self):
        tally = data_manager.PaperScoreTally.from_student(self.student, self.paper)
        self.adjacent_grades = data_manager.AdjacentGrades(self.paper.course.grade_levels, tally.percent_total, tally.grade, tally.paper_total)

class ClazzSummarySection(StudentReportSection):
    def __init__(self, html_macro, paper, clazz):
        self.html_macro = html_macro
        self.paper = paper
        self.clazz = clazz
        self.build_self()

    def build_self(self):
        self.tally = data_manager.PaperMultiScoreTally.from_clazz(self.clazz, self.paper)

class CohortSummarySection(StudentReportSection):
    def __init__(self, html_macro, paper):
        self.html_macro = html_macro
        self.paper = paper
        self.build_self()

    def build_self(self):
        self.tally = data_manager.PaperMultiScoreTally.from_cohort(self.paper)

## Strengths and Weaknesses = Highlights

class HighlightsSection(StudentReportSection):
    def __init__(self, html_macro, student, paper):
        super().__init__(html_macro, student, paper)

    def build_self(self):
        raw_scores = models.Score.query.filter_by(student_id = self.student.id, paper_id = self.paper.id).all()
        self.question_highlights = data_manager.QuestionHighlightSets(self.student, self.paper)
        self.tag_highlights = data_manager.TagHighlightSets(self.student, self.paper, raw_scores)
