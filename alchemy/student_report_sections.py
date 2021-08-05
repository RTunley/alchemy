from alchemy import models, db, report_calc

class StudentReportSection:
    def __init__(self, title, data):
        self.title = title
        self.data = data

## Each ReportSection will have a data attribute, but exactly what it contains depends on what that section needs to show. Currently each section will do it's own retrieval from the db for whatever information it needs.

class Data:
    raw_total = 0

def build_overview_section(student, clazz, paper):
    scores = models.Score.query.filter_by(student_id = student.id, paper_id = paper.id).all()
    raw_total = report_calc.total_score(scores)
    paper_total = paper.profile.total_points
    percentage_total = report_calc.calc_percentage(raw_total, paper_total)
    grade = report_calc.determine_grade(percentage_total, clazz.course)
    data = Data()
    data.paper_total = paper_total
    data.raw_total = raw_total
    data.percentage_total = percentage_total
    data.grade = grade

    return StudentReportSection('Overview', data)

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
    data.raw_diff_higher_grade = round(data.diff_higher_grade*paper.profile.total_points/100, 1)
    data.next_lowest_grade = adjacent_grades_obj.next_lowest_grade
    data.diff_lower_grade = adjacent_grades_obj.diff_lower_grade
    data.raw_diff_lower_grade = round(data.diff_lower_grade*paper.profile.total_points/100, 1)

    return StudentReportSection(None, data)
