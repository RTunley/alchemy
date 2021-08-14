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
        self.tally = data_manager.PaperMultiScoreTally.from_clazz(self.clazz, self.paper)

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

class GradeOverviewSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        self.html_macro = html_macro
        self.clazz = clazz
        self.paper = paper
        self.student_grade_dict = None
        self.grade_pie_data = None
        self.build_self()

    def build_self(self):
        student_tallies = [data_manager.PaperScoreTally.from_student(student, self.paper) for student in self.clazz.students]
        self.student_grade_dict = data_manager.make_student_grade_dict(student_tallies, self.paper.course)
        self.grade_pie_data = data_manager.make_grade_pie_data(self.student_grade_dict)

class TagOverviewSection(ClazzReportSection):
    def __init__(self, html_macro, clazz, paper):
        self.html_macro = html_macro
        self.clazz = clazz
        self.paper = paper
        self.tag_center_bar_plot = None
        self.tag_spread_bar_plot = None
        self.build_self()

    def build_self(self):
        self.tag_center_bar_plot, self.tag_spread_bar_plot = data_manager.make_tag_comparison_charts(self.clazz, self.paper)

# class QuestionOverviewSection(ClazzReportSection):
#     def __init__(self, html_macro, clazz, paper):
#         self.html_macro = html_macro
#         self.clazz = clazz
#         self.paper = paper
#         self.question_center_bar_plot = None
#         self.question_spread_bar_plot = None
#         self.build_self()
#
#     def build_self(self):
#         pass
