import numpy as np
import sqlalchemy
from alchemy import models, db
from alchemy.reports import plots

## Data organisation classes

class ClazzPaperProfile(object):
    def __init__(self, clazz, paper):
        self.paper = paper
        self.paper_score_tallies = []
        self.build_self(clazz)

    def build_self(self, clazz):
        for student in clazz.students:
            self.paper_score_tallies.append(PaperScoreTally.from_student(student, self.paper))

class ClazzCourseProfile(object):
    def __init__(self, clazz, course):
        self.clazz = clazz
        self.student_course_profiles = []
        self.build_self(clazz, course)

    def build_self(self, clazz, course):
        for student in clazz.students:
            self.student_course_profiles.append(StudentCourseProfile(student, course))

class StudentCourseProfile(object):
    def __init__(self, student, course):
        self.student = student
        self.paper_score_tallies = []
        self.build_self(student, course)

    def build_self(self, student, course):
        for paper in course.papers:
            paper_score_tally = PaperScoreTally.from_student(student, paper)
            self.paper_score_tallies.append(paper_score_tally)

class PaperScoreTally(object):
    def __init__(self, student, paper, score):
        self.student = student
        self.paper = paper
        self.scores = []
        self.paper_total = paper.profile.total_points
        self.raw_total = score
        self.percent_total = calc_percentage(self.raw_total, self.paper_total)
        self.grade = determine_grade(self.percent_total, paper.course)

    @staticmethod
    def from_student(student, paper):
        # get the scores for the student on this paper, ordered by each question's order number
        known_scores = db.session.query(models.Score
            ).filter(models.PaperQuestion.question_id == models.Score.question_id,
                     models.PaperQuestion.paper_id == models.Score.paper_id
            ).filter_by(student_id = student.id, paper_id = paper.id
            ).order_by(models.PaperQuestion.order_number
            ).all()
        # get the questions for this paper
        paper_questions = models.PaperQuestion.query.filter_by(paper_id = paper.id
            ).order_by(models.PaperQuestion.order_number
            ).all()

        scores = []
        for paper_question in paper_questions:
            score = None
            for known_score in known_scores:
                if known_score.question_id == paper_question.question_id:
                    score = known_score
                    break
            if not score:
                # no score has been recorded yet for this student, so make a blank score
                score = models.Score(value = None, paper_id = paper.id, question_id = paper_question.question_id, student_id = student.id)
            scores.append(score)

        paper_score_tally = PaperScoreTally(student, paper, total_score(scores))
        paper_score_tally.scores = scores
        return paper_score_tally

    def has_all_scores(self):
        for score in self.scores:
            if score == None or score.value == None:
                return False
            else:
                return True

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

class GradeBatch(object):
    def __init__(self, grade_level):
        self.grade_level = grade_level
        self.student_tallies = []

    def order_tallies(self):
        self.student_tallies.sort(key=lambda x: x.percent_total, reverse=True)

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

class StatSummary(object):
    def __init__(self, paper, score, total):
        self.object = None
        self.total = total
        self.raw_score = score
        self.percent_score = calc_percentage(self.raw_score, self.total)
        self.grade = determine_grade(self.percent_score, paper.course)

    @staticmethod
    def from_tag(paper, tag_profile, score):
        tag_statsumm = StatSummary(paper, score, tag_profile.allocated_points)
        tag_statsumm.object = tag_profile
        return tag_statsumm

    @staticmethod
    def from_paperquestion(paper, paper_question, score):
        question_statsumm = StatSummary(paper, score, paper_question.question.points)
        question_statsumm.object = paper_question
        return question_statsumm

class QuestionHighlightSets(object):
    def __init__(self, student, paper):
        self.strengths = []
        self.has_strengths = False
        self.weaknesses = []
        self.has_weaknesses = False
        self.build_self(student, paper)

    def build_self(self, student, paper):
        student_statsumm_list = make_student_statsumm_list(student, paper)
        student_statsumm_list.sort(key=lambda x: x.percent_score, reverse=True)
        max_percentage = student_statsumm_list[0].percent_score
        min_percentage = student_statsumm_list[-1].percent_score
        if min_percentage == 100:
            self.has_strengths = True
        elif max_percentage == 0:
            self.has_weaknesses = True
        else:
            self.has_weaknesses = True
            self.has_strengths = True
        for statsumm in student_statsumm_list:
            if statsumm.percent_score == max_percentage:
                self.strengths.append(statsumm)

            elif statsumm.percent_score == min_percentage:
                self.weaknesses.append(statsumm)

