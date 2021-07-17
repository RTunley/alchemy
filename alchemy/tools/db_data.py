from alchemy import models as m
from alchemy import db

def add_account():
    account = m.Account(name = "School of Rock")
    db.session.add(account)
    db.commit()
    return(account)


def add_course(account):
    test_course = m.Course(name = "IGCSE Physics", account = account)
    db.session.add(test_course)
    db.session.commit()
    return(course)

def add_grade_levels(course):
    grade_Astar = m.GradeLevel(grade = 'A*', lower_bound = 85, upper_bound = 100, course_id = course.id)
    grade_A = m.GradeLevel(grade = 'A', lower_bound = 75, upper_bound = 85, course_id = course.id)
    grade_B = m.GradeLevel(grade = 'B', lower_bound = 65, upper_bound = 75, course_id = course.id)
    grade_C = m.GradeLevel(grade = 'C', lower_bound = 55, upper_bound = 65, course_id = course.id)
    grade_D = m.GradeLevel(grade = 'D', lower_bound = 45, upper_bound = 55, course_id = course.id)
    grade_E = m.GradeLevel(grade = 'F', lower_bound = 35, upper_bound = 45, course_id = course.id)
    grade_F = m.GradeLevel(grade = 'F', lower_bound = 25, upper_bound = 35, course_id = course.id)
    grade_G = m.GradeLevel(grade = 'F', lower_bound = 15, upper_bound = 25, course_id = course.id)
    grade_U = m.GradeLevel(grade = 'F', lower_bound = 0, upper_bound = 15, course_id = course.id)

    course_grades = [grade_Astar, grade_A, grade_B, grade_C, grade_D, grade_E, grade_F, grade_G, grade_U]

    for gl in course_grades:
        db.session.add(gl)
    db.session.commit()
    return(course_grades)

def add_questions_and_tags(course):
    tag_1 = m.Tag(name = 'Algebra', course = course.id)
    tag_2 = m.Tag(name = 'Calculate', course = course.id)
    tag_3 = m.Tag(name = 'Explain', course = course.id)

    tags = [tag_1, tag_2, tag_3]
    for t in tags:
        db.session.add(t)
    db.session.commit()

    content_1 = """Calculate the average acceleration of a cyclist whose velocity changes from 2.1 m/s \([S]\) to 2.5 m/s \([W]\) over 3.5 seconds. """
    solution_1 = """Since \(a = \frac{\Delta v}{\Delta t}\), find \(v_{final} - v_{initial}\) (triangle - 1 point, magnitude - 1 point, direction, 1 point). Then divide by the change in time (1 point)."""
    points_1 = 4
    question_1 = m.Question(content = content_1, solution = solution_1, points = points_1, course_id = course.id, tags=[tag_2])

    content_2 = """A car with mass 5200 kg and a truck wih mass 8340 kg are moving towards each other, both moving 5.1 m/s. In a completely inelastic collision, calculate the final velocity of the combined masses."""
    solution_2 = """$$m_1v - m_2v = (m_1+m_2)v_{final} \text{       (2 points)}$$
                    So

                    \[ v_{final} = v\frac{(m_1-m_2)}{(m_1+m_2)} \] (1 point)

                    \[\]
                    (1 point correct units and sig figs in final answer)"""
    points_2 = 4
    question_2 = m.Question(content = content_2, solution = solution_2, points = points_2, course_id = course.id, tags = [tag_1, tag_2])

    content_3 = """A small satellite moves through a Low Earth Orbit (LEO) of 2000 km. Jim claims in the satellite were larger it would crash into the Earth, and Jenny disagrees. Explain whether Jim is correct and justify your response with known physics. """
    solution_3 = """Since \(mv^2/r = GMm/r^2\) (1 point uniform circular motion, 1 point gravitation, 1 point setting them equal), the mass of the satellite is irrelevent (1 point) and Jim is incorrect. An orbit at this distance could be achived by any object with the correct velocity (1 point). """
    points_3 = 3
    question_3 = m.Question(content = content_3, solution = solution_3, points = points_3, course_id = course.id, tags = [tag_3])

    content_4 = """A rubber ball with mass = 0.3 kg travels towards a brick wall at 4 m/s. After bouncing, it travels back the way it came at 3 m/s. Calculate the impulse of the ball due to the wall. """
    solution_4 = """\(I = \Delta p\) So we have

                    \[I = p_f - p_i \] (1 point)

                    \[ = 0.6 kg \times (3 m/s [L] - 4 m/s [R]) \] (1 point)

                    \[ = 2.1 kg m/s [L] \] (1 point)"""
    points_4 = 3
    question_4 = m.Question(content = content_4, solution = solution_4, points = points_4, course_id = course.id, tags = [tag_2])

    questions = [question_1, question_2, question_3, question_4]

    for q in questions:
        db.session.add(q)
    db.session.commit()
    return(questions)

def add_paper(course):
    paper = m.Paper(title = 'Mechanics Quiz', course_id = course.id)
    db.session.add(paper)
    db.commit()
    return(paper)

def add_questions_to_paper(paper, questions):
    for q in questions:
        index = len(paper.paper_questions)
        pq = m.PaperQuestion(paper_id = paper.id, question_id = question.id, order_number = index+1)
        db.session.add(pq)

    db.session.commit()

def add_clazz(course):
    clazz = m.Clazz(code = 'IGPHY01', course_id = course.id)
    db.session.add(clazz)
    db.commit()
    return(clazz)

def add_admin():
    admin = m.AwsUser(user_id = 'some funky string of coolness', username = 'rtunley', group = 'admin', given_name = 'Robin', family_name = 'Tunley', email = 'robin.tunley@gmail.com')

    db.session.add(admin)
    db.session.commit()

def make_userid(given_name, family_name, index):
    user_id = given_name + family_name + index
    return user_id

def make_email(userid):
    email = userid+'@schoolofrock.com'
    return email

def add_students_and_aws_users(course):
    index = 1000
    clazz = m.Clazz.query.filter_by(course_id = course.id).first()
    user_tuples = [('Jimmy', 'Knuckle'), ('AyAyRon', 'Dinglebop'), ('Beefy', 'Taco'), ('Chaneese', 'Spankle'), ('Bobbins', 'Wiremack'), ('Ranger', 'Gilespie'), ('Django', 'Meathead')]
    student_list = []

    for i in range(len(user_tuples)):
        given = user_tuples[i][0]
        family = user_tuples[i][1]
        userid = make_userid(given, family, index+i)
        email = make_email(userid)
        aws_user = m.AwsUser(given_name = given, family_name = family, id = index, user_id = userid, email = email, group = 'student', username = userid)
        student = m.Student(aws_user = aws_user, clazzes = [clazz])
        student_list.append(student)
        db.session.add(student)

    db.session.commit()
    return(student_list)

def add_scores(paper, student_list):
    #total points on mechanics quiz is 14 so need a selection of 7 score_tuples than cover several grades. Total avilable points are (4,4,3,3).
    score_tuples = [(0,0,0,0), (1,1,1,0), (2,1,1,1), (2,1,2,2), (4,0,3,2), (2,4,2,3), (4,4,3,3)]
    for i in range(len(student_list)):
        for j in range(len(paper.paper_questions)):
            question_id = paper.paper_questions[j].question.id
            student_id = student_list[i].id
            new_score = m.Score(value = score_tuples[i][j], paper_id = paper.id, question_id = question_id, student_id = student_id)
            db.session.add(new_score)

    db.session.commit()
