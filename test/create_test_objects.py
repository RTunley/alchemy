from alchemy import models as m
from alchemy import db

def create_account():
    test_account = m.Account(name = "Test School")
    db.session.add(test_account)
    db.session.commit()
    return test_account

def create_course(account):
    test_course = m.Course(name = "Test Course", account = account)
    db.session.add(test_course)
    db.session.commit()
    return test_course

def create_grade_levels(course):
    grade_A = m.GradeLevel(grade = 'A', lower_bound = 85, upper_bound = 100, course_id = course.id)
    grade_B = m.GradeLevel(grade = 'B', lower_bound = 70, upper_bound = 85, course_id = course.id)
    grade_C = m.GradeLevel(grade = 'C', lower_bound = 50, upper_bound = 70, course_id = course.id)
    grade_D = m.GradeLevel(grade = 'D', lower_bound = 30, upper_bound = 50, course_id = course.id)
    grade_F = m.GradeLevel(grade = 'F', lower_bound = 30, upper_bound = 0, course_id = course.id)

    course_grades = [grade_A, grade_B, grade_C, grade_D, grade_F]

    for gl in course_grades:
        db.session.add(gl)
    db.session.commit()
    return course_grades

def create_question1(course):
    test_question = m.Question(content = 'Not Very Challenging', solution = 'Simple Solution', points = 4, course_id = course.id)
    db.session.add(test_question)
    db.session.commit()
    return test_question

def create_question2(course):
    test_question = m.Question(content = 'Very Challenging', solution = 'Difficult Solution', points = 2, course_id = test_course1.id)
    db.session.add(test_question)
    db.session.commit()
    return test_question

def create_lone_tag(course, name):
    test_tag = m.Tag(name = name, course_id = course.id)
    db.session.add(test_tag)
    db.session.commit()
    return test_tag

def create_attached_tag(course, question, name):
    test_tag = m.Tag(name = name, course_id = course.id, questions = [question])
    db.session.add(test_tag)
    db.session.commit()
    return test_tag

def create_paper(course):
    test_paper = m.Paper(title = "A Very Short Quiz", course_id = course.id)
    db.session.add(test_paper)
    db.session.commit()
    return test_paper

def add_question_to_paper(paper, question):
    index = len(paper.paper_questions)
    pq = m.PaperQuestion(paper_id = paper.id, question_id = question.id, order_number = index+1)
    db.session.add(pq)
    db.session.commit()
