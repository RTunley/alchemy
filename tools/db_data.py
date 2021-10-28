from alchemy import models as m
from alchemy import db

def add_account():
    account = m.Account(name = "School of Rock")
    db.session.add(account)
    db.session.commit()
    return(account)


def add_course(account, name):
    course = m.Course(name = name, account = account)
    db.session.add(course)
    db.session.commit()
    return(course)

def add_grade_levels(course):
    grade_Astar = m.GradeLevel(grade = 'A*', lower_bound = 85, upper_bound = 100, course_id = course.id)
    grade_A = m.GradeLevel(grade = 'A', lower_bound = 75, upper_bound = 85, course_id = course.id)
    grade_B = m.GradeLevel(grade = 'B', lower_bound = 65, upper_bound = 75, course_id = course.id)
    grade_C = m.GradeLevel(grade = 'C', lower_bound = 55, upper_bound = 65, course_id = course.id)
    grade_D = m.GradeLevel(grade = 'D', lower_bound = 45, upper_bound = 55, course_id = course.id)
    grade_E = m.GradeLevel(grade = 'E', lower_bound = 35, upper_bound = 45, course_id = course.id)
    grade_F = m.GradeLevel(grade = 'F', lower_bound = 25, upper_bound = 35, course_id = course.id)
    grade_G = m.GradeLevel(grade = 'G', lower_bound = 15, upper_bound = 25, course_id = course.id)
    grade_U = m.GradeLevel(grade = 'U', lower_bound = 0, upper_bound = 15, course_id = course.id)

    course_grades = [grade_Astar, grade_A, grade_B, grade_C, grade_D, grade_E, grade_F, grade_G, grade_U]

    for gl in course_grades:
        db.session.add(gl)
    db.session.commit()
    return(course_grades)

def add_questions_and_tags(course):
    tag_1 = m.Tag(name = 'Algebra', course_id = course.id)
    tag_2 = m.Tag(name = 'Calculate', course_id = course.id)
    tag_3 = m.Tag(name = 'Explain', course_id = course.id)

    tags = [tag_1, tag_2, tag_3]
    for tag in tags:
        db.session.add(tag)
    db.session.commit()

    la_content_1 = """Calculate the average acceleration of a cyclist whose velocity changes from 2.1 m/s \([S]\) to 2.5 m/s \([W]\) over 3.5 seconds. """
    la_solution_1 = m.Solution(content = """Since \(a = \\frac{\Delta v}{\Delta t}\), find \(v_{final} - v_{initial}\) (triangle - 1 point, magnitude - 1 point, direction, 1 point). Then divide by the change in time (1 point).""")
    la_points_1 = 4
    la_question_1 = m.Question.create(content = la_content_1, all_solutions = [la_solution_1], points = la_points_1, course_id = course.id, tags=[tag_2])

    la_content_2 = """A car with mass 5200 kg and a truck wih mass 8340 kg are moving towards each other, both moving 5.1 m/s. In a completely inelastic collision, calculate the final velocity of the combined masses."""
    la_solution_2 = m.Solution(content = """$$m_1v - m_2v = (m_1+m_2)v_{final} \\  \\text{(2 points)}$$
                    So

                    \[ v_{final} = v\\frac{m_1-m_2}{m_1+m_2} \\ \\text{(1 point)}\]

                    \[\]
                    (1 point correct units and sig figs in final answer)""")
    la_points_2 = 4
    la_question_2 = m.Question.create(content = la_content_2, all_solutions = [la_solution_2], points = la_points_2, course_id = course.id, tags = [tag_1, tag_2])

    la_content_3 = """A small satellite moves through a Low Earth Orbit (LEO) of 2000 km. Jim claims in the satellite were larger it would crash into the Earth, and Jenny disagrees. Explain whether Jim is correct and justify your response with known physics. """
    la_solution_3 = m.Solution(content = """Since \(mv^2/r = GMm/r^2\) (1 point uniform circular motion, 1 point gravitation, 1 point setting them equal), the mass of the satellite is irrelevent (1 point) and Jim is incorrect. An orbit at this distance could be achived by any object with the correct velocity (1 point). """)
    la_points_3 = 3
    la_question_3 = m.Question.create(content = la_content_3, all_solutions = [la_solution_3], points = la_points_3, course_id = course.id, tags = [tag_3])

    la_content_4 = """A rubber ball with mass = 0.3 kg travels towards a brick wall at 4 m/s. After bouncing, it travels back the way it came at 3 m/s. Calculate the impulse of the ball due to the wall. """
    la_solution_4 = m.Solution(content = """\(I = \Delta p\) So we have

                    \[I = p_f - p_i \] (1 point)

                    \[ = 0.6 kg \\times (3 \\ m/s \\ [L] - 4 \\ m/s \\ [R]) \] (1 point)

                    \[ = 2.1 \\ kg \\ m/s \\ [L] \] (1 point)""")
    la_points_4 = 3
    la_question_4 = m.Question.create(content = la_content_4, all_solutions = [la_solution_4], points = la_points_4, course_id = course.id, tags = [tag_2])

    mc_choices_1 = [m.Solution(content=content) for content in ('\[r = (\\frac{3m}{4\pi\\rho})^{\\frac{1}{3}}\]', '\[r = \\frac{3m}{4\pi\\rho}\]', '\[r = (\\frac{4\pi\\rho}{3m})^{\\frac{1}{3}}\]', '\[r = \\frac{4\pi\\rho}{3m}\]')]
    mc_content_1 = """A sphere-shaped submarine will be used for deep sea exploration, but the engineers are unsure how large to make it. Using the volume of a sphere \(V = \\frac{4}{3}\pi r^3\), a mathematical expression for the radius which involves its density is: """
    mc_question_1 = m.Question.create(content = mc_content_1, all_solutions = mc_choices_1, correct_solution_index = 0, points = 1, course_id = course.id, tags = [tag_1])

    mc_choices_2 = [m.Solution(content=content) for content in ('3 \(m/s^2\)', '0.3 \(m/s^2\)', '0.03 \(m/s^2\)', '30 \(m/s^2\)')]
    mc_content_2 = """A woman pushes a 75 kg crate across a frictionless floor with a force of 2.5 N. The acceleration of the crate will be: """
    mc_question_2 = m.Question.create(content = mc_content_2, all_solutions = mc_choices_2, correct_solution_index = 2, points = 1, course_id = course.id, tags = [tag_2, tag_1])

    mc_choices_3 = [m.Solution(content=content) for content in ('centripetal force acting away from the center of the path', 'tension force acting toward the center of the path', 'normal force acting away from the center of the path', 'centripetal force acting toward the center of the path')]
    mc_content_3 = "An object like the moon is kept in a perfectly circular orbit because there is a: "
    mc_question_3 = m.Question.create(content = mc_content_3, all_solutions = mc_choices_3, correct_solution_index = 3, points = 1, course_id = course.id, tags = [tag_3])

    questions = [la_question_1, la_question_2, la_question_3, la_question_4, mc_question_1, mc_question_2, mc_question_3]
    for question in questions:
        db.session.add(question)

    db.session.commit()
    return(questions)