class TagHighlightSets(object):
    def __init__(self, student, paper, scores):
        self.strengths = []
        self.weaknesses = []
        self.build_self(student, paper, scores)

    def build_self(self, student, paper, scores):
        student_tag_statsumms = []
        for profile in paper.profile.tag_profile_list:
            student_tag_score = get_tag_score(student, profile.tag.name, paper, scores)
            tag_statsumm = StatSummary.from_tag(paper, profile, student_tag_score)
            student_tag_statsumms.append(tag_statsumm)

        student_tag_statsumms.sort(key=lambda x: x.percent_score, reverse=True)
        for statsumm in student_tag_statsumms:
            if statsumm.percent_score == student_tag_statsumms[0].percent_score:
                self.strengths.append(statsumm)

            elif statsumm.percent_score == student_tag_statsumms[-1].percent_score:
                self.weaknesses.append(statsumm)

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
        self.norm_iqr = round(self.norm_fivenumsumm[3] - self.norm_fivenumsumm[1],2)

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

    # Used for comparing MCQ acievement and OA achievement - not associated with particular objects, but need labels to distringuish them.
    @staticmethod
    def from_question_group(values_list, total, label):
        statprofile = StatProfile(values_list, total)
        statprofile.label = label
        return statprofile

## A selection of functions that will required for multuple report sections, and probably used to build profiles as well.

def all_students_in_course(course):
    all_students = []
    for clazz in course.clazzes:
        for student in clazz.students:
            all_students.append(student)
    return(all_students)

def total_score(score_list):
    return sum(score.value for score in score_list if score.value)

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

def get_tag_score(student, tag_string, paper, scores):
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

def make_grade_batch_list(student_tally_list, course):
    grade_batch_list = []
    for grade_level in course.grade_levels:
        grade_batch = GradeBatch(grade_level)
        for tally in student_tally_list:
            if tally.grade == grade_batch.grade_level.grade:
                grade_batch.student_tallies.append(tally)
        grade_batch.order_tallies()
        grade_batch_list.append(grade_batch)

    return grade_batch_list

def make_tag_statprofile_list(student_list, paper):
    tag_statprofile_list = []
    for tag_profile in paper.profile.tag_profile_list:
        raw_totals = []
        for student in student_list:
            scores = models.Score.query.filter_by(student_id = student.id, paper_id = paper.id).all()
            tag_total = get_tag_score(student, tag_profile.name, paper, scores)
            raw_totals.append(tag_total)
        tag_statprofile = StatProfile.from_tag(raw_totals, tag_profile.allocated_points, tag_profile.tag)
        tag_statprofile_list.append(tag_statprofile)
    return tag_statprofile_list

def make_question_statprofile_list(student_list, paper):
    student_ids = [student.id for student in student_list]
    question_statprofile_list = []
    for pq in paper.paper_questions:
        if not pq.question.is_multiple_choice():
            all_scores = models.Score.query.filter_by(paper_id = paper.id, question_id = pq.question.id).all()
            group_scores = []
            for score in all_scores:
                if score.student_id in student_ids:
                    group_scores.append(score)
            raw_totals = [score.value for score in group_scores]
            question_statprofile = StatProfile.from_question(raw_totals, pq.question.points, pq)
            question_statprofile_list.append(question_statprofile)
    return question_statprofile_list

def make_question_group_statprofiles(student_list, paper):
    student_ids = []
    mcq_ids = []
    mcq_raw_totals = []
    oaq_raw_totals = []
    for pq in paper.paper_questions:
        if pq.question.is_multiple_choice():
            mcq_ids.append(pq.question.id)
    for student in student_list:
        mcq_raw = 0
        oaq_raw = 0
        student_scores = models.Score.query.filter_by(paper_id = paper.id, student_id = student.id).all()
        for score in student_scores:
            if score.question_id in mcq_ids:
                mcq_raw += score.value
            else:
                oaq_raw += score.value
        mcq_raw_totals.append(mcq_raw)
        oaq_raw_totals.append(oaq_raw)
    mcq_statprofile = StatProfile.from_question_group(mcq_raw_totals, paper.profile.total_mc_points, "Multiple Choice")
    oaq_statprofile = StatProfile.from_question_group(oaq_raw_totals, paper.profile.total_oa_points, "Open Answer")
    return [mcq_statprofile, oaq_statprofile]

