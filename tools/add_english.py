'''
Populates the Alchemy database with dummy data for the English Department based on the parameters set in tools.populate

Run this from the root alchemy directory:
    python -m tools.add_english
'''

from alchemy import db
from tools import db_data
from alchemy import models as m

def add_questions_and_tags(course):

    tag1 = m.Tag(name = 'Reading Comprehension', course_id = course.id)
    tag2 = m.Tag(name = 'Grammar', course_id = course.id)
    tag3 = m.Tag(name = 'Writing', course_id = course.id)

    tags = [tag1, tag2, tag3]
    for tag in tags:
        db.session.add(tag)
    db.session.commit()

    oa_content_1 = "Write a letter in 250 words to a landlord convincing them to let you rent their apartment for less than their asking price."
    oa_solution_1 = m.Solution(content = "2 points - formal language and tone, 2 points - grammar, 2 points - correct letter format, 2 points - convincing arguments.")
    oa_points_1 = 10
    oa_question_1 = m.Question.create(content = oa_content_1, all_solutions = [oa_solution_1], points = oa_points_1, course_id = course.id, tags = [tag3, tag2])

    oa_content_2 = "Choose one poem studied in class and provide and briefly explain an example for three of the following five literary devices: 1) Alliteration 2) Foreshadowing 3) Metaphor 4) Symbolism 5) Irony"
    oa_solution_2 = m.Solution(content = "For each of the three devices: 1 point for the example and 1 point for the explanation. ")
    oa_points_2 = 6
    oa_question_2 = m.Question.create(content = oa_content_2, all_solutions = [oa_solution_2], points = oa_points_2, course_id = course.id, tags = [tag1])

    oa_content_3 = "Compare and contrast two of the novels studied in class in a 500 word essay, focused on social justice."
    oa_solution_3 = m.Solution(content = "5 points - correct essay structure, 5 points - examples from both selected novels are used as evidence, 5 points - grammar and spelling, 5 points - relevance to social justice")
    oa_points_3 = 20
    oa_question_3 = m.Question.create(content = oa_content_3, all_solutions = [oa_solution_3], points = oa_points_3, course_id = course.id, tags = [tag1, tag3, tag2])

    oa_content_4 = """Read the following passage and answer the question below:

                        Robin Tunley is the greatest english teacher the world has ever seen. Remarkably, he has no qualifications of any sort in this field. Students praise his clarity and colleagues admire his technique. They say that his secret is that he sold his soul to the Devil for his immense talent, and will live out a joyless life despite the incredible success that he has achieved.

                    Explain in your own words the irony of Mr Tunley's situation. """
    oa_solution_4 = m.Solution(content = "1 point - includes a definition of irony, 1 point - majority of writing is alternate wording, 2 point - comprehension is evident in explanation")
    oa_points_4 = 4
    oa_question_4 = m.Question.create(content = oa_content_4, all_solutions = [oa_solution_4], points = oa_points_4, course_id = course.id, tags = [tag1, tag3])

    questions = [oa_question_1, oa_question_2, oa_question_3, oa_question_4]
    for question in questions:
        db.session.add(question)

    db.session.commit()
    return(questions)

def add_english():
    # Danger!! Hard coded ID's might break if changes are made to tools.populate!
    department_id = 3
    course_id = 3
    course = m.Course.query.get(course_id)
    all_questions = add_questions_and_tags(course)
    first_exam = m.Paper.query.filter_by(course_id = course.id, id = 7).first()
    first_test = m.Paper.query.filter_by(course_id = course.id, id = 6).first()
    db_data.add_questions_to_paper(first_test, [all_questions[0], all_questions[3]])
    db_data.add_questions_to_paper(first_exam, [all_questions[1], all_questions[2], all_questions[3]])
    # scores for all the students in each clazz
    for clazz in course.clazzes:
        db_data.add_scores(first_test, clazz.students)
        db_data.add_scores(first_exam, clazz.students)


    print("DONE!!")

if __name__ == '__main__':
    add_english()
