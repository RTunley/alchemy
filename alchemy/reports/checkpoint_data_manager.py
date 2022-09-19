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
        self.paper_tally_groups = []

class CategoryTallyGroup():
    def __init__(self, category, paper_tally_list):
        self.category = category
        self.paper_tally_list = []
        self.average_tally = 0
        self.build_self(paper_tally_list)

    def build_self(self, paper_tally_list):
        tally_sum = 0
        for tally in paper_tally_list:
            if tally.paper.category == self.category:
                self.paper_tally_list.append(tally)
                tally_sum += tally.percent_total

        if len(self.paper_tally_list) != 0:
            self.average_tally = round(tally_sum/len(self.paper_tally_list),2)
        else:
            self.average_tally = None

def make_student_checkpoint_tally(student, checkpoint):
    student_checkpoint_tally = StudentCheckpointTally(student, checkpoint)

    # Make StudentPaperTally for each paper
    for paper in checkpoint.papers:
        paper_tally = data_manager.PaperScoreTally.from_student(student, paper)
        student_checkpoint_tally.paper_score_tally_list.append(paper_tally)

    # Group tallys into PaperTallyGroups and find weight_sum
    # (in case some categories are missing - normally weight_sum = 100)

    all_categories = [category for category in checkpoint.course.assessment_categories]
    weight_sum = 0
    for category in all_categories:
        category_group = CategoryTallyGroup(category, student_checkpoint_tally.paper_score_tally_list)
        student_checkpoint_tally.paper_tally_groups.append(category_group)
        if category_group.average_tally != None:
            weight_sum += category_group.category.weight

    # Add up the weighted category averages and normalize against weight_sum
    weighted_category_sum = 0
    for group in student_checkpoint_tally.paper_tally_groups:
        if group.average_tally != None:
            weighted_category_sum += round(group.average_tally*group.category.weight, 2)

    student_checkpoint_tally.percentage = round(weighted_category_sum/weight_sum, 1)
    student_checkpoint_tally.grade = data_manager.determine_grade(student_checkpoint_tally.percentage, checkpoint.course)
    return student_checkpoint_tally
