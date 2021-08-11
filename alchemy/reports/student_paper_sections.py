from alchemy import models
from alchemy.reports import data_manager

class StudentReportSection:
    def __init__(self, html_macro):
        self.html_macro = html_macro

class OverviewSection(StudentReportSection):
    def __init__(self, html_macro, student, paper):
        self.html_macro = html_macro
        self.student = student
        self.paper = paper
        self.student_paper_summary = None
        self.build_self()

    def build_self(self):
        scores = models.Score.query.filter_by(student_id = self.student.id, paper_id = self.paper.id).all()
        self.student_paper_summary = data_manager.StudentPaperSummary(self.student, self.paper, scores)

class AdjacentGradesSection(StudentReportSection):
    def __init__(self, html_macro, student, paper):
        self.html_macro = html_macro
        self.student = student
        self.paper = paper
        self.student_paper_summary = None
        self.adjacent_grades = None
        self.build_self()

    def build_self(self):
        scores = models.Score.query.filter_by(student_id = self.student.id, paper_id = self.paper.id).all()
        self.student_paper_summary = data_manager.StudentPaperSummary(self.student, self.paper, scores)
        self.adjacent_grades = data_manager.AdjacentGrades(self.paper.course.grade_levels, self.student_paper_summary.percent_total, self.student_paper_summary.grade, self.student_paper_summary.paper_total)

class ClazzSummarySection(StudentReportSection):
    def __init__(self, html_macro, paper, clazz):
        self.html_macro = html_macro
        self.paper = paper
        self.clazz = clazz
        self.clazz_summary = None
        self.build_self()

    def build_self(self):
        cohort_scores = models.Score.query.filter_by(paper_id = self.paper.id).all()
        clazz_scores = data_manager.filter_scores_by_clazz(cohort_scores, self.clazz)
        self.clazz_summary = data_manager.ClazzPaperSummary(self.paper, clazz_scores)

class CohortSummarySection(StudentReportSection):
    def __init__(self, html_macro, paper):
        self.html_macro = html_macro
        self.paper = paper
        self.cohort_summary = None
        self.build_self()

    def build_self(self):
        cohort_scores = models.Score.query.filter_by(paper_id = self.paper.id).all()
        self.cohort_summary = data_manager.CohortPaperSummary(self.paper, cohort_scores)

## Strengths and Weaknesses = Highlights

class HighlightsSection(StudentReportSection):
    def __init__(self, html_macro, student, paper):
        self.html_macro = html_macro
        self.student = student
        self.paper = paper
        self.question_highlights = None
        self.tag_highlights = None
        self.build_self()

    def build_self(self):
        raw_scores = models.Score.query.filter_by(student_id = self.student.id, paper_id = self.paper.id).all()
        self.question_highlights = data_manager.QuestionHighlights(self.student, self.paper, raw_scores)
        self.tag_highlights = data_manager.TagHighlights(self.student, self.paper, raw_scores)
