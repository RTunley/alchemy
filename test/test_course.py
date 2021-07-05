from alchemy import application as app
from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course

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

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class FlaskTestCase(BaseTestCase):

    def test_course_home(self):
        course = Course.query.first()
        course_id = course.id
        response = self.client.get("/course/{}".format(course_id), content_type='html/text', follow_redirects = True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
