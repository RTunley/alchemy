'''
Populates the Alchemy database with a set of dummy data for testing/development.

Run this from the root alchemy directory:
    python -m tools.populate
'''
import os
from alchemy import application, db
from tools import db_data

def populate_db():
    db_path = os.path.join(os.getcwd(), 'alchemy/master.db')
    if os.path.exists(db_path):
        print('Removing existing db:', db_path)
        os.remove(os.path.join(os.getcwd(), 'alchemy/master.db'))
    print('Populating test data...')

    school = db_data.add_school("School of Rock")

    sci_department = db_data.add_department(school, "Science")
    course = db_data.add_course(sci_department, 'IGCSE Physics')
    course_grades = db_data.add_grade_levels(course)
    clazz1 = db_data.add_clazz(course, 'IGPHY01')
    clazz2 = db_data.add_clazz(course, 'IGPHY02')
    all_questions = db_data.add_questions_and_tags(course)
    mc_questions = db_data.get_mc_questions(all_questions)
    oa_questions = db_data.get_oa_questions(all_questions)
    papers = db_data.add_papers_and_categories_physics(course)
    db_data.add_questions_to_paper(papers[0], all_questions)
    db_data.add_questions_to_paper(papers[1], mc_questions)
    db_data.add_questions_to_paper(papers[2], oa_questions)

    #other courses and classes to test student homepage

    math_department = db_data.add_department(school, "Mathematics")
    course_math = db_data.add_course(math_department, 'IGCSE Mathematics')
    grades_math = db_data.add_grade_levels(course_math)
    clazz_math1 = db_data.add_clazz(course_math, 'IGMAT01')
    clazz_math2 = db_data.add_clazz(course_math, 'IGMAT02')

    hum_department = db_data.add_department(school, "Humanities")
    course_eng = db_data.add_course(hum_department, 'IGCSE English')
    grades_eng = db_data.add_grade_levels(course_eng)
    clazz_eng1 = db_data.add_clazz(course_eng, 'IGENG01')
    clazz_eng2 = db_data.add_clazz(course_eng, 'IGENG02')

    courses = [course_math, course_eng]
    other_papers = db_data.add_other_papers_and_categories(courses)
    clazzes1 = [clazz1, clazz_math1, clazz_eng1]
    clazzes2 = [clazz2, clazz_math2, clazz_eng2]
    student_list1, student_list2 = db_data.add_students_and_aws_users(clazzes1, clazzes2)
    for paper in papers:
        db_data.add_scores(paper, student_list1)
        db_data.add_scores(paper, student_list2)

    db_data.add_admin_and_aws_users()

    print('Done!')

if __name__ == '__main__':
    with application.app_context():
        db.create_all()
        populate_db()
