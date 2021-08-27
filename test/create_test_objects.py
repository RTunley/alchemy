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
    grade_F = m.GradeLevel(grade = 'F', lower_bound = 0, upper_bound = 30, course_id = course.id)

    course_grades = [grade_A, grade_B, grade_C, grade_D, grade_F]

    for gl in course_grades:
        db.session.add(gl)
    db.session.commit()
    return course_grades

def create_question1(course):
    test_question = m.Question(content = 'Not Very Challenging', solution = m.Solution(content='Simple Solution'), points = 4, course_id = course.id)
    db.session.add(test_question)
    db.session.commit()
    return test_question

def create_question2(course):
    test_question = m.Question(content = 'Very Challenging', solution = m.Solution(content='Difficult Solution'), points = 2, course_id = course.id)
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

def add_clazz(course):
    clazz = m.Clazz(code = 'clazz01', course_id = course.id)
    db.session.add(clazz)
    db.session.commit()
    return clazz

def make_sub(given_name, family_name, index):
    sub = 'aws-sub-' + given_name + '-' + family_name + '-' + str(index)
    return sub

def make_email(given_name, family_name, id):
    email = given_name+'.'+family_name+str(id)+'@schoolofrock.com'
    return email

def add_students_and_aws_users(course, clazz):
    index = 2000
    user_tuples = [('Jimmy', 'Knuckle'), ('AyAyRon', 'Dinglebop'), ('Beefy', 'Taco'), ('Chaneese', 'Spankle')]
    student_list = []

    for i in range(len(user_tuples)):
        given = user_tuples[i][0]
        family = user_tuples[i][1]
        sub = make_sub(given, family, index+i)
        email = make_email(given, family, index+i)
        aws_user = m.AwsUser(given_name = given, family_name = family, id = index+i, sub = sub, email = email, group = 'student', username = sub)
        db.session.add(aws_user)
        student = m.Student(aws_user = aws_user, clazzes = [clazz])
        student_list.append(student)
        db.session.add(student)

    db.session.commit()
    return(student_list)

def add_scores(paper, student_list):
    #test_paper contains two questions totallying 6 points (see add_question1 and add_question2). Need tuples for four students.
    score_tuples = [(4,2), (3,1), (2,0), (0,0)]
    for i in range(len(student_list)):
        for j in range(len(paper.paper_questions)):
            question_id = paper.paper_questions[j].question.id
            student_id = student_list[i].id
            new_score = m.Score(value = score_tuples[i][j], paper_id = paper.id, question_id = question_id, student_id = student_id)
            db.session.add(new_score)

    db.session.commit()
