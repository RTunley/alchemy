import numpy as np
from alchemy.reports import plots

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

class ClazzPaperSummary(object):
    def __init__(self, paper, clazz_scores):
        self.paper_total = paper.profile.total_points
        self.raw_mean = 0
        self.percent_mean = 0
        self.mean_grade = None
        self.build_self(paper, clazz_scores)

    def build_self(self, paper, clazz_scores):
        student_summaries = build_student_summaries(paper, clazz_scores)
        self.raw_mean = calc_mean([summary.raw_total for summary in student_summaries])
        self.percent_mean = calc_percentage(self.raw_mean, self.paper_total)
        self.mean_grade = determine_grade(self.percent_mean, paper.course)

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

## Strengths and Weaknesses = Highlights ##

class QuestionHighlight(object):
    def __init__(self, order_id, percentage, grade):
        self.order_id = order_id
        self.percentage = percentage
        self.grade = grade

class StudentTagAchievement(object):
    "Contains info on the tag and the student achievement on that tag in a given paper."
    def __init__(self, student, paper, tag_profile, total):
        self.student = student
        self.paper = paper
        self.tag = tag_profile.tag
        self.tag_total = tag_profile.allocated_points
        self.raw_score = total
        self.percent_score = 0
        self.grade = None
        self.build_self(tag_profile, total)

    def build_self(self, tag_profile, total):
        self.percent_score = calc_percentage(self.raw_score, self.tag_total)
        self.grade = determine_grade(self.percent_score, self.paper.course)

class QuestionHighlights(object):
    def __init__(self, student, paper, scores):
        self.strengths = []
        self.has_strengths = False
        self.weaknesses = []
        self.has_weaknesses = False
        self.build_self(student, paper, scores)

    def build_self(self, student, paper, scores):
        percent_scores = calc_percent_scores([score for score in scores])
        highest_percent = max(percent_scores)
        lowest_percent = min(percent_scores)
        if lowest_percent == 100:
            self.has_strengths = True
        elif highest_percent == 0:
            self.has_weaknesses = True
        else:
            self.has_weaknesses = True
            self.has_strengths = True
        strength_indexes = [x for x in range(len(percent_scores)) if percent_scores[x] == highest_percent]
        weakness_indexes = [x for x in range(len(percent_scores)) if percent_scores[x] == lowest_percent]
        for i in strength_indexes:
            self.strengths.append(QuestionHighlight(paper.paper_questions[i].order_number, percent_scores[i], determine_grade(percent_scores[i], paper.course)))
        for j in weakness_indexes:
            self.weaknesses.append(QuestionHighlight(paper.paper_questions[j].order_number, percent_scores[j], determine_grade(percent_scores[j], paper.course)))

class TagHighlights(object):
    def __init__(self, student, paper, scores):
        self.strengths = []
        self.weaknesses = []
        self.build_self(student, paper, scores)

    def build_self(self, student, paper, scores):
        all_student_tag_achievements = []
        for profile in paper.profile.tag_profile_list:
            student_tag_total = get_tag_total(student, profile.tag.name, paper, scores)
            student_tag_achievement = StudentTagAchievement(student, paper, profile, student_tag_total)
            all_student_tag_achievements.append(student_tag_achievement)

        all_student_tag_achievements.sort(key=lambda x: x.percent_score, reverse=True)
        for s_t_a in all_student_tag_achievements:
            if s_t_a.percent_score == all_student_tag_achievements[0].percent_score:
                self.strengths.append(s_t_a)

            elif s_t_a.percent_score == all_student_tag_achievements[-1].percent_score:
                self.weaknesses.append(s_t_a)

class StatSummary(object):
    def __init__(self, values_list):
        self.value_list = values_list
        self.mean = 0
        self.sd = 0
        self.fivenumsumm = []
        self.build_self()

    def build_self(self):
        array = np.array(self.value_list)
        self.mean = round(np.mean(array), 2)
        self.sd = round(np.std(array), 2)
        min = array.min()
        max = array.max()
        quartiles = np.percentile(array, [25, 50, 75], interpolation = 'midpoint')
        self.fivenumsumm = [round(min,2), round(quartiles[0],2), round(quartiles[1],2), round(quartiles[2],2), round(max,2)]

class NormStatSumm(StatSummary):
    def __init__(self, statsumm, total):
        self.statsumm = statsumm
        self.value_list = []
        self.total = total
        self.mean = round(statsumm.mean/total*100, 2)
        self.sd = round(statsumm.sd/total*100, 2)
        self.fivenumsumm = []
        self.normalize_fivenumsumm()
        self.normalize_value_list()

    def normalize_fivenumsumm(self):
        for value in self.statsumm.fivenumsumm:
            self.fivenumsumm.append(round(value/self.total*100, 2))

    def normalize_value_list(self):
        self.value_list = [calc_percentage(value, self.total) for value in self.statsumm.value_list]

## A selection of functions that will required for multuple report sections, and probably used to build profiles as well.

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

def calc_percent_scores(scores):
    percent_scores = []
    for score in scores:
        percent_scores.append(round(score.value/score.question.points*100, 2))

    return percent_scores

def filter_questions_by_tag(question_assoc_list, tag_string):
    question_id_list = []
    for question_assoc in question_assoc_list:
        for tag in question_assoc.question.tags:
            if tag.name == tag_string:
                question_id_list.append(question_assoc.question.id)

    return(question_id_list)

def get_tag_total(student, tag_string, paper, scores):
    tag_total = 0
    question_id_list = filter_questions_by_tag(paper.paper_questions, tag_string)
    for score in scores:
        if score.question_id in question_id_list:
            tag_total += score.value

    return tag_total

def filter_scores_by_clazz(scores, clazz):
    student_ids = [student.id for student in clazz.students]
    clazz_scores = []
    for score in scores:
        if score.student_id in student_ids:
            clazz_scores.append(score)

    return clazz_scores

## Functions for interacting with reports.plots ##

def create_distribution_plot(clazz, paper, scores):
    student_summaries = build_student_summaries(paper, scores)
    clazz_statsumm = StatSummary([summary.raw_total for summary in student_summaries])
    clazz_norm_statsumm = NormStatSumm(clazz_statsumm, paper.profile.total_points)
    print('Norm Statsumm value_list: ', clazz_norm_statsumm.value_list)
    plot_data = plots.create_distribution_plot(clazz_norm_statsumm.value_list, clazz_norm_statsumm.sd, clazz_norm_statsumm.mean, 'Distribution of Overall Achievement', False, None)
    return plot_data
