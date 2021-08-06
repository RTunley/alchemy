from alchemy import models, db, report_calc

class StudentReportSection:
    def __init__(self, html_macro):
        self.html_macro = html_macro

class OverviewSection(StudentReportSection):
    def __init__(self, html_macro, student, clazz, paper):
        self.html_macro = html_macro
        self.student = student
        self.clazz = clazz
        self.paper = paper
        self.paper_total = self.paper.profile.total_points
        self.raw_total = 0
        self.percent_total = 0
        self.grade = None
        self.build_self()

    def build_self(self):
        scores = models.Score.query.filter_by(student_id = self.student.id, paper_id = self.paper.id).all()
        self.raw_total = report_calc.total_score(scores)
        self.percent_total = report_calc.calc_percentage(self.raw_total, self.paper_total)
        self.grade = report_calc.determine_grade(self.percent_total, self.clazz.course)


def build_adjacent_grades_section(student, clazz, paper):
    overview_data = build_overview_section(student, clazz, paper).data
    grade_list = clazz.course.grade_levels
    adjacent_grades_obj = report_calc.get_adjacent_grades(grade_list, overview_data.percentage_total, overview_data.grade)
    data = Data()
    data.paper_total = overview_data.paper_total
    data.raw_total = overview_data.raw_total
    data.percentage_total = overview_data.percentage_total
    data.grade = overview_data.grade
    print('Data Object: ', data)
    print('Adjacent Grades Object: ', adjacent_grades_obj)
    data.next_highest_grade = adjacent_grades_obj.next_highest_grade
    data.diff_higher_grade = adjacent_grades_obj.diff_higher_grade
    if data.next_highest_grade:
        data.raw_diff_higher_grade = round(data.diff_higher_grade*paper.profile.total_points/100, 1)
    else:
        data.raw_diff_higher_grade = None
    data.next_lowest_grade = adjacent_grades_obj.next_lowest_grade
    data.diff_lower_grade = adjacent_grades_obj.diff_lower_grade
    if data.next_lowest_grade:
        data.raw_diff_lower_grade = round(data.diff_lower_grade*paper.profile.total_points/100, 1)
    else:
        data.raw_diff_lower_grade = None

    return StudentReportSection(None, data)
