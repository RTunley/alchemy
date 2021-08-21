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

class QuestionHighlightSets(object):
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

class TagHighlightSets(object):
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

class StatProfile(object):
    def __init__(self, values_list, total):
        self.raw_values_list = values_list
        self.total = total
        self.object = None
        self.norm_values_list = []
        self.raw_mean = 0
        self.norm_mean = 0
        self.raw_sd = 0
        self.norm_sd = 0
        self.raw_fivenumsumm = []
        self.norm_fivenumsumm = []
        self.raw_iqr = 0
        self.norm_iqr = 0
        self.build_self()

    def build_self(self):
        self.norm_values_list = [calc_percentage(value, self.total) for value in self.raw_values_list]
        raw_array = np.array(self.raw_values_list)
        self.raw_mean = round(np.mean(raw_array), 2)
        self.raw_sd = round(np.std(raw_array), 2)
        raw_min = raw_array.min()
        raw_max = raw_array.max()
        raw_quartiles = np.percentile(raw_array, [25, 50, 75], interpolation = 'midpoint')
        self.raw_fivenumsumm = [round(raw_min,2), round(raw_quartiles[0],2), round(raw_quartiles[1],2), round(raw_quartiles[2],2), round(raw_max,2)]
        self.raw_iqr = self.raw_fivenumsumm[3] - self.raw_fivenumsumm[1]

        norm_array = np.array(self.norm_values_list)
        self.norm_mean = round(self.raw_mean/self.total*100, 2)
        self.norm_sd = round(self.raw_sd/self.total*100, 2)
        self.norm_fivenumsumm = [round(value/self.total*100, 2) for value in self.raw_fivenumsumm]
        self.norm_iqr = self.norm_fivenumsumm[3] - self.norm_fivenumsumm[1]

    @staticmethod
    def from_tag(values_list, total, tag):
        statprofile = StatProfile(values_list, total)
        statprofile.object = tag
        return statprofile

    @staticmethod
    def from_question(values_list, total, paper_question):
        statprofile = StatProfile(values_list, total)
        statprofile.object = paper_question
        return statprofile

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

def make_tag_statprofile_list(clazz, paper):
    tag_statprofile_list = []
    for tag_profile in paper.profile.tag_profile_list:
        raw_totals = []
        for student in clazz.students:
            scores = models.Score.query.filter_by(student_id = student.id, paper_id = paper.id).all()
            tag_total = get_tag_total(student, tag_profile.name, paper, scores)
            raw_totals.append(tag_total)
        tag_statprofile = StatProfile.from_tag(raw_totals, tag_profile.allocated_points, tag_profile.tag)
        tag_statprofile_list.append(tag_statprofile)
    return tag_statprofile_list

def make_question_statprofile_list(clazz, paper):
    question_statprofile_list = []
    for pq in paper.paper_questions:
        scores = models.Score.query.filter_by(paper_id = paper.id, question_id = pq.question.id).all()
        raw_totals = [score.value for score in scores]
        question_statprofile = StatProfile.from_question(raw_totals, pq.question.points, pq)
        question_statprofile_list.append(question_statprofile)
    return question_statprofile_list

## Functions for interacting with reports.plots ##

def create_clazz_distribution_plot(clazz, paper):
    clazz_statprofile = StatProfile(total_student_scores_for_clazz(clazz, paper), paper.profile.total_points)
    plot_data = plots.create_distribution_plot(clazz_statprofile.norm_values_list, clazz_statprofile.norm_sd, clazz_statprofile.norm_mean, 'Distribution of Overall Achievement', False, None)
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

def make_comparison_charts(statprofile_list):
    means = []
    medians = []
    sd_list = []
    iqr_list = []
    labels = []
    for statprofile in statprofile_list:
        means.append(statprofile.norm_mean)
        medians.append(statprofile.norm_fivenumsumm[2])
        sd_list.append(statprofile.norm_sd)
        iqr_list.append(statprofile.norm_iqr)
        if isinstance(statprofile.object, models.Tag):
            labels.append(statprofile.object.name)
        elif isinstance(statprofile_list[0].object, models.PaperQuestion):
            labels.append(statprofile.object.order_number)

    if isinstance(statprofile.object, models.Tag):
        center_title = 'Tag Comparison: Central Tendency'
        spread_title = 'Tag Comparison: Spread'
        x_axis = None
    elif isinstance(statprofile_list[0].object, models.PaperQuestion):
        center_title = 'Question Comparison: Central Tendency'
        spread_title = 'Question Comparison: Spread'
        x_axis = 'Question Number'

    center_bar_plot = plots.create_comparative_bar_chart(center_title, means, 'Mean', medians, 'Median', labels, x_axis)
    spread_bar_plot = plots.create_comparative_bar_chart(spread_title, sd_list, 'Standard Deviation', iqr_list, 'Interquartile Range', labels, x_axis)
    return (center_bar_plot, spread_bar_plot)

def make_achievement_plots(statprofile_list):
    tag_plot_list = []
    for statprofile in statprofile_list:
        if isinstance(statprofile.object, models.Tag):
            title = f"{statprofile.object.name} - Achievement Distribution"
        elif isinstance(statprofile.object, models.PaperQuestion):
            title = f"Question {statprofile.object.order_number} - Achievement Distribution"
        plot_data = plots.create_distribution_plot(statprofile.norm_values_list, statprofile.norm_sd, statprofile.norm_mean, title, False, None)
        tag_plot_list.append(plot_data)

    return tag_plot_list
