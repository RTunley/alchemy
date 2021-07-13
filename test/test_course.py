from alchemy import application as app
from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course, GradeLevel
import test.create_test_objects as cto

grade_tuples = [('A',85,100), ('B',70,85), ('C',50,70), ('D',30,50), ('F',0,30)]

class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('alchemy.config.TestConfig')
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

    # Test changing grade names (harmless)
    def test_change_grade_name(self):
        course = Course.query.first()
        course_id = course.id
        altered_grade_string = "Z,85,B,70,C,50,D,30,F,0"
        data = {"course_id": course_id, "grade_levels": altered_grade_string}
        response = self.client.get("course/{}/edit_grade_levels".format(course_id), query_string = data)

        grade_Z = GradeLevel.query.filter_by(grade = 'Z').first()
        self.assertEqual(grade_Z.lower_bound, 85)
        self.assertEqual(grade_Z.upper_bound, 100)

if __name__ == '__main__':
    unittest.main()
