from alchemy import models, db, report_calc

class ReportSection:
    def __init__(self, title, data):
        self.title = title
        self.data = data

class Data:
    raw_total = 0

def build_overview_section(student, clazz, paper):
    scores = models.Score.query.filter_by(student_id = student.id, paper_id = paper.id).all()
    print('Scores are: ', scores)
    overview_data = Data()
    overview_data.paper_total = paper.profile.total_points
    overview_data.raw_total = report_calc.total_score(scores)
    print('raw_total = ', overview_data.raw_total)
    overview_data.percentage_total = report_calc.calc_percentage(overview_data.raw_total, overview_data.paper_total)
    overview_data.grade = report_calc.determine_grade(overview_data.percentage_total, clazz.course)
    return ReportSection('Overview', overview_data)
