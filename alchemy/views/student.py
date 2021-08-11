import flask
from flask import g
import random
from alchemy import application, db, models, auth_manager, summary_profiles, reports

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

@bp_student.url_defaults
def url_defaults(endpoint, values):
    if 'student_id' not in values:
        values['student_id'] = g.student.id

@bp_student.route('/index')
@auth_manager.require_group
def index():
    return flask.render_template('student/index.html')

@bp_student.route('/course-view/<int:course_id>')
@auth_manager.require_group
def course_view(course_id):
    g.course = models.Course.query.filter_by(id = course_id).first()
    for clazz in g.student.clazzes:
        if clazz.course.id == g.course.id:
            g.clazz = clazz
    course_profile = summary_profiles.make_student_course_profile(g.student, g.course)
    return flask.render_template('student/course_view.html', profile = course_profile)

@bp_student.route('/student_paper_report/clazz/<int:clazz_id>/paper/<int:paper_id>')
@auth_manager.require_group
def paper_report(clazz_id=0, paper_id=0):
    paper = models.Paper.query.get_or_404(paper_id)
    clazz = models.Clazz.query.get_or_404(clazz_id)
    paper.paper_questions = sorted(paper.paper_questions, key=lambda x: x.order_number)
    student_report = reports.report_objects.StudentPaperReport(g.student, clazz, paper)
    return flask.render_template('student/paper_report.html', student_report = student_report)
