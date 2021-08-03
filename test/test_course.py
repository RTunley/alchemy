import os
os.environ['ALCHEMY_CONFIG'] = 'TestConfig'
from alchemy import application as app

from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course, GradeLevel
import test.create_test_objects as cto

class BaseTestCase(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        test_account = cto.create_account()
        test_course = cto.create_course(test_account)
        grade_levels = cto.create_grade_levels(test_course)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class FlaskTestCase(BaseTestCase):

    #Testing course home page
    def test_course_home(self):
        course = Course.query.first()
        course_id = course.id
        response = self.client.get("/course/{}".format(course_id), content_type='html/text', follow_redirects = True)
        self.assertEqual(response.status_code, 200)

    #testing basic GradeLevel relationships
    def test_grade_levels(self):
        grade_levels = GradeLevel.query.all()
        self.assertEqual(len(grade_levels), 5)

        grade_A = GradeLevel.query.filter_by(grade = 'A').first()
        self.assertEqual(grade_A.lower_bound, 85)
        self.assertEqual(grade_A.upper_bound, 100)

    # Test changing grade names and grade levels
    def test_change_grade_name(self):
        grade_level_lists = [
            ['Z','85','B','70','C','50','D','30','F','0'],  # 1st grade has changed
            ['A','85'], # only 1 grade
            ['A','0'],  # only 1 grade, with value 0
            ['A','30','F','0'], # only 2 grades
        ]
        course = Course.query.first()
        for grade_level_list in grade_level_lists:
            with self.subTest(grades=grade_level_list):
                data = {"course_id": course.id, "grade_levels": grade_level_list}
                response = self.client.post("course/{}/edit_grade_levels".format(course.id), json = data)
                self.assertEqual(response.status_code, 200)

                upper_bound = 100
                for i in range(0, len(grade_level_list), 2):
                    grade_name = grade_level_list[i]
                    lower_bound = int(grade_level_list[i+1])

                    grade = GradeLevel.query.filter_by(grade=grade_name).first()
                    self.assertEqual(grade.lower_bound, lower_bound)
                    self.assertEqual(grade.upper_bound, upper_bound)
                    upper_bound = lower_bound

if __name__ == '__main__':
    unittest.main()
