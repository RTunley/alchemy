import os
os.environ['ALCHEMY_CONFIG'] = 'TestConfig'
from alchemy import application as app

from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course, Clazz, AwsUser, Student, Paper, Score
import test.create_test_objects as cto

class ClazzTestCase(TestCase):

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
        test_paper = cto.create_paper(test_course)
        cto.add_question_to_paper(test_paper, q1)
        cto.add_question_to_paper(test_paper, q2)
        cto.add_scores(test_paper, student_list)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
        course = Course.query.first()
        clazz = Clazz.query.first()
        response = self.client.get('/course/{}/clazz/{}'.format(course.id, clazz.id), follow_redirects = True)
        self.assertEqual(response.status_code, 200)

    def test_student_info_present(self):
        course = Course.query.first()
        clazz = Clazz.query.first()
        response = self.client.get('/course/{}/clazz/{}'.format(course.id, clazz.id), follow_redirects = True)
        for student in clazz.students:
            self.assertTrue(bytes(student.aws_user.family_name, "UTF-8") in response.data)
            self.assertTrue(bytes(student.aws_user.given_name, "UTF-8") in response.data)

    def test_paper_results(self):
        course = Course.query.first()
        clazz = Clazz.query.first()
        paper = Paper.query.first()
        data = {'paper_id': paper.id}
        response = self.client.get('/course/{}/clazz/{}/paper_results'.format(course.id, clazz.id), query_string = data)
        self.assertEqual(response.status_code, 200)

    def test_paper_report(self):
        course = Course.query.first()
        clazz = Clazz.query.first()
        paper = Paper.query.first()
        scores = Score.query.all()
        section_types = ['OverviewSection', 'OverviewPlotSection', 'OverviewDetailsSection', 'GradeOverviewSection', 'TagOverviewSection', 'QuestionOverviewSection', 'TagDetailsSection', 'QuestionDetailsSection']

        for section_type in section_types:
            with self.subTest(section=section_type):
                data = {'paper_id': paper.id, 'section_selection_string_get': section_type}
                response = self.client.get(f'/course/{course.id}/clazz/{clazz.id}/paper_report/{paper.id}', query_string = data, follow_redirects = True)
                self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
