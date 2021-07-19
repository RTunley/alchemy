import numpy as np
from alchemy import models, plots

def make_student_paper_scoreset(student, paper):
    score_list = []
    for paper_question in paper.ordered_paper_questions():
        score = models.Score.query.filter_by(paper_id = paper.id, student_id = student.id, question_id = paper_question.question_id).first()
        if not score:
            score = None

        score_list.append(score)
    student_scoreset = StudentScoreSet(student, score_list, paper)
    return student_scoreset

def make_student_scoreset_list(clazz, paper):
    score_set_list = []
    for s in clazz.students:
        new_student_set = make_student_paper_scoreset(s, paper)
        score_set_list.append(new_student_set)

    return score_set_list

def make_question_scoreset_list(clazz, paper):
    score_set_list = []
    for paper_question in paper.paper_questions:
        score_list = ordered_paper_score_list(paper, models.Score.query.filter_by(paper_id = paper.id, question_id = paper_question.question.id).all())
        for s in score_list:
            student = models.Student.query.filter_by(id = s.student_id).first()
            clazz_codes = []
            for c in student.clazzes:
                clazz_codes.append(c.code)

            if clazz.code not in clazz_codes:
                score_list.remove(s)

        new_question_set = QuestionScoreSet(paper_question, score_list)
        score_set_list.append(new_question_set)

    return score_set_list

def get_tag_profile(tag, paper):
    for tp in paper.profile.tag_profile_list:
        if tp.tag.name == tag.Name:
            return tp

def get_grade_index(grade_list, grade):
    for i in range(len(grade_list)):
        if grade_list[i].grade == grade:
            return i

def filter_questions_by_tag(question_assoc_list, tag_string):
    question_id_list = []
    for q in question_assoc_list:
        for t in q.question.tags:
            if t.name == tag_string:
                question_id_list.append(q.question.id)

    return(question_id_list)

def get_user_tag_total(student, tag_string, paper):
    scores = models.Score.query.filter_by(paper_id = paper.id, student_id = student.id).all()
    tag_total = 0
    question_id_list = filter_questions_by_tag(paper.paper_questions, tag_string)
    for s in scores:
        if s.question_id in question_id_list:
            tag_total += s.value

    return tag_total

def make_tag_totalset_list(clazz, paper):
    tag_totalset_list = []
    for tp in paper.profile.tag_profile_list:
        tag_totals = []
        for s in clazz.students:
            student_tag_total = get_user_tag_total(s, tp.name, paper)
            tag_totals.append(student_tag_total)

        new_tag_totalset = TagTotalSet(tp.tag, tag_totals, tp.allocated_points)
        tag_totalset_list.append(new_tag_totalset)
    return tag_totalset_list

def filter_student_scoresets_by_grade(student_scoreset_list, grade_levels):
    grade_batch_dict = {}
    for gl in grade_levels:
        grade_batch = []
        for s in student_scoreset_list:
            if s.grade == gl.grade:
                grade_batch.append(s)
        grade_batch_dict[gl.grade] = grade_batch

    for l in grade_batch_dict:
        grade_batch_dict[l].sort(key=lambda x: x.percentage, reverse=True)

    return grade_batch_dict

## Statistical Summaries ##

class StatSummary(object):
    def __init__(self, mean, sd, fivenumsumm):
        self.mean = mean
        self.sd = sd
        self.fivenumsumm = fivenumsumm

class NormStatSumm(StatSummary):
    def __init__(self, statsumm, total):
        self.statsumm = statsumm
        self.total = total
        self.mean = round(statsumm.mean/total*100, 2)
        self.sd = round(statsumm.sd/total*100, 2)
        self.fivenumsumm = []

    def normalize_fivenumsumm(self):
        for value in self.statsumm.fivenumsumm:
            self.fivenumsumm.append(round(value/self.total*100, 2))

def calculate_stat_summary(values_list):
    array = np.array(values_list)
    mean = round(np.mean(array), 2)
    sd = round(np.std(array), 2)
    min = array.min()
    max = array.max()
    quartiles = np.percentile(array, [25, 50, 75], interpolation = 'midpoint')
    fivenumsum = [round(min,2), round(quartiles[0],2), round(quartiles[1],2), round(quartiles[2],2), round(max,2)]
    statsumm = StatSummary(mean, sd, fivenumsum)

    return statsumm

def calculate_mean(values_list):
    array = np.array(values_list)
    mean = round(np.mean(array), 2)
    return mean

## Strengths and Weaknesses = Highlights ##

