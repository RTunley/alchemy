from alchemy.reports import student_paper_sections, clazz_paper_sections, cohort_paper_sections

class StudentPaperReport(object):
    def __init__(self, student, clazz, paper, section_types=['OverviewSection', 'AdjacentGradesSection', 'ClazzSummarySection', 'CohortSummarySection', 'HighlightsSection']):
        self.title = None
        self.subtitle = None
        self.student = student
        self.clazz = clazz
        self.paper = paper
        self.sections = []
        self.build_self(section_types)

    def build_self(self, section_types):
        self.title = f"{self.student.aws_user.family_name}, {self.student.aws_user.given_name} - Achievment Report"
        self.subtitle = f"{self.clazz.course.name} ({self.clazz.code}): {self.paper.title}"

        for section_type in section_types:
            section_class = getattr(student_paper_sections, section_type)
            section = section_class(student = self.student, paper = self.paper, clazz = self.clazz)
            self.sections.append(section)

class ClazzPaperReport(object):
    def __init__(self, clazz, paper, section_types = ['OverviewSection', 'OverviewPlotSection', 'OverviewDetailsSection', 'GradeOverviewSection', 'TagOverviewSection', 'QuestionOverviewSection', 'TagDetailsSection', 'QuestionDetailsSection']):
        self.title = None
        self.subtitle = None
        self.clazz = clazz
        self.paper = paper
        self.sections = []
        self.build_self(section_types)

    def build_self(self, section_types):
        self.title = f"{self.clazz.code} - Achievment Report"
        self.subtitle = f"{self.clazz.course.name}: {self.paper.title}"

        for section_type in section_types:
            section_class = getattr(clazz_paper_sections, section_type)
            section = section_class(paper = self.paper, clazz = self.clazz)
            self.sections.append(section)

    # def old_build_self(self):
    #     self.title = f"{self.clazz.code} - Achievment Report"
    #     self.subtitle = f"{self.clazz.course.name}: {self.paper.title}"
    #
    #     overview_section = clazz_paper_sections.OverviewSection('course/clazz/report_section_macros/overview.html', self.clazz, self.paper)
    #     self.sections.append(overview_section)
    #
    #     overview_plot_section = clazz_paper_sections.OverviewPlotSection('course/clazz/report_section_macros/overview_plot.html', self.clazz, self.paper)
    #     self.sections.append(overview_plot_section)
    #
    #     overview_details_section = clazz_paper_sections.OverviewDetailsSection('course/clazz/report_section_macros/overview_details.html', self.clazz, self.paper)
    #     self.sections.append(overview_details_section)
    #
    #     grade_overview_section = clazz_paper_sections.GradeOverviewSection('course/clazz/report_section_macros/grades_overview.html', self.clazz, self.paper)
    #     self.sections.append(grade_overview_section)
    #
    #     tag_overview_section = clazz_paper_sections.TagOverviewSection('course/clazz/report_section_macros/tag_overview.html', self.clazz, self.paper)
    #     self.sections.append(tag_overview_section)
    #
    #     question_overview_section = clazz_paper_sections.QuestionOverviewSection('course/clazz/report_section_macros/question_overview.html', self.clazz, self.paper)
    #     self.sections.append(question_overview_section)
    #
    #     tag_details_section = clazz_paper_sections.TagDetailsSection('course/clazz/report_section_macros/tag_details.html', self.clazz, self.paper)
    #     self.sections.append(tag_details_section)
    #
    #     question_details_section = clazz_paper_sections.QuestionDetailsSection('course/clazz/report_section_macros/question_details.html', self.clazz, self.paper)
    #     self.sections.append(question_details_section)

class CohortPaperReport(object):
    def __init__(self, paper):
        self.title = None
        self.subtitle = None
        self.clazzes = []
        self.paper = paper
        self.sections = []
        self.build_self()

    def build_self(self):
        self.title = f"{self.paper.course.name} - Cohort Achievment Report"
        self.subtitle = f"Assessment: {self.paper.title}"
        self.clazzes = [clazz for clazz in self.paper.course.clazzes]

        overview_section = cohort_paper_sections.OverviewSection('course/cohort/report_section_macros/overview.html', self.paper)
        self.sections.append(overview_section)

        overview_plot_section = cohort_paper_sections.OverviewPlotSection('course/cohort/report_section_macros/overview_plot.html', self.paper)
        self.sections.append(overview_plot_section)

        overview_details_section = cohort_paper_sections.OverviewDetailsSection('course/cohort/report_section_macros/overview_details.html', self.paper)
        self.sections.append(overview_details_section)

        grade_overview_section = cohort_paper_sections.GradeOverviewSection('course/cohort/report_section_macros/grades_overview.html', self.paper)
        self.sections.append(grade_overview_section)
