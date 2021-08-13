from alchemy import models
from alchemy.reports import data_manager

class ClazzReportSection:
    def __init__(self, html_macro):
        self.html_macro = html_macro

class OverviewSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        self.html_macro = html_macro
        self.clazz = clazz
        self.paper = paper
        self.clazz_paper_summary = None
        self.build_self()

    def build_self(self):
        all_scores = models.Score.query.filter_by(paper_id = self.paper.id).all()
        clazz_scores = data_manager.filter_scores_by_clazz(all_scores, self.clazz)
        self.clazz_paper_summary = data_manager.ClazzPaperSummary(self.paper, clazz_scores)

class OverviewPlotSection(ClazzReportSection):
        def __init__(self, html_macro, clazz, paper):
            self.html_macro = html_macro
            self.clazz = clazz
            self.paper = paper
            self.plot = None
            self.build_self()

        def build_self(self):
            all_scores = models.Score.query.filter_by(paper_id = self.paper.id).all()
            clazz_scores = data_manager.filter_scores_by_clazz(all_scores, self.clazz)
            self.plot = data_manager.create_distribution_plot(self.clazz, self.paper, clazz_scores)

class OverviewDetailsSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        self.html_macro = html_macro
        self.clazz = clazz
        self.paper = paper
        self.raw_statsumm = None
        self.norm_statsumm = None
        self.build_self()

    def build_self(self):
        all_scores = models.Score.query.filter_by(paper_id = self.paper.id).all()
        clazz_scores = data_manager.filter_scores_by_clazz(all_scores, self.clazz)
        student_summaries = data_manager.build_student_summaries(self.paper, clazz_scores)
        self.raw_statsumm = data_manager.StatSummary([summary.raw_total for summary in student_summaries])
        self.norm_statsumm = data_manager.NormStatSumm(self.raw_statsumm, self.paper.profile.total_points)

class GradeOverviewSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        self.html_macro = html_macro
        self.clazz = clazz
        self.paper = paper
        self.student_grade_dict = None
        self.grade_pie_data = None
        self.build_self()

    def build_self(self):
        all_scores = models.Score.query.filter_by(paper_id = self.paper.id).all()
        clazz_scores = data_manager.filter_scores_by_clazz(all_scores, self.clazz)
        student_summaries = data_manager.build_student_summaries(self.paper, clazz_scores)
        self.student_grade_dict = data_manager.make_student_grade_dict(student_summaries)
        self.grade_pie_data = data_manager.make_grade_pie_data(self.student_grade_dict)
