from alchemy.reports import student_paper_sections, clazz_paper_sections

class StudentPaperReport(object):
    def __init__(self, student, clazz, paper):
        self.title = None
        self.subtitle = None
        self.student = student
        self.clazz = clazz
        self.paper = paper
        self.sections = []
        self.build_self()

    def build_self(self):
        self.title = f"{self.student.aws_user.family_name}, {self.student.aws_user.given_name} - Achievment Report"
        self.subtitle = f"{self.clazz.course.name} ({self.clazz.code}): {self.paper.title}"
        overview_section = student_paper_sections.OverviewSection('student/report_section_macros/overview.html', self.student, self.paper)
        self.sections.append(overview_section)

        adjacent_grades_section = student_paper_sections.AdjacentGradesSection('student/report_section_macros/adjacent_grades.html', self.student, self.paper)
        self.sections.append(adjacent_grades_section)

        cohort_summary_section = student_paper_sections.CohortSummarySection('student/report_section_macros/cohort_summary.html', self.paper)
        self.sections.append(cohort_summary_section)

        clazz_summary_section = student_paper_sections.ClazzSummarySection('student/report_section_macros/clazz_summary.html', self.paper, self.clazz)
        self.sections.append(clazz_summary_section)

        highlights_section = student_paper_sections.HighlightsSection('student/report_section_macros/highlights_section.html', self.student, self.paper)
        self.sections.append(highlights_section)

class ClazzPaperReport(object):
    def __init__(self, clazz, paper):
        self.title = None
        self.subtitle = None
        self.clazz = clazz
        self.paper = paper
        self.sections = []
        self.build_self()

    def build_self(self):
        self.title = f"{self.clazz.code} - Achievment Report"
        self.subtitle = f"{self.clazz.course.name}: {self.paper.title}"

        overview_section = clazz_paper_sections.OverviewSection('course/clazz/report_section_macros/overview.html', self.clazz, self.paper)
        self.sections.append(overview_section)

        overview_plot_section = clazz_paper_sections.OverviewPlotSection('course/clazz/report_section_macros/overview_plot.html', self.clazz, self.paper)
        self.sections.append(overview_plot_section)

        overview_details_section = clazz_paper_sections.OverviewDetailsSection('course/clazz/report_section_macros/overview_details.html', self.clazz, self.paper)
        self.sections.append(overview_details_section)

        grade_overview_section = clazz_paper_sections.GradeOverviewSection('course/clazz/report_section_macros/grades_overview.html', self.clazz, self.paper)
        self.sections.append(grade_overview_section)

        tag_overview_section = clazz_paper_sections.TagOverviewSection('course/clazz/report_section_macros/tag_overview.html', self.clazz, self.paper)
        self.sections.append(tag_overview_section)

        question_overview_section = clazz_paper_sections.QuestionOverviewSection('course/clazz/report_section_macros/question_overview.html', self.clazz, self.paper)
        self.sections.append(question_overview_section)

        tag_details_section = clazz_paper_sections.TagDetailsSection('course/clazz/report_section_macros/tag_details.html', self.clazz, self.paper)
        self.sections.append(tag_details_section)

        question_details_section = clazz_paper_sections.QuestionDetailsSection('course/clazz/report_section_macros/question_details.html', self.clazz, self.paper)
        self.sections.append(question_details_section)
