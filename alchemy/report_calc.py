def total_score(score_list):
    total = 0
    for score in score_list:
        total += score.value
        print(total)

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
