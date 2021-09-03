from alchemy import models
from alchemy.reports import data_manager

class ClazzReportSection:
    def __init__(self, html_macro, clazz, paper):
        self.html_macro = html_macro
        self.clazz = clazz
        self.paper = paper
        self.build_self()

class OverviewSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        super().__init__(html_macro, clazz, paper)

    def build_self(self):
        self.tally = data_manager.PaperMultiScoreTally.from_clazz(self.clazz, self.paper)

class OverviewPlotSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        super().__init__(html_macro, clazz, paper)

    def build_self(self):
        self.plot = data_manager.create_clazz_distribution_plot(self.clazz, self.paper)

class OverviewDetailsSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        super().__init__(html_macro, clazz, paper)

    def build_self(self):
        self.statprofile = data_manager.StatProfile(data_manager.total_student_scores_for_clazz(self.clazz, self.paper), self.paper.profile.total_points)

class GradeOverviewSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        super().__init__(html_macro, clazz, paper)

    def build_self(self):
        student_tallies = [data_manager.PaperScoreTally.from_student(student, self.paper) for student in self.clazz.students]
        self.grade_batch_list = data_manager.make_grade_batch_list(student_tallies, self.paper.course)
        self.grade_pie_data = data_manager.make_grade_pie_data(self.grade_batch_list)

class TagOverviewSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        super().__init__(html_macro, clazz, paper)

    def build_self(self):
        self.statprofiles = data_manager.make_tag_statprofile_list(self.clazz, self.paper)
        self.center_bar_plot, self.spread_bar_plot = data_manager.make_comparison_charts(self.statprofiles)

class QuestionOverviewSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        super().__init__(html_macro, clazz, paper)

    def build_self(self):
        self.statprofiles = data_manager.make_question_statprofile_list(self.clazz, self.paper)
        self.center_bar_plot, self.spread_bar_plot = data_manager.make_comparison_charts(self.statprofiles)

class TagDetailsSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        super().__init__(html_macro, clazz, paper)

    def build_self(self):
        self.statprofiles = data_manager.make_tag_statprofile_list(self.clazz, self.paper)
        self.plots = data_manager.make_achievement_plots(self.statprofiles)

class QuestionDetailsSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        super().__init__(html_macro, clazz, paper)

    def build_self(self):
        self.statprofiles = data_manager.make_question_statprofile_list(self.clazz, self.paper)
        self.plots = data_manager.make_achievement_plots(self.statprofiles)
