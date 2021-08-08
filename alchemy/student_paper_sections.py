from alchemy import models, db, report_calc

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
        self.student_paper_summary = report_calc.StudentPaperSummary(self.student, self.paper, scores)

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
        self.student_paper_summary = report_calc.StudentPaperSummary(self.student, self.paper, scores)
        self.adjacent_grades = report_calc.AdjacentGrades(self.paper.course.grade_levels, self.student_paper_summary.percent_total, self.student_paper_summary.grade, self.student_paper_summary.paper_total)

class CohortSummarySection(StudentReportSection):
    def __init__(self, html_macro, paper):
        self.html_macro = html_macro
        self.paper = paper
        self.cohort_summary = None
        self.build_self()

    def build_self(self):
        cohort_scores = models.Score.query.filter_by(paper_id = self.paper.id).all()
        self.cohort_summary = report_calc.CohortPaperSummary(self.paper, cohort_scores)
