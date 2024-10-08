import numpy as np
import sqlalchemy
from alchemy import models, db
from alchemy.views import profile
from alchemy.reports import plots, data_manager

class StudentCheckpointTally():
    def __init__(self, student, checkpoint):
        self.student = student
        self.checkpoint = checkpoint
        self.clazz = None
        self.percent_total = 0
        self.grade = None
        self.paper_score_tally_list = []
        self.category_tally_groups = []
        self.weight_sum = 0
        self.build_self(student, checkpoint)

    def build_self(self, student, checkpoint):

        for clazz in self.student.clazzes:
            if clazz.course == self.checkpoint.course:
                self.clazz = clazz

        # Make StudentPaperTally for each paper
        for paper in checkpoint.papers:
            paper_tally = data_manager.PaperScoreTally.from_student(student, paper)
            self.paper_score_tally_list.append(paper_tally)

        # Group tallys into PaperTallyGroups and find weight_sum
        # (in case some categories are missing - normally weight_sum = 100)

        all_categories = [category for category in checkpoint.course.assessment_categories]
        for category in all_categories:
            category_group = CategoryTallyGroup(category, self.paper_score_tally_list, checkpoint.course)
            self.category_tally_groups.append(category_group)
            if category_group.percentage != None:
                self.weight_sum += category_group.category.weight

        # Add up the weighted category averages and normalize against weight_sum
        weighted_category_sum = 0
        for group in self.category_tally_groups:
            if group.percentage != None:
                group.get_weighted_percentage(self.weight_sum)
                weighted_category_sum += round(group.percentage*group.category.weight, 2)

        self.percent_total = round(weighted_category_sum/self.weight_sum, 1)
        self.grade = data_manager.determine_grade(self.percent_total, checkpoint.course)

class StudentSnapshotSection():
    def __init__(self, student, checkpoint):
        self.student = student
        self.checkpoint = checkpoint
        self.course = self.checkpoint.course
        self.tally = StudentCheckpointTally(student, checkpoint)
        self.cohort_tally = CheckpointMultiScoreTally.from_cohort(checkpoint)

class CategoryTallyGroup():
    def __init__(self, category, paper_tally_list, course):
        self.category = category
        self.paper_tally_list = []
        self.total_points = 0
        self.total_tally = 0
        self.percentage = 0
        self.grade = None
        self.weighted_percentage = 0
        self.build_self(paper_tally_list, course)

    def build_self(self, paper_tally_list, course):
        tally_sum = 0
        for tally in paper_tally_list:
            if tally.paper.category == self.category:
                self.paper_tally_list.append(tally)
                self.total_tally += tally.raw_total
                self.total_points += tally.paper.profile.total_points

        if len(self.paper_tally_list) != 0:
            self.percentage = round(self.total_tally/self.total_points*100, 2)
            self.grade = data_manager.determine_grade(self.percentage, course)

        else:
            self.percentage = None

    def get_weighted_percentage(self, weight_sum):
        self.weighted_percentage = round(self.total_tally/self.total_points*self.category.weight/weight_sum*100, 2)

class AdjacentGrades(object):
    def __init__(self, grade_list, percentage, grade):
        self.higher_grade = None
        self.diff_higher_grade = 0
        self.lower_grade = None
        self.diff_lower_grade = 0
        self.build_self(grade_list, percentage, grade)

    def build_self(self, grade_list, percentage, grade):
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

class TagCheckpointSummary():
    def __init__(self, student, tag, checkpoint):
        self.student = student
        self.tag = tag
        self.checkpoint = checkpoint
        self.total = 0
        self.raw_score = 0
        self.percentage = 0
        self.grade = None

    def calculate_percentage_and_grade(self):
        self.percentage = data_manager.calc_percentage(self.raw_score, self.total)
        self.grade = data_manager.determine_grade(self.percentage, self.checkpoint.course)

