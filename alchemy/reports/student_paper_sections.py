from alchemy import models
from alchemy.reports import data_manager

class StudentReportSection:
    def __init__(self, html_macro, **kwargs):
        self.html_macro = html_macro
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.build_self()

class OverviewSection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/report_section_macros/overview.html', **section_kwargs)

    def build_self(self):
        self.tally = data_manager.PaperScoreTally.from_student(self.student, self.paper)

class AdjacentGradesSection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/report_section_macros/adjacent_grades.html', **section_kwargs)

    def build_self(self):
        tally = data_manager.PaperScoreTally.from_student(self.student, self.paper)
        self.adjacent_grades = data_manager.AdjacentGrades(self.paper.course.grade_levels, tally.percent_total, tally.grade, tally.paper_total)

class ClazzSummarySection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/report_section_macros/clazz_summary.html', **section_kwargs)
        self.build_self()

    def build_self(self):
        self.tally = data_manager.PaperMultiScoreTally.from_clazz(self.clazz, self.paper)

class CohortSummarySection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/report_section_macros/cohort_summary.html', **section_kwargs)

    def build_self(self):
        self.tally = data_manager.PaperMultiScoreTally.from_cohort(self.paper)

## Strengths and Weaknesses = Highlights

class HighlightsSection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/report_section_macros/highlights_section.html', **section_kwargs)

    def build_self(self):
        raw_scores = models.Score.query.filter_by(student_id = self.student.id, paper_id = self.paper.id).all()
        self.question_highlights = data_manager.QuestionHighlightSets(self.student, self.paper)
        self.tag_highlights = data_manager.TagHighlightSets(self.student, self.paper, raw_scores)

class TagDetailsSection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/report_section_macros/tag_details.html', **section_kwargs)

    def build_self(self):
        raw_scores = models.Score.query.filter_by(student_id = self.student.id, paper_id = self.paper.id).all()
        # self.question_highlights = data_manager.QuestionHighlightSets(self.student, self.paper)
        # self.tag_highlights = data_manager.TagHighlightSets(self.student, self.paper, raw_scores)

class QuestionDetailsSection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/report_section_macros/question_details.html', **section_kwargs)

    def build_self(self):
        raw_scores = models.Score.query.filter_by(student_id = self.student.id, paper_id = self.paper.id).all()
        question_statsumms = data_manager.make_student_statsumm_list(self.student, self.paper)
        self.oa_statsumms = data_manager.only_oa_statsumms(question_statsumms)
        self.mc_statsumms = data_manager.only_mc_statsumms(question_statsumms)
        print(self.mc_statsumms)
        self.oa_question_chart = data_manager.make_student_question_chart(self.paper, raw_scores)
