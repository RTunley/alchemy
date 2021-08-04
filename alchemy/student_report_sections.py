from alchemy import models, db, report_calc

class ReportSection:
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
    overview_data = Data()
    overview_data.paper_total = paper_total
    overview_data.raw_total = raw_total
    overview_data.percentage_total = percentage_total
    overview_data.grade = grade

    return ReportSection('Overview', overview_data)
