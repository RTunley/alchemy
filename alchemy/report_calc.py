## A selection of functions that will required for multuple report sections, and probably used to profiles as well.

class AdjacentGrades(object):
    def __init__(self, higher_grade, diff_higher_grade, lower_grade, diff_lower_grade):
        self.next_highest_grade = higher_grade
        self.diff_higher_grade = diff_higher_grade
        self.next_lowest_grade = lower_grade
        self.diff_lower_grade = diff_lower_grade

def total_score(score_list):
    total = 0
    for score in score_list:
        total += score.value
    return total

def calc_percentage(value, total):
    percentage = round(value/total*100, 2)
    return percentage

def determine_grade(percentage, course):
    grade_levels = course.grade_levels
    for i in range(len(grade_levels)):
        if i == 0:
            if percentage >= grade_levels[i].lower_bound:
                new_grade = grade_levels[i].grade
        elif percentage >= grade_levels[i].lower_bound and percentage < grade_levels[i].upper_bound:
            new_grade = grade_levels[i].grade
    return new_grade

def get_adjacent_grades(grade_list, percentage, grade):
    for i in range(len(grade_list)):
        if grade_list[i].grade == grade:
            index = i

    if index == 0:
        next_lowest_grade = grade_list[index+1]
        diff_lower_grade = round(percentage - next_lowest_grade.upper_bound, 1)
        next_highest_grade = None
        diff_higher_grade = None

    elif index == len(grade_list)-1:
        next_highest_grade = grade_list[index-1]
        diff_higher_grade = round(next_highest_grade.lower_bound - percentage, 1)
        next_lowest_grade = None
        diff_lower_grade = None

    else:
        next_highest_grade = grade_list[index-1]
        diff_higher_grade = round(next_highest_grade.lower_bound - percentage, 1)
        next_lowest_grade = grade_list[index+1]
        diff_lower_grade = round(percentage - next_lowest_grade.upper_bound, 1)

    adjacent_grades = AdjacentGrades(next_highest_grade, diff_higher_grade, next_lowest_grade, diff_lower_grade)
    return adjacent_grades
