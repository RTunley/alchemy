from alchemy import application as app
from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course, GradeLevel

grade_tuples = [('A',85,100), ('B',70,85), ('C',50,70), ('D',30,50), ('F',0,30)]

class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('alchemy.config.TestConfig')
        return app

    def setUp(self):
        db.create_all()
        test_account = Account(name = "Test School")
        db.session.add(test_account)
        test_course = Course(name = "Test Course", account = test_account)
        db.session.add(test_course)
        db.session.commit()
        for t in grade_tuples:
            db.session.add(GradeLevel(grade = t[0], lower_bound = t[1], upper_bound = t[2], course_id = test_course.id))
        db.session.commit()

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
        print(grade_A)
        self.assertEqual(grade_A.lower_bound, 85)
        self.assertEqual(grade_A.upper_bound, 100)



if __name__ == '__main__':
    unittest.main()
