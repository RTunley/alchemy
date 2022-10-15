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
        super().__init__('student/paper_report_sections/overview.html', **section_kwargs)

    def build_self(self):
        self.tally = data_manager.PaperScoreTally.from_student(self.student, self.paper)

class AdjacentGradesSection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/paper_report_sections/adjacent_grades.html', **section_kwargs)

    def build_self(self):
        tally = data_manager.PaperScoreTally.from_student(self.student, self.paper)
        self.adjacent_grades = data_manager.AdjacentGrades(self.paper.course.grade_levels, tally.percent_total, tally.grade, tally.paper_total)

class ClazzSummarySection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/paper_report_sections/clazz_summary.html', **section_kwargs)

    def build_self(self):
        self.tally = data_manager.PaperMultiScoreTally.from_clazz(self.clazz, self.paper)

class CohortSummarySection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/paper_report_sections/cohort_summary.html', **section_kwargs)

    def build_self(self):
        self.tally = data_manager.PaperMultiScoreTally.from_cohort(self.paper)

## Strengths and Weaknesses = Highlights

class HighlightsSection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/paper_report_sections/highlights_section.html', **section_kwargs)

    def build_self(self):
        raw_scores = models.Score.query.filter_by(student_id = self.student.id, paper_id = self.paper.id).all()
        self.question_highlights = data_manager.QuestionHighlightSets(self.student, self.paper)
        self.tag_highlights = data_manager.TagHighlightSets(self.student, self.paper, raw_scores)
        self.all_same = False
        if self.question_highlights.all_min == True or self.question_highlights.all_max == True:
            self.all_same = True
        print("self dot all_same")
        print(self.all_same)
        print("Questions all_min")
        print(self.question_highlights.all_min)
        print("MC Questions all_min")
        print(self.question_highlights.all_mc_min)
        print("OA Questions all_min")
        print(self.question_highlights.all_oa_min)

class TagDetailsSection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/paper_report_sections/tag_details.html', **section_kwargs)

    def build_self(self):
        self.tag_statsumms = data_manager.make_tag_statsumm_list(self.student, self.paper)
        self.tag_chart = data_manager.make_student_statsumm_chart(self.tag_statsumms)

class QuestionDetailsSection(StudentReportSection):
    def __init__(self, **section_kwargs):
        super().__init__('student/paper_report_sections/question_details.html', **section_kwargs)

    def build_self(self):
        question_statsumms = data_manager.make_student_statsumm_list(self.student, self.paper)
        if self.paper.has_mc_questions():
            self.mc_statsumms = data_manager.only_mc_statsumms(question_statsumms)
        if self.paper.has_oa_questions():
            self.oa_statsumms = data_manager.only_oa_statsumms(question_statsumms)
            self.oa_question_chart = data_manager.make_student_statsumm_chart(self.oa_statsumms)
