'''
Populates the Alchemy database with a set of dummy data for testing/development.

Run this from the root alchemy directory:
    python -m tools.populate
'''
from alchemy import application
from tools import db_data

def populate_db():
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

if __name__ == '__main__':
    populate_db()
