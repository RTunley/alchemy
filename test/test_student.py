import os
os.environ['ALCHEMY_CONFIG'] = 'TestConfig'
from alchemy import application as app

from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course, Clazz, AwsUser, Student, Paper, Score
import test.create_test_objects as cto

class StudentTestCase(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        test_account = cto.create_account()
        test_course = cto.create_course(test_account)
        grade_levels = cto.create_grade_levels(test_course)
        test_clazz = cto.add_clazz(test_course)
        student_list = cto.add_students_and_aws_users(test_course, test_clazz)

        q1 = cto.create_question1(test_course)
        q2 = cto.create_question2(test_course)
        tag1 = cto.create_attached_tag(test_course, q1, "Easy")
        tag2 = cto.create_attached_tag(test_course, q2, "Hard")
        category1 = cto.create_category(test_course)
        test_paper = cto.create_paper(test_course, category1)
        cto.add_question_to_paper(test_paper, q1)
        cto.add_question_to_paper(test_paper, q2)
        cto.add_scores(test_paper, student_list)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_paper_report(self):
        clazz = Clazz.query.first()
        paper = Paper.query.first()
        student = Student.query.first()
        section_types = ['OverviewSection', 'AdjacentGradesSection', 'ClazzSummarySection', 'CohortSummarySection', 'HighlightsSection']

        for section_type in section_types:
            with self.subTest(section=section_type):
                data = {'paper_id': paper.id, 'clazz_id': clazz.id, 'student_id': student.id, 'section_selection_string_get': section_type}
                response = self.client.get(f'/student/{student.id}/student_paper_report/clazz/{clazz.id}/paper/{paper.id}', query_string = data, follow_redirects = True)
                self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
