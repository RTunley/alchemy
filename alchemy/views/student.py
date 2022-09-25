import flask
from flask import g
import random
from alchemy import application, db, models, auth_manager
from alchemy.reports import data_manager, report_types

bp_student = flask.Blueprint('student', __name__)

@application.template_filter('shuffle')
def filter_shuffle(seq):
    try:
        result = list(seq)
        random.shuffle(result)
        return result
    except:
        return seq

@bp_student.url_value_preprocessor
def url_value_preprocessor(endpoint, values):
    g.student = models.Student.query.get_or_404(values.pop('student_id'))
    g.school = models.School.query.first()
    g.student_paper_report_sections_string = 'OverviewSection,AdjacentGradesSection,ClazzSummarySection,CohortSummarySection,HighlightsSection,TagDetailsSection,QuestionDetailsSection'
    g.student_checkpoint_report_sections_string = 'OverviewSection,AdjacentGradesSection'

@bp_student.url_defaults
def url_defaults(endpoint, values):
    if 'student_id' not in values:
        values['student_id'] = g.student.id

@bp_student.route('/index')
@auth_manager.require_group
def index():
    return flask.render_template('student/index.html')

@bp_student.route('/courses')
@auth_manager.require_group
def courses():
    return flask.render_template('student/courses.html')


@bp_student.route('/course-view/<int:course_id>')
@auth_manager.require_group
def course_view(course_id):
    g.course = models.Course.query.filter_by(id = course_id).first()
    for clazz in g.student.clazzes:
        if clazz.course.id == g.course.id:
            g.clazz = clazz
    course_profile = data_manager.StudentCourseProfile(g.student, g.course)
    return flask.render_template('student/course_view.html', profile = course_profile)

@bp_student.route('/student_paper_report/clazz/<int:clazz_id>/paper/<int:paper_id>')
@auth_manager.require_group
def paper_report(clazz_id=0, paper_id=0):
    paper = models.Paper.query.get_or_404(paper_id)
    clazz = models.Clazz.query.get_or_404(clazz_id)
    section_selection_string = flask.request.args.get('section_selection_string_get')
    section_selections = section_selection_string.split(',')
    student_report = report_types.StudentPaperReport(g.student, clazz, paper, section_selections)
    return flask.render_template('student/paper_report.html', student_report = student_report)

@bp_student.route('/student_paper_report/clazz/<int:clazz_id>/checkpoint/<int:checkpoint_id>')
@auth_manager.require_group
def checkpoint_report(clazz_id=0, checkpoint_id=0):
    checkpoint = models.Checkpoint.query.get_or_404(checkpoint_id)
    clazz = models.Clazz.query.get_or_404(clazz_id)
    section_selection_string = flask.request.args.get('section_selection_string_get')
    section_selections = section_selection_string.split(',')
    student_checkpoint_report = report_types.StudentCheckpointReport(g.student, clazz, checkpoint, section_selections)
    return flask.render_template('student/checkpoint_report.html', student_checkpoint_report = student_checkpoint_report)
