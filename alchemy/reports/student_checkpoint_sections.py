from alchemy import models
from alchemy.reports import data_manager, checkpoint_data_manager

class StudentReportSection:
    def __init__(self, html_macro, **kwargs):
        self.html_macro = html_macro
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.build_self()

class OverviewSection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/checkpoint_report_sections/overview.html', **section_kwargs)

    def build_self(self):
        self.checkpoint_tally = checkpoint_data_manager.StudentCheckpointTally(self.student, self.checkpoint)

class AdjacentGradesSection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/checkpoint_report_sections/adjacent_grades.html', **section_kwargs)

    def build_self(self):
        checkpoint_tally = checkpoint_data_manager.StudentCheckpointTally(self.student, self.checkpoint)
        self.adjacent_grades = checkpoint_data_manager.AdjacentGrades(self.checkpoint.course.grade_levels, checkpoint_tally.percentage, checkpoint_tally.grade)
