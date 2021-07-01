
def build_tag_profile(paper, tag):
    allocated_questions = 0
    allocated_points = 0
    for paper_question in paper.paper_questions:
        for t in paper_question.question.tags:
            if t.name == tag.name:
                allocated_questions += 1
                allocated_points += paper_question.question.points
    tag_profile = TagProfile(tag, allocated_questions, allocated_points)
    return tag_profile

class PaperProfile:
    def __init__(self):
        self.total_questions = 0
        self.total_points = 0
        self.tag_profile_list = []

class TagProfile:
    def __init__(self, tag, allocated_questions, allocated_points):
        self.tag = tag
        self.name = self.tag.name
        self.allocated_questions = allocated_questions
        self.allocated_points = allocated_points
        self.question_percentage = 0
        self.points_percentage = 0

    def calculate_q_percentage(self, paper_profile):
        q_percentage = self.allocated_questions/paper_profile.total_questions*100
        self.question_percentage = round(q_percentage, 1)

    def calculate_p_percentage(self, paper_profile):
        p_percentage = self.allocated_points/paper_profile.total_points*100
        self.points_percentage = round(p_percentage, 1)
