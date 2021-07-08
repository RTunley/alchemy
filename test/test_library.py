from alchemy import application as app
from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course, Question, Tag, Paper, PaperQuestion

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

    #Test whether question info appears on library homepage
    def test_question_on_library_index(self):
        course = Course.query.first()
        course_id = course.id
        q_tag_name = b"Difficult"
        q_tag = Tag(name = str(q_tag_name), course_id = course_id)
        db.session.add(q_tag)
        q_content = b"A very challenging question."
        q_soln = b"not an obvious solution"
        q_points = 5
        db.session.add(Question(content = str(q_content), solution = str(q_soln), points = q_points, course_id = course_id, tags = [q_tag]))
        db.session.commit()

        response = self.client.get("/course/{}/library".format(course_id), follow_redirects = True)
        self.assertTrue(q_content in response.data)
        self.assertTrue(q_soln in response.data)
        self.assertTrue(q_tag_name in response.data)

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
        self.assertTrue(tag_1_bytes in response.data)
        self.assertTrue(tag_2_bytes in response.data)

    # testing the edit question endpoint
    def test_edit_question(self):
        course = Course.query.first()
        course_id = course.id
        old_q = Question(content = 'New Question', solution = 'New Solution', points = 12, course_id = course_id)
        db.session.add(old_q)
        db.session.commit()

        old_q_id = old_q.id
        response = self.client.post('/course/{}/library/edit_question_submit'.format(course_id),
        data = dict(question_id = old_q_id, content = 'Edited Question', solution = 'Edited Solution', points = 10),
        follow_redirects = True)
        # number of question in db should be 1
        num_questions = len(course.questions)
        self.assertEqual(num_questions, 1)

        # question has correct attributes
        question = Question.query.filter_by(course_id = course_id).first()
        self.assertEqual(question.content, 'Edited Question')
        self.assertEqual(question.solution, 'Edited Solution')
        self.assertEqual(question.points, 10)

    # testing the delete question endpoint, no paper
    def test_delete_question(self):
        course = Course.query.first()
        course_id = course.id
        q = Question(content = 'New Question', solution = 'New Solution', points = 12, course_id = course_id)
        db.session.add(q)
        db.session.commit()
        data = {'question_id':q.id}
        response = self.client.get('/course/{}/library/delete_question'.format(course_id), query_string = data, follow_redirects = True)

        # number of question in db should be 0
        num_questions = len(course.questions)
        self.assertEqual(num_questions, 0)

    #testing the delete question endpoint, with paper --> Problematic since the delete function above is not working, so this question won't be deleted either but for the wrong reason.
    def test_delete_question_with_paper(self):
        course = Course.query.first()
        course_id = course.id
        q = Question(content = 'New Question', solution = 'New Solution', points = 12, course_id = course_id)
        db.session.add(q)
        paper = Paper(title = "Test paper", course_id = course_id)
        db.session.add(paper)
        db.session.commit()
        pq = PaperQuestion(paper_id = paper.id, question_id = q.id, order_number = 1)
        db.session.add(pq)
        db.session.commit()

        data = {'question_id':q.id}
        response = self.client.get('/course/{}/library/delete_question'.format(course_id), query_string = data, follow_redirects = True)

        # number of question in db should be 0
        num_questions = len(course.questions)
        self.assertEqual(num_questions, 1)

if __name__ == '__main__':
    unittest.main()
