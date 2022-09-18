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
        self.checkpoint_tally = checkpoint_data_manager.CheckpointTally(self.student, self.checkpoint)