def add_paper(course):
    paper = m.Paper(title = 'Mechanics Quiz', course_id = course.id)
    db.session.add(paper)
    db.session.commit()
    return(paper)

def add_questions_to_paper(paper, questions):
    for question in questions:
        pq = paper.new_question(question)
        db.session.add(pq)

    db.session.commit()

def add_clazz(course, code):
    clazz = m.Clazz(code = code, course_id = course.id)
    db.session.add(clazz)
    db.session.commit()
    return(clazz)

def add_admin_and_aws_users():
    admin_list = []
    user_tuples = [('Robin', 'Admin'), ('Bea', 'Admin')]
    for user_tuple in user_tuples:
        given, family = user_tuple
        email = f'{given}.{family}@example.com'
        admin = m.Admin.create(given_name=given, family_name=family, email=email)
        admin_list.append(admin)
        db.session.add(admin)

    db.session.commit()
    return admin_list

def add_students_and_aws_users(clazzes):
    student_list = []
    user_tuples = [('Robin', 'Student'), ('Bea', 'Student'), ('Jimmy', 'Knuckle'), ('AyAyRon', 'Dinglebop'), ('Beefy', 'Taco'), ('Chaneese', 'Spankle'), ('Bobbins', 'Wiremack')]
    for user_tuple in user_tuples:
        given, family = user_tuple
        email = f'{given}.{family}@example.com'
        student = m.Student.create(given_name=given, family_name=family, email=email, clazzes=clazzes)
        student_list.append(student)
        db.session.add(student)

    db.session.commit()
    return student_list

def add_scores(paper, student_list):
    #total points on mechanics quiz is 14 so need a selection of 8 score_tuples than cover several grades. Total avilable points are (4,4,3,3,4).
    score_tuples = [(0,0,0,0,0,0,0), (1,1,1,0,0,1,1), (2,1,1,1,1,1,0), (2,1,2,2,1,0,1), (4,0,3,2,1,1,0), (2,4,2,3,1,0,1), (4,4,3,3,0,1,1)]
    for i in range(len(student_list)):
        for j in range(len(paper.paper_questions)):
            question_id = paper.paper_questions[j].question.id
            student_id = student_list[i].id
            new_score = m.Score(value = score_tuples[i][j], paper_id = paper.id, question_id = question_id, student_id = student_id)
            db.session.add(new_score)

    db.session.commit()