class QuestionHighlight(object):
    def __init__(self, order_id, percentage, grade):
        self.order_id = order_id
        self.percentage = percentage
        self.grade = grade

class TagHighlight(object):
    def __init__(self, tag, percentage, grade):
        self.tag = tag
        self.percentage = percentage
        self.grade = grade

def determine_grade(value, course):
    grade_levels = course.grade_levels
    for i in range(len(grade_levels)):
        if i == 0:
            if value >= grade_levels[i].lower_bound:
                new_grade = grade_levels[i].grade
        elif value >= grade_levels[i].lower_bound and value < grade_levels[i].upper_bound:
            new_grade = grade_levels[i].grade
    return new_grade

## Score Sets ##

def find_paper_question(paper_questions, question_id):
    for i, paper_question_association in enumerate(paper_questions):
        if paper_question_association.question_id == question_id:
            return i
    return -1

def ordered_paper_score_list(paper, scores):
    '''
    Orders a list of Score objects according to the question ordering for its paper.
    '''
    ordered_paper_questions = sorted(paper.paper_questions, key=lambda p: p.order_number)
    return sorted(scores, key=lambda score: find_paper_question(ordered_paper_questions, score.question_id))

class StudentScoreSet(object):
    def __init__(self, student, score_list, paper):
        self.student = student
        self.score_list = score_list
        self.paper = paper
        self.total = 0
        self.percentage = 0
        self.grade = None
        self.has_all_scores = False
        self.build_self()

    def calculate_total(self):
        for score in self.score_list:
            if score is not None and score.value is not None:
                self.total += score.value
                self.has_all_scores = True


    def calculate_percentage(self):
        paper_total = 0
        for paper_question in self.paper.paper_questions:
            paper_total += paper_question.question.points
        self.percentage = round(self.total/paper_total*100, 2)

    # def determine_grade(self):
    #     grade_levels = self.paper.course.grade_levels
    #     for gl in grade_levels:
    #         if self.percentage >= gl.lower_bound and self.percentage < gl.upper_bound:
    #             self.grade = gl.grade

    def build_self(self):
        self.calculate_total()
        self.calculate_percentage()
        self.grade = determine_grade(self.percentage, self.paper.course)

class QuestionScoreSet(object):
    def __init__(self, paper_question, scores_list):
        self.paper_question = paper_question
        self.question = self.paper_question.question
        self.order_number = self.paper_question.order_number
        self.scores_list = scores_list
        self.values_list = []
        self.percentages_list = []
        self.raw_statsumm = None
        self.norm_statsumm = None
        self.set_plot = None
        self.build_self()

    def make_values_list(self):
        for s in self.scores_list:
            self.values_list.append(s.value)

    def make_percentages_list(self):
        for v in self.values_list:
            self.percentages_list.append(round(v/self.paper_question.question.points*100, 2))

    def make_statsumm(self):
        self.raw_statsumm = calculate_stat_summary(self.values_list)
        self.norm_statsumm = NormStatSumm(self.raw_statsumm, self.paper_question.question.points)
        self.norm_statsumm.normalize_fivenumsumm()

    def make_question_plot(self):
        title = 'Question {}: Distribution of Achievement'.format(self.order_number)
        plot_data = plots.create_distribution_plot(self.percentages_list, self.norm_statsumm.sd, self.norm_statsumm.mean, title, False, None)
        self.set_plot = plot_data

    def build_self(self):
        self.make_values_list()
        self.make_percentages_list()
        self.make_statsumm()
        self.make_question_plot()

class TagTotalSet(object):
    def __init__(self, tag, values_list, total):
        self.tag = tag
        self.total = total
        self.values_list = values_list
        self.percentages_list = []
        self.raw_statsumm = None
        self.norm_statsumm = None
        self.set_plot = None
        self.build_self()

    def make_percentages_list(self):
        for v in self.values_list:
            self.percentages_list.append(round(v/self.total*100, 2))

    def make_statsumm(self):
        self.raw_statsumm = calculate_stat_summary(self.values_list)
        self.norm_statsumm = NormStatSumm(self.raw_statsumm, self.total)
        self.norm_statsumm.normalize_fivenumsumm()

    def make_tag_plot(self):
        title = '{}: Distribution of Achievement'.format(self.tag.name)
        plot_data = plots.create_distribution_plot(self.percentages_list, self.norm_statsumm.sd, self.norm_statsumm.mean, title, False, None)
        self.set_plot = plot_data

    def build_self(self):
        self.make_percentages_list()
        self.make_statsumm()
        self.make_tag_plot()

