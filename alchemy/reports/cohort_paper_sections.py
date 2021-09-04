from alchemy import models
from alchemy.reports import data_manager

class CohortReportSection:
    def __init__(self, html_macro, paper):
        self.html_macro = html_macro
        self.paper = paper
        self.build_self()

class OverviewSection(CohortReportSection):
    def __init__(self, html_macro, paper):
        super().__init__(html_macro, paper)

    def build_self(self):
         self.tally = data_manager.PaperMultiScoreTally.from_cohort(self.paper)
