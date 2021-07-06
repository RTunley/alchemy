from alchemy import application as app
from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course, Question, Tag

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

    def test_library_home(self):
        course = Course.query.first()
        course_id = course.id
        response = self.client.get("/course/{}/library".format(course_id), content_type='html/text', follow_redirects = True)
        self.assertEqual(response.status_code, 200)

    # testing the add question endpoint
    def test_new_question(self):
        course = Course.query.first()
        course_id = course.id
        response = self.client.post('/course/{}/library/add_question'.format(course_id),
        data = dict(content = 'New Question', solution = 'New Solution', points = 12),
        follow_redirects = True)
        # number of question in db should be 1
        question = Question.query.filter_by(course_id = course_id).first()
        num_questions = len(course.questions)
        self.assertEqual(num_questions, 1)

        # question has correct attributes
        self.assertEqual(question.content, 'New Question')
        self.assertEqual(question.solution, 'New Solution')
        self.assertEqual(question.points, 12)

    # Testing added tags appear in html 
    def test_available_tags(self):
        course = Course.query.first()
        course_id = course.id
        tag_1_bytes = b'Familiar'
        tag_2_bytes = b'Electricity'
        tag_1 = Tag(name = str(tag_1_bytes), course_id = course.id)
        tag_2 = Tag(name = str(tag_2_bytes), course_id = course.id)
        db.session.add(tag_1)
        db.session.add(tag_2)
        db.session.commit()

        response = self.client.get("/course/{}/library".format(course_id), follow_redirects = True)
        print(response.data)
        self.assertTrue(tag_1_bytes in response.data)
        self.assertTrue(tag_2_bytes in response.data)

if __name__ == '__main__':
    unittest.main()