class ClassReport(object):
    def __init__(self, paper, student_scoreset_list, tag_totalset_list, question_scoreset_list):
        self.paper = paper
        self.student_scoresets = student_scoreset_list
        self.tag_totalsets = tag_totalset_list
        self.question_scoresets = question_scoreset_list
        self.set_plot = None
        self.grade_batch_dict = None
        self.totals_list = []
        self.percentages_list = []
        self.raw_statsumm = None
        self.norm_statsumm = None
        self.grade_pie_data = None
        self.tag_center_bar = None
        self.tag_spread_bar = None
        self.question_center_bar = None
        self.question_spread_bar = None
        self.build_self()

    def make_totals_list(self):
        for s in self.student_scoresets:
            self.totals_list.append(s.total)

    def make_percentages_list(self):
        for s in self.student_scoresets:
            self.percentages_list.append(s.percentage)

    def make_statsumm_raw(self):
        self.raw_statsumm = calculate_stat_summary(self.totals_list)

    def make_statsumm_percentage(self):
        self.norm_statsumm = calculate_stat_summary(self.percentages_list)

    def make_clazz_plot(self):
        plot_data = plots.create_distribution_plot(self.percentages_list, self.norm_statsumm.sd, self.norm_statsumm.mean, 'Distribution of Overall Achievement', False, None)
        self.set_plot = plot_data

    def make_grade_batch_dict(self):
        self.grade_batch_dict = filter_student_scoresets_by_grade(self.student_scoresets, self.paper.course.grade_levels)

    def make_grade_pie_data(self):
        slices = []
        labels = []
        for k,v in self.grade_batch_dict.items():
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
        self.grade_pie_data = plots.create_pie_chart('Grade Level Distribution', slices, labels)

    def make_tag_comparison_charts(self):
        means = []
        medians = []
        sd_list = []
        iq_range_list = []
        labels = []
        for t in self.tag_totalsets:
            means.append(t.norm_statsumm.mean)
            medians.append(t.norm_statsumm.fivenumsumm[2])
            sd_list.append(t.norm_statsumm.sd)
            iq_range = t.norm_statsumm.fivenumsumm[3] - t.norm_statsumm.fivenumsumm[1]
            iq_range_list.append(iq_range)
            labels.append(t.tag.name)

        self.tag_center_bar = plots.create_comparative_bar_chart('Tag Comparison: Central Tendency', means, 'Mean', medians, 'Median', labels, 'Tag')
        self.tag_spread_bar = plots.create_comparative_bar_chart('Tag Comparison: Spread', sd_list, 'Standard Deviation', iq_range_list, 'Interquartile Range', labels, 'Tag')

    def make_question_comparison_charts(self):
        means = []
        medians = []
        sd_list = []
        iq_range_list = []
        labels = []
        for q in self.question_scoresets:
            means.append(q.norm_statsumm.mean)
            medians.append(q.norm_statsumm.fivenumsumm[2])
            sd_list.append(q.norm_statsumm.sd)
            iq_range = q.norm_statsumm.fivenumsumm[3] - q.norm_statsumm.fivenumsumm[1]
            iq_range_list.append(iq_range)
            labels.append(q.order_number)

        self.question_center_bar = plots.create_comparative_bar_chart('Question Comparison: Central Tendency', means, 'Mean', medians, 'Median', labels, 'Question Number')
        self.question_spread_bar = plots.create_comparative_bar_chart('Question Comparison: Spread', sd_list, 'Standard Deviation', iq_range_list, 'Interquartile Range', labels, 'Question Number')

    def build_self(self):
        self.make_totals_list()
        self.make_percentages_list()
        self.make_statsumm_raw()
        self.make_statsumm_percentage()
        self.make_clazz_plot()
        self.make_grade_batch_dict()
        self.make_grade_pie_data()
        self.make_tag_comparison_charts()
        self.make_question_comparison_charts()

