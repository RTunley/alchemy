import numpy as np
import sqlalchemy
from alchemy import models, db
from alchemy.views import profile
from alchemy.reports import plots, data_manager

class CheckpointTally():
    def __init__(self, student, checkpoint):
        self.student = student
        self.checkpoint = checkpoint
        self.percentage = 55
        self.grade = 'C'
