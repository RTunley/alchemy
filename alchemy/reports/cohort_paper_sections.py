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

class OverviewPlotSection(CohortReportSection):
    def __init__(self, html_macro, paper):
        super().__init__(html_macro, paper)

    def build_self(self):
        self.plot = data_manager.create_cohort_distribution_plot(self.paper)

class OverviewDetailsSection(CohortReportSection):
    def __init__(self, html_macro, paper):
        super().__init__(html_macro, paper)

    def build_self(self):
        self.statprofile = data_manager.StatProfile(data_manager.total_student_scores_for_cohort(self.paper), self.paper.profile.total_points)

class GradeOverviewSection(CohortReportSection):
    def __init__(self, html_macro, paper):
        super().__init__(html_macro, paper)

    def build_self(self):
        clazzes = self.paper.course.clazzes
        student_tallies = []
        for clazz in clazzes:
            for student in clazz.students:
                paper_score_tally = data_manager.PaperScoreTally.from_student(student, self.paper)
                student_tallies.append(paper_score_tally)

        self.grade_batch_list = data_manager.make_grade_batch_list(student_tallies, self.paper.course)
        self.grade_pie_data = data_manager.make_grade_pie_data(self.grade_batch_list)
