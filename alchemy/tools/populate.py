from alchemy.tools import db_data
from alchemy import db

def populate_db(db):
    account = db_data.add_account()
    course = db_data.add_course(account)
    course_grades = db_data.add_grade_levels(course)
    clazz = db_data.add_clazz(course)
    question_list = db_data.add_questions_and_tags(course)
    paper = db_data.add_paper(course)
    db_data.add_questions_to_paper(paper, question_list)
    db_data.add_admin()
    student_list = db_data.add_students_and_aws_users(course)
    db_data.add_scores(paper, student_list)
