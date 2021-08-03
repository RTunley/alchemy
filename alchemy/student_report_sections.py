from alchemy import models, db, report_calc

class ReportSection:
    def __init__(self, title, data):
        self.title = title
        self.data = data

class Data:

def build_overview_section(student, clazz, paper):
    scores = models.Score.query.filter_by(student_id = student.id, paper_id = paper.id)
    overview_data = Data()
    overview_data.paper_total = paper.profile.total_points
    overview_data.raw_total = report_calc.total_score(scores)
    overview_data.percentage_total = report_calc.calc_percentage(raw_total, overview_data.paper_total)
    overview_data.grade = report_calc.determine_grade(percentage_total, clazz.course)
    return ReportSection('Overview', overview_data)
