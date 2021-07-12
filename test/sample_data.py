from alchemy import models as m

test_account = m.Account(name = "Test School")

test_course1 = m.Course(name = "Test Course 1", account = test_account)

#Grades for Test Course 1
grade_A = m.GradeLevel(grade = 'A', lower_bound = 85, upper_bound = 100, course_id = test_course1.id)
grade_B = m.GradeLevel(grade = 'B', lower_bound = 70, upper_bound = 85, course_id = test_course1.id)
grade_C = m.GradeLevel(grade = 'C', lower_bound = 50, upper_bound = 70, course_id = test_course1.id)
grade_D = m.GradeLevel(grade = 'D', lower_bound = 30, upper_bound = 50, course_id = test_course1.id)
grade_F = m.GradeLevel(grade = 'F', lower_bound = 30, upper_bound = 0, course_id = test_course1.id)

course1_grades = [grade_A, grade_B, grade_C, grade_D, grade_F]

test_question1 = m.Question(content = 'Not Very Challenging', solution = 'Simple Solution', points = 4, course_id = test_course1.id)
test_question2 = m.Question(content = 'Very Challenging', solution = 'Difficult Solution', points = 2, course_id = test_course1.id)

test_tag1 = m.Tag(name = "Familiar", course_id = test_course1.id)
test_tag2 = m.Tag(name = "Explanation", course_id = test_course1.id)

test_paper1 = m.Paper(title = "A Very Short Quiz", course_id = test_course1.id)