class StudentReport(object):
    def __init__(self, student, paper, student_scoreset_list, tag_totalset_list, question_scoreset_list):
        self.student = student
        self.paper = paper
        self.student_scoresets = student_scoreset_list
        self.tag_totalsets = tag_totalset_list
        self.question_scoresets = question_scoreset_list
        self.scoreset = None
        self.total = None
        self.percentage = None
        self.grade = None
        self.next_higher_grade = None
        self.next_lower_grade = None
        self.diff_highest_grade = None
        self.diff_lowest_grade = None
        self.grade_batch_dict = None
        self.clazz_raw_mean = None
        self.clazz_percentage_mean = None
        self.clazz_mean_grade = None
        self.question_strengths = None
        self.question_weaknesses = None
        self.tag_strengths = None
        self.tag_weaknesses = None
        self.build_self()

    def get_totals_and_grade(self):
        for s in self.student_scoresets:
            if s.student == self.student:
                self.scoreset = s
                self.total = s.total
                self.percentage = s.percentage
                self.grade = s.grade

    def build_grade_distances(self):
        course = self.paper.course
        grade_list = course.grade_levels
        i = get_grade_index(grade_list, self.grade)

        if i == 0:
            self.next_lowest_grade = grade_list[i+1]
            self.diff_lower_grade = round(self.percentage - self.next_lowest_grade.upper_bound, 1)
            self.next_highest_grade = None
            self.diff_higher_grade = None

        elif i == len(grade_list)-1:
            self.next_highest_grade = grade_list[i-1]
            self.diff_higher_grade = round(self.next_highest_grade.lower_bound - self.percentage, 1)
            self.next_lowest_grade = None
            self.diff_lower_grade = None

        else:
            self.next_highest_grade = grade_list[i-1]
            self.diff_higher_grade = round(self.next_highest_grade.lower_bound - self.percentage, 1)
            self.next_lowest_grade = grade_list[i+1]
            self.diff_lower_grade = round(self.percentage - self.next_lowest_grade.upper_bound, 1)

    def get_clazz_mean_data(self):
        raw_totals = []
        percentage_totals = []
        for s in self.student_scoresets:
            raw_totals.append(s.total)
            percentage_totals.append(s.percentage)
            self.clazz_raw_mean = calculate_mean(raw_totals)
            self.clazz_percentage_mean = calculate_mean(percentage_totals)

        grade_levels = self.paper.course.grade_levels
        for gl in grade_levels:
            if self.clazz_percentage_mean >= gl.lower_bound and self.clazz_percentage_mean < gl.upper_bound:
                self.clazz_mean_grade = gl.grade

    def make_grade_batch_dict(self):
        self.grade_batch_dict = filter_student_scoresets_by_grade(self.student_scoresets, self.paper.course.grade_levels)

    def get_question_highlights(self):
        self.question_strengths = []
        self.question_weaknesses = []
        percentage_list = []
        for s in self.scoreset.score_list:
            percentage_list.append(round(s.value/s.question.points*100, 2))
        highest_percentage = max(percentage_list)
        lowest_percentage = min(percentage_list)
        score_strengths_indexes = [x for x in range(len(percentage_list)) if percentage_list[x] == highest_percentage]
        score_weakness_indexes = [x for x in range(len(percentage_list)) if percentage_list[x] == lowest_percentage]
        for i in score_strengths_indexes:
            self.question_strengths.append(QuestionHighlight(self.paper.paper_questions[i].order_number, percentage_list[i], determine_grade(percentage_list[i], self.paper.course)))
        for j in score_weakness_indexes:
            self.question_weaknesses.append(QuestionHighlight(self.paper.paper_questions[j].order_number, percentage_list[j], determine_grade(percentage_list[j], self.paper.course)))

    def get_tag_highlights(self):
        self.tag_strengths = []
        self.tag_weaknesses = []
        percentage_list = []
        for tp in self.paper.profile.tag_profile_list:
            student_total = get_user_tag_total(self.student, tp.name, self.paper)
            percentage_list.append(round(student_total/tp.allocated_points*100, 2))

        highest_percentage = max(percentage_list)
        lowest_percentage = min(percentage_list)
        tag_strengths_indexes = [x for x in range(len(percentage_list)) if percentage_list[x] == highest_percentage]
        tag_weakness_indexes = [x for x in range(len(percentage_list)) if percentage_list[x] == lowest_percentage]
        for i in tag_strengths_indexes:
            self.tag_strengths.append(TagHighlight(self.paper.profile.tag_profile_list[i].tag, percentage_list[i], determine_grade(percentage_list[i], self.paper.course)))
        for j in tag_weakness_indexes:
            self.tag_weaknesses.append(TagHighlight(self.paper.profile.tag_profile_list[j].tag, percentage_list[j], determine_grade(percentage_list[j], self.paper.course)))

    def build_self(self):
        self.get_totals_and_grade()
        self.build_grade_distances()
        self.get_clazz_mean_data()
        self.make_grade_batch_dict()
        self.get_question_highlights()
        self.get_tag_highlights()
