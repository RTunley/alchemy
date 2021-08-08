import numpy as np

## Data organisation classes

class StudentPaperSummary(object):
    def __init__(self, student, paper, scores):
        self.scores = scores
        self.paper_total = 0
        self.raw_total = 0
        self.percent_total = 0
        self.grade = None
        self.build_self(student, paper, scores)

    def build_self(self, student, paper, scores):
        self.paper_total = paper.profile.total_points
        self.raw_total = total_score(scores)
        self.percent_total = calc_percentage(self.raw_total, self.paper_total)
        self.grade = determine_grade(self.percent_total, paper.course)

class AdjacentGrades(object):
    def __init__(self, grade_list, percentage, grade, paper_total):
        self.higher_grade = None
        self.diff_higher_grade = 0
        self.raw_diff_higher_grade = 0
        self.lower_grade = None
        self.diff_lower_grade = 0
        self.raw_diff_lower_grade = 0
        self.build_self(grade_list, percentage, grade, paper_total)

    def build_self(self, grade_list, percentage, grade, paper_total):
        for i in range(len(grade_list)):
            if grade_list[i].grade == grade:
                index = i
                break
        if index == 0:
            self.lower_grade = grade_list[index+1]
            self.diff_lower_grade = round(percentage - self.lower_grade.upper_bound, 1)
            self.higher_grade = None
            self.diff_higher_grade = None
        elif index == len(grade_list)-1:
            self.higher_grade = grade_list[index-1]
            self.diff_higher_grade = round(self.higher_grade.lower_bound - percentage, 1)
            self.lower_grade = None
            self.diff_lower_grade = None
        else:
            self.higher_grade = grade_list[index-1]
            self.diff_higher_grade = round(self.higher_grade.lower_bound - percentage, 1)
            self.lower_grade = grade_list[index+1]
            self.diff_lower_grade = round(percentage - self.lower_grade.upper_bound, 1)
        if self.higher_grade:
            self.raw_diff_higher_grade = round(self.diff_higher_grade*paper_total/100, 1)
        else:
            self.raw_diff_higher_grade = None
        if self.lower_grade:
            self.raw_diff_lower_grade = round(self.diff_lower_grade*paper_total/100, 1)
        else:
            self.raw_diff_lower_grade = None

class CohortPaperSummary(object):
    def __init__(self, paper, cohort_scores):
        self.paper_total = paper.profile.total_points
        self.raw_mean = 0
        self.percent_mean = 0
        self.mean_grade = None
        self.build_self(paper, cohort_scores)

    def build_self(self, paper, cohort_scores):
        student_summaries = build_student_summaries(paper, cohort_scores)
        self.raw_mean = calc_mean([summary.raw_total for summary in student_summaries])
        self.percent_mean = calc_percentage(self.raw_mean, self.paper_total)
        self.mean_grade = determine_grade(self.percent_mean, paper.course)


## A selection of functions that will required for multuple report sections, and probably used to profiles as well.

def total_score(score_list):
    return sum(score.value for score in score_list)

def calc_percentage(numerator, denominator):
    percentage = round(numerator/denominator*100, 2)
    return percentage

def determine_grade(percentage, course):
    grade_levels = course.grade_levels
    for i in range(len(grade_levels)):
        if percentage >= grade_levels[i].lower_bound:
            new_grade = grade_levels[i].grade
            break
    return new_grade

def calc_mean(values_list):
    array = np.array(values_list)
    return round(np.mean(array), 2)

def all_students_in_course(course):
    students_in_course = []
    for clazz in course.clazzes:
        for student in clazz.students:
            students_in_course.append(student)
    return students_in_course

def build_student_summaries(paper, scores):
    student_list = all_students_in_course(paper.course)
    student_summaries = []
    for student in student_list:
        student_scores = []
        for score in scores:
            if score.student_id == student.id:
                student_scores.append(score)

        student_summary = StudentPaperSummary(student, paper, student_scores)
        student_summaries.append(student_summary)

    return student_summaries
