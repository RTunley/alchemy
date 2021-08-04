from alchemy import student_report_sections

class StudentPaperReport(object):
    def __init__(self, title, subtitle, student, clazz, paper, sections):
        self.title = title
        self.subtitle = subtitle
        self.student = student
        self.clazz = clazz
        self.paper = paper
        self.sections = sections

# TODO What should be in the sections list?

def make_student_paper_report(student, clazz, paper):
    title = f"{student.aws_user.family_name}, {student.aws_user.given_name} - Achievment Report"
    subtitle = f"{clazz.course.name} ({clazz.code}): {paper.title}"
    student_report = StudentPaperReport(title, subtitle, student, clazz, paper, [])
    ## TODO can we loop through the desired sections and add them as a list?
    overview_section = student_report_sections.build_overview_section(student, clazz, paper)
    student_report.sections.append(overview_section)
    return student_report
