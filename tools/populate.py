'''
Populates the Alchemy database with a set of dummy data for testing/development.

Run this from the root alchemy directory:
    python -m tools.populate
'''
import os
from alchemy import db
from tools import db_data

def populate_db():
    db_path = os.path.join(os.getcwd(), 'alchemy/master.db')
    if os.path.exists(db_path):
        print('Removing existing db:', db_path)
        os.remove(os.path.join(os.getcwd(), 'alchemy/master.db'))
        db.create_all()
    print('Populating test data...')

    sci_department = db_data.add_department("Science")
    course = db_data.add_course(sci_department, 'IGCSE Physics')
    course_grades = db_data.add_grade_levels(course)
    clazz = db_data.add_clazz(course, 'IGPHY01')
    all_questions = db_data.add_questions_and_tags(course)
    mc_questions = db_data.get_mc_questions(all_questions)
    oa_questions = db_data.get_oa_questions(all_questions)
    papers = db_data.add_papers_and_categories(course)
    db_data.add_questions_to_test(papers[0], all_questions)
    db_data.add_questions_to_test(papers[1], mc_questions)
    db_data.add_questions_to_test(papers[2], oa_questions)

    #other courses and classes to test student homepage
    course_chem = db_data.add_course(sci_department, 'IGCSE Chemistry')
    grades_chem = db_data.add_grade_levels(course_chem)
    clazz_chem = db_data.add_clazz(course_chem, 'IGCHEM01')

    math_department = db_data.add_department("Mathematics")
    course_math = db_data.add_course(math_department, 'IGCSE Mathematics')
    grades_math = db_data.add_grade_levels(course_math)
    clazz_math = db_data.add_clazz(course_math, 'IGMAT01')

    hum_department = db_data.add_department("Humanities")
    course_mus = db_data.add_course(hum_department, 'IGCSE Music')
    grades_mus = db_data.add_grade_levels(course_mus)
    clazz_mus = db_data.add_clazz(course_mus, 'IGMUS01')
    course_eng = db_data.add_course(hum_department, 'IGCSE English')
    grades_eng = db_data.add_grade_levels(course_eng)
    clazz_eng = db_data.add_clazz(course_eng, 'IGMUS01')

    clazzes = [clazz, clazz_chem, clazz_math, clazz_mus, clazz_eng]
    student_list = db_data.add_students_and_aws_users(clazzes)
    db_data.add_scores(papers[0], student_list)

    db_data.add_admin_and_aws_users()

    print('Done!')

if __name__ == '__main__':
    populate_db()