class TagCheckpointProfile():
    def __init__(self, tag, student_list, checkpoint):
        self.tag = tag
        self.students = student_list
        self.checkpoint = checkpoint
        self.mean = 0
        self.sd = 0
        self.fivenumsumm = 0
        self.iqr = 0
        self.build_self()

    def build_self(self):
        student_tag_summaries = many_students_single_tag_summaries(self.tag, self.students, self.checkpoint)
        percent_values = []
        for tag_summary in student_tag_summaries:
            percent_values.append(tag_summary.percentage)

        array = np.array(percent_values)
        self.mean = round(np.mean(array), 2)
        self.sd = round(np.std(array), 2)
        min = array.min()
        max = array.max()
        quartiles = np.percentile(array, [25, 50, 75], interpolation = 'midpoint')
        self.fivenumsumm = [round(min,2), round(quartiles[0],2), round(quartiles[1],2), round(quartiles[2],2), round(max,2)]
        self.iqr = round(self.fivenumsumm[3] - self.fivenumsumm[1],2)

def all_checkpoint_tags(checkpoint):
    all_tags = []
    for paper in checkpoint.papers:
        for pq in paper.paper_questions:
            for tag in pq.question.tags:
                if tag not in all_tags:
                    all_tags.append(tag)
    return all_tags

def get_tag_summary(tag_summary_list, tag):
    for tag_summary in tag_summary_list:
        if tag_summary.tag == tag:
            target_summary = tag_summary
            break
    return target_summary

def single_student_many_tag_summaries(tag_list, student, checkpoint):
    checkpoint_tag_summaries = [TagCheckpointSummary(student, tag, checkpoint) for tag in tag_list]
    for paper in checkpoint.papers:
        for pq in paper.paper_questions:
            score = models.Score.query.filter_by(paper_id = paper.id, question_id = pq.question.id,
                    student_id = student.id).first()
            for tag in pq.question.tags:
                current_tag_summary = get_tag_summary(checkpoint_tag_summaries, tag)
                current_tag_summary.total += pq.question.points
                current_tag_summary.raw_score += score.value

    return checkpoint_tag_summaries

def many_students_single_tag_summaries(tag, student_list, checkpoint):
    all_tag_summaries = []
    for student in student_list:
        checkpoint_tag_summary = TagCheckpointSummary(student, tag, checkpoint)
        for paper in checkpoint.papers:
            for pq in paper.paper_questions:
                if tag in pq.question.tags:
                    score = models.Score.query.filter_by(paper_id = paper.id, question_id = pq.question.id, student_id = student.id).first()
                    checkpoint_tag_summary.total += pq.question.points
                    checkpoint_tag_summary.raw_score += score.value
        checkpoint_tag_summary.calculate_percentage_and_grade()
        all_tag_summaries.append(checkpoint_tag_summary)
    return all_tag_summaries

def all_checkpoint_tag_profiles(checkpoint, student_list):
    all_tags = all_checkpoint_tags(checkpoint)
    all_tag_profiles = []
    for tag in all_tags:
        profile = TagCheckpointProfile(tag, student_list, checkpoint)
        all_tag_profiles.append(profile)
    return all_tag_profiles

class TagHighlights():
    def __init__(self, student, checkpoint):
        self.has_strengths = False
        self.has_weaknesses = False
        self.strengths = []
        self.weaknesses = []
        self.build_self(student, checkpoint)

    def build_self(self, student, checkpoint):
        all_tags = all_checkpoint_tags(checkpoint)
        all_tag_summaries = single_student_many_tag_summaries(all_tags, student, checkpoint)
        for tag_summary in all_tag_summaries:
            tag_summary.calculate_percentage_and_grade()
        all_tag_summaries.sort(key=lambda x: x.percentage, reverse=True)

        max_percentage = all_tag_summaries[0].percentage
        min_percentage = all_tag_summaries[-1].percentage
        if min_percentage == 100:
            self.has_strengths = True
        elif max_percentage == 0:
            self.has_weaknesses = True
        else:
            self.has_weaknesses = True
            self.has_strengths = True
        for tag_summary in all_tag_summaries:
            if tag_summary.percentage == max_percentage:
                self.strengths.append(tag_summary)

            elif tag_summary.percentage == min_percentage:
                self.weaknesses.append(tag_summary)

