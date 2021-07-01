from sam import score_manager

class StudentCourseProfile(object):
    def __init__(self, student, scoreset_list):
        self.student = student
        self.scoreset_list = scoreset_list

def make_student_course_profile(student, course):
    scoreset_list = []
    for p in course.papers:
        if len(p.paper_questions) != 0:
            student_paper_scoreset = score_manager.make_student_paper_scoreset(student, p)
            scoreset_list.append(student_paper_scoreset)

    student_profile = StudentCourseProfile(student, scoreset_list)
    return student_profile
