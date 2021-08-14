import numpy as np
import sqlalchemy
from alchemy import models, db
from alchemy.reports import plots

## Data organisation classes

class PaperScoreTally(object):
    def __init__(self, student, paper, score):
        self.student = student
        self.paper_total = paper.profile.total_points
        self.raw_total = score
        self.percent_total = calc_percentage(self.raw_total, self.paper_total)
        self.grade = determine_grade(self.percent_total, paper.course)

    @staticmethod
    def from_student(student, paper):
        scores = models.Score.query.filter_by(student_id = student.id, paper_id = paper.id).all()
        return PaperScoreTally(student, paper, total_score(scores))

class PaperMultiScoreTally(object):
    def __init__(self, paper, score_list):
        self.paper_total = paper.profile.total_points
        self.raw_mean = calc_mean(score_list)
        self.percent_mean = calc_percentage(self.raw_mean, self.paper_total)
        self.mean_grade = determine_grade(self.percent_mean, paper.course)

    @staticmethod
    def from_clazz(clazz, paper):
        clazz_student_totals = total_student_scores_for_clazz(clazz, paper)
        return PaperMultiScoreTally(paper, clazz_student_totals)

    @staticmethod
    def from_cohort(paper):
        cohort_student_totals = total_student_scores_for_cohort(paper)
        return PaperMultiScoreTally(paper, cohort_student_totals)

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
        self.iqr = 0
        self.build_self()

    def build_self(self):
        array = np.array(self.value_list)
        self.mean = round(np.mean(array), 2)
        self.sd = round(np.std(array), 2)
        min = array.min()
        max = array.max()
        quartiles = np.percentile(array, [25, 50, 75], interpolation = 'midpoint')
        self.fivenumsumm = [round(min,2), round(quartiles[0],2), round(quartiles[1],2), round(quartiles[2],2), round(max,2)]
        self.iqr = self.fivenumsumm[3] - self.fivenumsumm[1]

class NormStatSumm(StatSummary):
    def __init__(self, statsumm, total):
        self.statsumm = statsumm ## TODO possibly don't need this....
        self.value_list = []
        self.total = total
        self.mean = round(statsumm.mean/total*100, 2)
        self.sd = round(statsumm.sd/total*100, 2)
        self.fivenumsumm = []
        self.normalize_fivenumsumm()
        self.normalize_value_list()
        self.iqr = self.fivenumsumm[3] - self.fivenumsumm[1]

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

def total_student_scores_for_clazz(clazz, paper):
    clazz_student_ids = [student.id for student in clazz.students]
    clazz_student_totals = []
    # Query for the summed value of all scores for each students from this class for this paper
    total_student_scores = db.session.query(
            models.Score.student_id,
            sqlalchemy.func.sum(models.Score.value).label('total_student_score')
        ).filter_by(paper_id = paper.id
        ).filter(models.Score.student_id.in_(clazz_student_ids)
        ).group_by(models.Score.student_id
        ).all()
    clazz_student_totals = []
    for student_total in total_student_scores:
        clazz_student_totals.append(student_total.total_student_score)
    return clazz_student_totals

def total_student_scores_for_cohort(paper):
    # Query for the summed value of all scores for each student for this paper
    total_student_scores = db.session.query(
            models.Score.student_id,
            sqlalchemy.func.sum(models.Score.value).label('total_student_score')
        ).filter_by(paper_id = paper.id
        ).group_by(models.Score.student_id
        ).all()
    cohort_student_totals = []
    for student_total in total_student_scores:
        cohort_student_totals.append(student_total.total_student_score)
    return cohort_student_totals

def make_student_grade_dict(student_tallies, course):
    student_grade_dict = {}
    for grade_level in course.grade_levels:
        grade_batch = []
        for tally in student_tallies:
            if tally.grade == grade_level.grade:
                grade_batch.append(tally)
        student_grade_dict[grade_level.grade] = grade_batch

    for level in student_grade_dict:
        student_grade_dict[level].sort(key=lambda x: x.percent_total, reverse=True)

    return student_grade_dict

## Functions for interacting with reports.plots ##

def create_distribution_plot(clazz, paper):
    clazz_statsumm = StatSummary(total_student_scores_for_clazz(clazz, paper))
    clazz_norm_statsumm = NormStatSumm(clazz_statsumm, paper.profile.total_points)
    print('Norm Statsumm value_list: ', clazz_norm_statsumm.value_list)
    plot_data = plots.create_distribution_plot(clazz_norm_statsumm.value_list, clazz_norm_statsumm.sd, clazz_norm_statsumm.mean, 'Distribution of Overall Achievement', False, None)
    return plot_data

def make_grade_pie_data(student_grade_dict):
    slices = []
    labels = []
    for k,v in student_grade_dict.items():
        label = ''
        if len(v) == 1:
            label = k + ' (1 Student)'
        elif len(v) == 0:
            label = k + ' (None)'
        else:
            label = k + ' ({} Students)'.format(len(v))

        labels.append(label)
        slices.append(len(v))

    slices.reverse()
    labels.reverse()
    grade_pie_data = plots.create_pie_chart('Grade Level Distribution', slices, labels)
    return grade_pie_data

def make_tag_comparison_charts(clazz, paper):
    means = []
    medians = []
    sd_list = []
    iqr_list = []
    labels = []

    for profile in paper.profile.tag_profile_list:
        raw_totals = []
        for student in clazz.students:
            scores = models.Score.query.filter_by(student_id = student.id, paper_id = paper.id).all()
            tag_total = get_tag_total(student, profile.name, paper, scores)
            raw_totals.append(tag_total)
        tag_statsumm = StatSummary(raw_totals)
        norm_tag_statsumm = NormStatSumm(tag_statsumm, profile.allocated_points)
        means.append(norm_tag_statsumm.mean)
        medians.append(norm_tag_statsumm.fivenumsumm[2])
        sd_list.append(norm_tag_statsumm.sd)
        iqr_list.append(norm_tag_statsumm.iqr)
        labels.append(profile.name)

    tag_center_bar_plot = plots.create_comparative_bar_chart('Tag Comparison: Central Tendency', means, 'Mean', medians, 'Median', labels, 'Tag')
    tag_spread_bar_plot = plots.create_comparative_bar_chart('Tag Comparison: Spread', sd_list, 'Standard Deviation', iqr_list, 'Interquartile Range', labels, 'Tag')
    return (tag_center_bar_plot, tag_spread_bar_plot)


# def make_tag_comparison_charts(self):
#     means = []
#     medians = []
#     sd_list = []
#     iq_range_list = []
#     labels = []
#     for totalset in self.tag_totalsets:
#         means.append(totalset.norm_statsumm.mean)
#         medians.append(totalset.norm_statsumm.fivenumsumm[2])
#         sd_list.append(totalset.norm_statsumm.sd)
#         iq_range = totalset.norm_statsumm.fivenumsumm[3] - totalset.norm_statsumm.fivenumsumm[1]
#         iq_range_list.append(iq_range)
#         labels.append(totalset.tag.name)
#
#         self.tag_center_bar = plots.create_comparative_bar_chart('Tag Comparison: Central Tendency', means, 'Mean', medians, 'Median', labels, 'Tag')
#         self.tag_spread_bar = plots.create_comparative_bar_chart('Tag Comparison: Spread', sd_list, 'Standard Deviation', iq_range_list, 'Interquartile Range', labels, 'Tag')
