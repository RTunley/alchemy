from alchemy import application as app
from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course, Question

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

    #Ensure that flask was set up correctly
    def test_index(self):
        response = self.client.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    #Check that the account homepage contains correct data
    def test_account_home(self):
        response = self.client.get('/', content_type='html/text')
        account_home_body = b"This is the account homepage - But there's nothing interesting here yet."
        account_home_header = b"Alchemy:"
        account_home_false = b"We will never put these words on the home page"
        self.assertTrue(account_home_body in response.data)
        self.assertTrue(account_home_header in response.data)
        self.assertFalse(account_home_false in response.data)

    def test_course_home(self):
        course = Course.query.first()
        course_id = course.id
        response = self.client.get("/course/{}".format(course_id), content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_library_home(self):
        course = Course.query.first()
        course_id = course.id
        response = self.client.get("/course/{}/library".format(course_id), content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_new_question(self):
        course = Course.query.first()
        course_id = course.id
        response = self.client.post('/course/{}/library/add_question'.format(course_id),
        data = dict(content = 'New Question', solution = 'Famous Solution', points = '12'),
        follow_redirects = True)
        # number of question in db should be 1
        questions = Question.query.all()
        num_questions = len(questions)
        self.assertEqual(num_questions, 1)


if __name__ == '__main__':
    unittest.main()