def make_student_statsumm_list(student, paper):
    question_statsumm_list = []
    for paper_question in paper.paper_questions:
        student_score = models.Score.query.filter_by(paper_id = paper.id, student_id = student.id, question_id = paper_question.question.id).first()
        question_statsumm = StatSummary.from_paperquestion(paper, paper_question, student_score.value)
        question_statsumm_list.append(question_statsumm)
    return question_statsumm_list

def make_student_course_profiles(course, student_list):
    student_profiles = []
    for student in student_list:
        course_profile = StudentCourseProfile(student, course)
        student_profiles.append(course_profile)
    return student_profiles

## Functions for interacting with reports.plots ##

def create_clazz_distribution_plot(clazz, paper):
    clazz_statprofile = StatProfile(total_student_scores_for_clazz(clazz, paper), paper.profile.total_points)
    plot_data = plots.create_distribution_plot(clazz_statprofile.norm_values_list, clazz_statprofile.norm_sd, clazz_statprofile.norm_mean, 'Distribution of Overall Achievement', False, None)
    return plot_data

def create_cohort_distribution_plot(paper):
    cohort_statprofile = StatProfile(total_student_scores_for_cohort(paper), paper.profile.total_points)
    plot_data = plots.create_distribution_plot(cohort_statprofile.norm_values_list, cohort_statprofile.norm_sd, cohort_statprofile.norm_mean, 'Distribution of Overall Achievement', False, None)
    return plot_data

def make_grade_pie_data(grade_batch_list):
    slices = []
    labels = []
    for batch in grade_batch_list:
        label = ''
        if len(batch.student_tallies) == 1:
            label = batch.grade_level.grade + ' (1 Student)'
        elif len(batch.student_tallies) == 0:
            label = batch.grade_level.grade + ' (None)'
        else:
            label = batch.grade_level.grade + f' ({len(batch.student_tallies)} Students)'

        labels.append(label)
        slices.append(len(batch.student_tallies))

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
    # print("Here is the statprofile list! :")
    # print(statprofile_list) Statprofile list is empty
    for statprofile in statprofile_list:
        means.append(statprofile.norm_mean)
        medians.append(statprofile.norm_fivenumsumm[2])
        sd_list.append(statprofile.norm_sd)
        iqr_list.append(statprofile.norm_iqr)
        if isinstance(statprofile.object, models.Tag):
            labels.append(statprofile.object.name)
        elif isinstance(statprofile.object, models.PaperQuestion):
            labels.append(statprofile.object.order_number)
        else:
            labels.append(statprofile.label)

    for statprofile in statprofile_list:
        if isinstance(statprofile.object, models.Tag):
            center_title = 'Tag Comparison: Central Tendency'
            spread_title = 'Tag Comparison: Spread'
            x_axis = None
            center_bar_plot = plots.create_comparative_bar_chart(center_title, means, 'Mean', medians, 'Median', labels, x_axis)
            spread_bar_plot = plots.create_comparative_bar_chart(spread_title, sd_list, 'Standard Deviation', iqr_list, 'Interquartile Range', labels, x_axis)
            return (center_bar_plot, spread_bar_plot)

        elif isinstance(statprofile.object, models.PaperQuestion):
            center_title = 'Open Answer Question Comparison: Central Tendency'
            spread_title = 'Open Answer Question Comparison: Spread'
            x_axis = 'Question Number'
            center_bar_plot = plots.create_comparative_bar_chart(center_title, means, 'Mean', medians, 'Median', labels, x_axis)
            spread_bar_plot = plots.create_comparative_bar_chart(spread_title, sd_list, 'Standard Deviation', iqr_list, 'Interquartile Range', labels, x_axis)
            return (center_bar_plot, spread_bar_plot)

        else:
            center_title = 'Multiple Choice vs Open Answer: Central Tendency'
            spread_title = 'Multiple Choice vs Open Answer: Spread'
            center_bar_plot = plots.create_comparative_bar_chart(center_title, means, 'Mean', medians, 'Median', labels, None)
            spread_bar_plot = plots.create_comparative_bar_chart(spread_title, sd_list, 'Standard Deviation', iqr_list, 'Interquartile Range', labels, None)
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
