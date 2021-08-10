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

class ClazzSummarySection(StudentReportSection):
    def __init__(self, html_macro, paper, clazz):
        self.html_macro = html_macro
        self.paper = paper
        self.clazz = clazz
        self.clazz_summary = None
        self.build_self()

    def build_self(self):
        cohort_scores = models.Score.query.filter_by(paper_id = self.paper.id).all()
        clazz_scores = report_calc.filter_scores_by_clazz(cohort_scores, self.clazz)
        self.clazz_summary = report_calc.ClazzPaperSummary(self.paper, clazz_scores)

class CohortSummarySection(StudentReportSection):
    def __init__(self, html_macro, paper):
        self.html_macro = html_macro
        self.paper = paper
        self.cohort_summary = None
        self.build_self()

    def build_self(self):
        cohort_scores = models.Score.query.filter_by(paper_id = self.paper.id).all()
        self.cohort_summary = report_calc.CohortPaperSummary(self.paper, cohort_scores)

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
        self.question_highlights = report_calc.QuestionHighlights(self.student, self.paper, raw_scores)
        self.tag_highlights = report_calc.TagHighlights(self.student, self.paper, raw_scores)
