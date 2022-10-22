from alchemy import models
from alchemy.reports import data_manager, checkpoint_data_manager

class CohortReportSection:
    def __init__(self, html_macro, **kwargs):
        self.html_macro = html_macro
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.build_self()

class OverviewSection(CohortReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/cohort/checkpoint_report_sections/overview.html', **section_kwargs)

    def build_self(self):
        self.tally = checkpoint_data_manager.CheckpointMultiScoreTally.from_cohort(self.checkpoint)

class GradeOverviewSection(CohortReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/cohort/checkpoint_report_sections/grades_overview.html', **section_kwargs)

    def build_self(self):
        all_students = []
        for clazz in self.checkpoint.course.clazzes:
            for student in clazz.students:
                all_students.append(student)
        student_tallies = [checkpoint_data_manager.StudentCheckpointTally(student, self.checkpoint) for student in all_students]
        self.grade_batch_list = data_manager.make_grade_batch_list(student_tallies, self.checkpoint.course)
        self.grade_pie_data = data_manager.make_grade_pie_data(self.grade_batch_list)

class OverviewDetailsSection(CohortReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/cohort/checkpoint_report_sections/overview_details.html', **section_kwargs)

    def build_self(self):
        all_students = []
        for clazz in self.checkpoint.course.clazzes:
            for student in clazz.students:
                all_students.append(student)
        student_tallies = [checkpoint_data_manager.StudentCheckpointTally(student, self.checkpoint) for student in all_students]
        self.statprofile = checkpoint_data_manager.GroupStatProfile([tally.percent_total for tally in student_tallies])
        self.plot = checkpoint_data_manager.create_distribution_plot(f"Distribution of Average Achievement across {self.checkpoint.course.name}", self.statprofile)

class TagOverviewSection(CohortReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/cohort/checkpoint_report_sections/tag_overview.html', **section_kwargs)

    def build_self(self):
        all_students = []
        for clazz in self.checkpoint.course.clazzes:
            for student in clazz.students:
                all_students.append(student)
        self.tag_profiles = checkpoint_data_manager.all_checkpoint_tag_profiles(self.checkpoint, all_students)
        self.center_bar_plot, self.spread_bar_plot = checkpoint_data_manager.make_comparison_charts(self.tag_profiles)
