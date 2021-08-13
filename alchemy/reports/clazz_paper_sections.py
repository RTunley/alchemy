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
        self.build_self()

    def build_self(self):
        self.tally = data_manager.MultiPaperScoreTally.from_clazz(self.clazz, self.paper)

class OverviewPlotSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        self.html_macro = html_macro
        self.clazz = clazz
        self.paper = paper
        self.plot = None
        self.build_self()

    def build_self(self):
        self.plot = data_manager.create_distribution_plot(self.clazz, self.paper)

class OverviewDetailsSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        self.html_macro = html_macro
        self.clazz = clazz
        self.paper = paper
        self.raw_statsumm = None
        self.norm_statsumm = None
        self.build_self()

    def build_self(self):
        self.raw_statsumm = data_manager.StatSummary(data_manager.total_student_scores_for_clazz(self.clazz, self.paper))
        self.norm_statsumm = data_manager.NormStatSumm(self.raw_statsumm, self.paper.profile.total_points)