class CategoryHighlights():
    def __init__(self, student, checkpoint):
        self.has_strengths = False
        self.has_weaknesses = False
        self.strengths = []
        self.weaknesses = []
        self.build_self(student, checkpoint)

    def build_self(self, student, checkpoint):
        paper_tally_list = []
        for paper in checkpoint.papers:
            paper_tally = data_manager.PaperScoreTally.from_student(student, paper)
            paper_tally_list.append(paper_tally)

        category_tally_list = []
        for category in checkpoint.course.assessment_categories:
            category_tally = CategoryTallyGroup(category, paper_tally_list, checkpoint.course)
            if category_tally.percentage:
                category_tally_list.append(category_tally)

        category_tally_list.sort(key=lambda x: x.percentage, reverse=True)
        max_percentage = category_tally_list[0].percentage
        min_percentage = category_tally_list[-1].percentage
        if min_percentage == 100:
            self.has_strengths = True
        elif max_percentage == 0:
            self.has_weaknesses = True
        else:
            self.has_weaknesses = True
            self.has_strengths = True
        for category_tally in category_tally_list:
            if category_tally.percentage == max_percentage:
                self.strengths.append(category_tally)

            elif category_tally.percentage == min_percentage:
                self.weaknesses.append(category_tally)

class CheckpointMultiScoreTally(object):
    def __init__(self, checkpoint, score_list):
        self.percent_mean = data_manager.calc_mean(score_list)
        self.mean_grade = data_manager.determine_grade(self.percent_mean, checkpoint.course)

    @staticmethod
    def from_clazz(clazz, checkpoint):
        clazz_checkpoint_percents = []
        for student in clazz.students:
            checkpoint_tally = StudentCheckpointTally(student, checkpoint)
            clazz_checkpoint_percents.append(checkpoint_tally.percent_total)
        return CheckpointMultiScoreTally(checkpoint, clazz_checkpoint_percents)

    @staticmethod
    def from_cohort(checkpoint):
        cohort_checkpoint_percents = []
        for clazz in checkpoint.course.clazzes:
            for student in clazz.students:
                checkpoint_tally = StudentCheckpointTally(student, checkpoint)
                cohort_checkpoint_percents.append(checkpoint_tally.percent_total)
        return CheckpointMultiScoreTally(checkpoint, cohort_checkpoint_percents)


def make_all_papers_graph(student, checkpoint):
    values = []
    labels = []
    for paper in checkpoint.papers:
        paper_score_tally = data_manager.PaperScoreTally.from_student(student, paper)
        values.append(paper_score_tally.percent_total)
        labels.append(paper_score_tally.paper.title)

    title = f"Overall Assessment Achievement for {checkpoint.snapshot.name}"
    plot_data = plots.create_bar_chart(title, values, None, labels, None)
    return plot_data

class GroupStatProfile():
    def __init__(self, percentage_list):
        self.values = percentage_list
        self.mean = 0
        self.sd = 0
        self.fivenumsumm = []
        self.iqr = 0
        self.build_self()

    def build_self(self):
        array = np.array(self.values)
        self.mean = round(np.mean(array), 2)
        self.sd = round(np.std(array), 2)
        min = array.min()
        max = array.max()
        quartiles = np.percentile(array, [25, 50, 75], interpolation = 'midpoint')
        self.fivenumsumm = [round(min,2), round(quartiles[0],2), round(quartiles[1],2), round(quartiles[2],2), round(max,2)]
        self.iqr = self.fivenumsumm[3] - self.fivenumsumm[1]

def create_distribution_plot(title, stat_profile):
    plot_data = plots.create_distribution_plot(stat_profile.values, stat_profile.sd, stat_profile.mean, title, False, None)
    return plot_data

def make_comparison_charts(tag_profile_list):
    means = []
    medians = []
    sd_list = []
    iqr_list = []
    labels = []
    for profile in tag_profile_list:
        means.append(profile.mean)
        medians.append(profile.fivenumsumm[2])
        sd_list.append(profile.sd)
        iqr_list.append(profile.iqr)
        labels.append(profile.tag.name)

    center_title = 'Tag Comparison: Central Tendency'
    spread_title = 'Tag Comparison: Spread'
    x_axis = None
    center_bar_plot = plots.create_comparative_bar_chart(center_title, means, 'Mean', medians, 'Median', labels, x_axis)
    spread_bar_plot = plots.create_comparative_bar_chart(spread_title, sd_list, 'Standard Deviation', iqr_list, 'Interquartile Range', labels, x_axis)
    return (center_bar_plot, spread_bar_plot)
