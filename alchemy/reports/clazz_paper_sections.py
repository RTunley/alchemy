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
