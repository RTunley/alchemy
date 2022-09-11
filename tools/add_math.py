'''
Populates the Alchemy database with dummy data for the Mathematics Department based on the parameters set in tools.populate

Run this from the root alchemy directory:
    python -m tools.add_math
'''

from alchemy import db
from alchemy import models as m
from tools import db_data

# Tags & Questions

def add_questions_and_tags(course):

    tag1 = m.Tag(name = 'Algebra', course_id = course.id)
    tag2 = m.Tag(name = 'Geometry', course_id = course.id)
    tag3 = m.Tag(name = 'Functions', course_id = course.id)

    tags = [tag1, tag2, tag3]
    for tag in tags:
        db.session.add(tag)
    db.session.commit()

    oa_content_1 = "The volume of a cyinder is 100 cm^3. If its length is 15 cm, determine its radius. Then, find the surface area of this cylinder."
    oa_solution_1 = m.Solution(content = "Use the volume formula (1 point) to solve for r^2 (1 point) and then r (1 point) to obtain r = 0.014 cm (1 point). Then, use the SA forula (1 point) to find SA = 1.32 cm^2 (1)")
    oa_points_1 = 5
    oa_question_1 = m.Question.create(content = oa_content_1, all_solutions = [oa_solution_1], points = oa_points_1, course_id = course.id, tags = [tag1, tag2])

    oa_content_2 = "Determine the roots and the apex of the parabola \(-2x^2 + 4x -12 = 0 \)."
    oa_solution_2 = m.Solution(content ="Use the quadratic equation (1 point) to determine the roots are x = 6 and x = -2. (1 point each). The apex will be found at the geometric average of the roots x = 2 (1 point). Substitue this into the original formula (1 point) to obtain y = -16 (1 point)")
    oa_points_2 = 6
    oa_question_2 = m.Question.create(content = oa_content_2, all_solutions = [oa_solution_2], points = oa_points_2, course_id  = course.id, tags = [tag1, tag3])

    mc_content_1 = """Which of the following quadratic equations describes a parabola with a global maximum: """
    mc_choices_1 = [m.Solution(content=content) for content in ('\[f(x) = \frac{x^2}{6} - 2x +9\]', '\[f(x) = -5x^2 + 5x + 10\]', '\[f(x) = 6x^2 - \frac{2x}{7} + 3\]', '\[f(x) = x^2 - 3x + \frac{5}{17}\]')]
    mc_question_1 = m.Question.create(content = mc_content_1, all_solutions = mc_choices_1, correct_solution_index = 1, points = 1, course_id = course.id, tags = [tag3])

    mc_content_2 = """A sphere of diameter s is half embedded in a cube with side length s. An expression for the surface area of this combined shape would be: """
    mc_choices_2 = [m.Solution(content=content) for content in ('\[SA = s^2(\pi + 5)\]', '\[SA = s^3\(5 + \frac{\pi}{2}\)\]', '\[SA = s^2\(5 - \frac{\pi}{2}\) \]', '\[SA = s^2\(5 + \frac{\pi}{2}\) \]')]
    mc_question_2 = m.Question.create(content = mc_content_2, all_solutions = mc_choices_2, correct_solution_index = 3, points = 1, course_id = course.id, tags = [tag1, tag2])

    mc_content_3 = """Which of the below graphs represents the equation \[ y/3 - x/3 = 3 \]"""
    mc_choices_3 = [m.Solution(content=content) for content in ('<picture 1>', '<picture 2>', '<picture 3>', '<picture 4>')]
    mc_question_3 = m.Question.create(content = mc_content_3, all_solutions = mc_choices_3, correct_solution_index = 0, points = 1, course_id = course.id, tags = [tag3])

    questions = [oa_question_1, oa_question_2, mc_question_1, mc_question_2, mc_question_3]
    for question in questions:
        db.session.add(question)

    db.session.commit()
    return(questions)

def add_math():
    # Danger!! Hard coded ID's might break if changes are made to tools.populate!
    department_id = 2
    course_id = 2
    course = m.Course.query.get(course_id)
    all_questions = add_questions_and_tags(course)
    mc_questions = db_data.get_mc_questions(all_questions)
    oa_questions = db_data.get_oa_questions(all_questions)
    # Danger!! Hardcoded Paper IDs!!
    first_exam = m.Paper.query.filter_by(course_id = course.id, id = 4).first()
    first_test = m.Paper.query.filter_by(course_id = course.id, id = 5).first()
    db_data.add_questions_to_paper(first_test, mc_questions)
    db_data.add_questions_to_paper(first_exam, all_questions)
    # scores for all the students in each clazz
    for clazz in course.clazzes:
        db_data.add_scores(first_test, clazz.students)
        db_data.add_scores(first_exam, clazz.students)

    print("DONE!!")

if __name__ == '__main__':
    add_math()
