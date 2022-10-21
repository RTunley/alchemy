from alchemy import models
from alchemy.reports import data_manager, checkpoint_data_manager

class ClazzReportSection:
    def __init__(self, html_macro, **kwargs):
        self.html_macro = html_macro
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.build_self()

class OverviewSection(ClazzReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/clazz/checkpoint_report_sections/overview.html', **section_kwargs)

    def build_self(self):
        self.tally = checkpoint_data_manager.CheckpointMultiScoreTally.from_clazz(self.clazz, self.checkpoint)


class GradeOverviewSection(ClazzReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('course/clazz/checkpoint_report_sections/grades_overview.html', **section_kwargs)

    def build_self(self):
        student_tallies = [checkpoint_data_manager.StudentCheckpointTally(student, self.checkpoint) for student in self.clazz.students]
        self.grade_batch_list = data_manager.make_grade_batch_list(student_tallies, self.checkpoint.course)
        self.grade_pie_data = data_manager.make_grade_pie_data(self.grade_batch_list)
