import numpy as np
import sqlalchemy
from alchemy import models, db
from alchemy.views import profile
from alchemy.reports import plots, data_manager

class StudentCheckpointTally():
    def __init__(self, student, checkpoint):
        self.student = student
        self.checkpoint = checkpoint
        self.percentage = 0
        self.grade = None
        self.paper_score_tally_list = []
        self.category_tally_groups = []
        self.weight_sum = 0
        self.build_self(student, checkpoint)

    def build_self(self, student, checkpoint):

        # Make StudentPaperTally for each paper
        for paper in checkpoint.papers:
            paper_tally = data_manager.PaperScoreTally.from_student(student, paper)
            self.paper_score_tally_list.append(paper_tally)

        # Group tallys into PaperTallyGroups and find weight_sum
        # (in case some categories are missing - normally weight_sum = 100)

        all_categories = [category for category in checkpoint.course.assessment_categories]
        for category in all_categories:
            category_group = CategoryTallyGroup(category, self.paper_score_tally_list)
            self.category_tally_groups.append(category_group)
            if category_group.percentage != None:
                self.weight_sum += category_group.category.weight

        # Add up the weighted category averages and normalize against weight_sum
        weighted_category_sum = 0
        for group in self.category_tally_groups:
            if group.percentage != None:
                group.get_weighted_percentage(self.weight_sum)
                weighted_category_sum += round(group.percentage*group.category.weight, 2)

        self.percentage = round(weighted_category_sum/self.weight_sum, 1)
        self.grade = data_manager.determine_grade(self.percentage, checkpoint.course)

class CategoryTallyGroup():
    def __init__(self, category, paper_tally_list):
        self.category = category
        self.paper_tally_list = []
        self.total_points = 0
        self.total_tally = 0
        self.percentage = 0
        self.weighted_percentage = 0
        self.build_self(paper_tally_list)

    def build_self(self, paper_tally_list):
        tally_sum = 0
        for tally in paper_tally_list:
            if tally.paper.category == self.category:
                self.paper_tally_list.append(tally)
                self.total_tally += tally.raw_total
                self.total_points += tally.paper.profile.total_points

        if len(self.paper_tally_list) != 0:
            self.percentage = round(self.total_tally/self.total_points*100, 2)

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
