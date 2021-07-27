import os
os.environ['ALCHEMY_CONFIG'] = 'TestConfig'
from alchemy import application as app

from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course, Clazz, AwsUser, Student, Paper
import test.create_test_objects as cto

class BaseTestCase(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        test_account = cto.create_account()
        test_course = cto.create_course(test_account)
        grade_levels = cto.create_grade_levels(test_course)
        test_clazz = cto.add_clazz(test_course)
        student_list = cto.add_students_and_aws_users(test_course, test_clazz)

        test_paper = cto.create_paper(test_course)
        q1 = cto.create_question1(test_course)
        cto.add_question_to_paper(test_paper, q1)
        q2 = cto.create_question2(test_course)
        cto.add_question_to_paper(test_paper, q2)
        cto.add_scores(test_paper, student_list)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class FlaskTestCase(BaseTestCase):

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

    # def_test_update_scores(self):
        #Should look like:
        # 1) Get student score data with
        # response = self.client.get('/course/{}/clazz/{}/paper_results'.format(course.id, clazz.id)
        # 2) make a change to one student scores using student_scores in response.data...?
        # 3) send the new new changes
        # response = self.client.post('/course/{}/clazz/{}/paper_results'.format(course.id, clazz.id), data = dict(student_scores = new_student_scores))
        # check that new values are in the db for that student

    def test_clazz_paper_report(self):
        course = Course.query.first()
        clazz = Clazz.query.first()
        paper = Paper.query.first()
        data = {'paper_id': paper.id}
        response = self.client.get('/course/{}/clazz/{}/paper_report'.format(course.id, clazz.id), query_string = data)
        self.assertEqual(response.status_code, 200)

    # Don't write a test for student_paper_report because that will eventually be moved to the student view


if __name__ == '__main__':
    unittest.main()
