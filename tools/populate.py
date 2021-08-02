'''
Populates the Alchemy database with a set of dummy data for testing/development.

Run this from the root alchemy directory:
    python -m tools.populate
'''
from alchemy import application
from tools import db_data

def populate_db():
    account = db_data.add_account()
    course = db_data.add_course(account, 'Physics')
    course_grades = db_data.add_grade_levels(course)
    clazz = db_data.add_clazz(course, 'IGPHY01')
    question_list = db_data.add_questions_and_tags(course)
    paper = db_data.add_paper(course)
    db_data.add_questions_to_paper(paper, question_list)

    #other courses and classes to test student homepage
    course_eng = db_data.add_course(account, 'English')
    grades_eng = db_data.add_grade_levels(course_eng)
    clazz_eng = db_data.add_clazz(course_eng, 'IGENG01')

    course_mus = db_data.add_course(account, 'Music')
    grades_mus = db_data.add_grade_levels(course_mus)
    clazz_mus = db_data.add_clazz(course_mus, 'IGMUS01')

    course_math = db_data.add_course(account, 'Mathematics')
    grades_math = db_data.add_grade_levels(course_math)
    clazz_math = db_data.add_clazz(course_math, 'IGMAT01')

    course_pe = db_data.add_course(account, 'Physical Education')
    grades_pe = db_data.add_grade_levels(course_pe)
    clazz_pe = db_data.add_clazz(course_pe, 'IGPHED01')

    clazzes = [clazz, clazz_eng, clazz_mus, clazz_math, clazz_pe]
    db_data.add_admin()
    student_list = db_data.add_students_and_aws_users(clazzes)
    db_data.add_scores(paper, student_list)

if __name__ == '__main__':
    populate_db()
