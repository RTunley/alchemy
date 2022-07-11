from alchemy import models
from alchemy.reports import data_manager

class CohortReportSection:
    def __init__(self, html_macro, **kwargs):
        self.html_macro = html_macro
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.build_self()

class OverviewSection(CohortReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/cohort/report_section_macros/overview.html', **section_kwargs)

    def build_self(self):
         self.tally = data_manager.PaperMultiScoreTally.from_cohort(self.paper)

class OverviewPlotSection(CohortReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/cohort/report_section_macros/overview_plot.html', **section_kwargs)

    def build_self(self):
        self.plot = data_manager.create_cohort_distribution_plot(self.paper)

class OverviewDetailsSection(CohortReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/cohort/report_section_macros/overview_details.html', **section_kwargs)

    def build_self(self):
        self.statprofile = data_manager.StatProfile(data_manager.total_student_scores_for_cohort(self.paper), self.paper.profile.total_points)

class GradeOverviewSection(CohortReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/cohort/report_section_macros/grades_overview.html', **section_kwargs)

    def build_self(self):
        all_students = data_manager.all_students_in_course(self.paper.course)
        student_tallies = []
        for student in all_students:
            paper_score_tally = data_manager.PaperScoreTally.from_student(student, self.paper)
            student_tallies.append(paper_score_tally)

        self.grade_batch_list = data_manager.make_grade_batch_list(student_tallies, self.paper.course)
        self.grade_pie_data = data_manager.make_grade_pie_data(self.grade_batch_list)

class TagOverviewSection(CohortReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/cohort/report_section_macros/tag_overview.html', **section_kwargs)

    def build_self(self):
        all_students = data_manager.all_students_in_course(self.paper.course)
        self.statprofiles = data_manager.make_tag_statprofile_list(all_students, self.paper)
        self.center_bar_plot, self.spread_bar_plot = data_manager.make_comparison_charts(self.statprofiles)

class QuestionOverviewSection(CohortReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/cohort/report_section_macros/question_overview.html', **section_kwargs)

    def build_self(self):
        all_students = data_manager.all_students_in_course(self.paper.course)
        if self.paper.has_oa_questions() and self.paper.has_mc_questions():
            self.question_group_statprofiles = data_manager.make_question_group_statprofiles(all_students, self.paper)
            self.oa_vs_mc_center_plot, self.oa_vs_mc_spread_plot = data_manager.make_comparison_charts(self.question_group_statprofiles)
        if self.paper.has_mc_questions():
            mcq_group_tallies = data_manager.make_mcq_group_tallies(self.paper, all_students)
            self.mcq_group_tallies = sorted(mcq_group_tallies, key=lambda x: x.num_correct_percent, reverse=True)
        if self.paper.has_oa_questions():
            self.statprofiles = data_manager.make_question_statprofile_list(all_students, self.paper)
            self.center_bar_plot, self.spread_bar_plot = data_manager.make_comparison_charts(self.statprofiles)

class TagDetailsSection(CohortReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/cohort/report_section_macros/tag_details.html', **section_kwargs)

    def build_self(self):
        all_students = data_manager.all_students_in_course(self.paper.course)
        self.statprofiles = data_manager.make_tag_statprofile_list(all_students, self.paper)
        self.plots = data_manager.make_achievement_plots(self.statprofiles)

class QuestionDetailsSection(CohortReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/cohort/report_section_macros/question_details.html', **section_kwargs)

    def build_self(self):
        all_students = data_manager.all_students_in_course(self.paper.course)
        if self.paper.has_mc_questions():
            mcq_group_tallies = data_manager.make_mcq_group_tallies(self.paper, all_students)
            self.mcq_batch_list = data_manager.make_mcq_batch_list(mcq_group_tallies)
        if self.paper.has_oa_questions():
            self.statprofiles = data_manager.make_question_statprofile_list(all_students, self.paper)
            self.plots = data_manager.make_achievement_plots(self.statprofiles)
