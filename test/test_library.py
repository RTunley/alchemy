import os
os.environ['ALCHEMY_CONFIG'] = 'TestConfig'
from alchemy import application as app

from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course, Question, Tag, Paper, PaperQuestion
import test.create_test_objects as cto

class LibraryTestCase(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        test_account = cto.create_account()
        test_course = cto.create_course(test_account)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_library_home(self):
        course = Course.query.first()
        response = self.client.get("/course/{}/library".format(course.id), content_type='html/text', follow_redirects = True)
        self.assertEqual(response.status_code, 200)

    # testing the add question endpoint
    def test_new_question(self):
        course = Course.query.first()
        question_data = [
            ('A question', 'A solution', 10, True),
            ('', 'A solution', 10, False), # invalid question
            ('A question', '', 10, False), # invalid solution
            ('A question', 'A solution', '', False), # invalid points
            # TODO the question should be invalid if points is negative.
        ]
        for i in range(len(question_data)):
            with self.subTest(question=question_data[i]):
                content, solution, points, question_valid = question_data[i]
                prev_question_count = len(course.questions)
                response = self.client.post('/course/{}/library/add_question'.format(course.id),
                data = dict(content=content, solution=solution, points=points),
                follow_redirects = True)

                if question_valid:
                    # check number of question in db
                    self.assertEqual(len(course.questions), prev_question_count+1)

                    # question has correct attributes
                    question = Question.query.filter_by(course_id=course.id).all()[-1]
                    self.assertEqual(question.content, content)
                    self.assertEqual(question.solution, solution)
                    self.assertEqual(question.points, points)
                else:
                    self.assertEqual(len(course.questions), prev_question_count)

    #Test whether question info appears on library homepage
    def test_question_added(self):
        course = Course.query.first()
        q = cto.create_question1(course)
        tag = cto.create_attached_tag(course, q, "Familiar")
        response = self.client.get("/course/{}/library".format(course.id), follow_redirects = True)
        self.assertTrue(bytes(q.content, "UTF-8") in response.data)
        self.assertTrue(bytes(q.solution, "UTF-8") in response.data)
        self.assertTrue(bytes(tag.name, "UTF-8") in response.data)

    # Testing added tags appear in html
    def test_tags_added(self):
        course = Course.query.first()
        tag1 = cto.create_lone_tag(course, "Familiar")
        tag2 = cto.create_lone_tag(course, "Unfamiliar")
        response = self.client.get("/course/{}/library".format(course.id), follow_redirects = True)
        self.assertTrue(bytes(tag1.name, "UTF-8") in response.data)
        self.assertTrue(bytes(tag2.name, "UTF-8") in response.data)

    # testing the edit question endpoint
    def test_edit_question(self):
        course = Course.query.first()
        q = cto.create_question1(course)
        response = self.client.post('/course/{}/library/edit_question_submit'.format(course.id),
        data = dict(question_id = q.id, content = 'Edited Question', solution = 'Edited Solution', points = 10), follow_redirects = True)
        # number of question in db should be 1
        num_questions = len(course.questions)
        self.assertEqual(num_questions, 1)

        # question has correct attributes
        question = Question.query.filter_by(course_id = course.id).first()
        self.assertEqual(question.content, 'Edited Question')
        self.assertEqual(question.solution, 'Edited Solution')
        self.assertEqual(question.points, 10)

    # testing the delete question endpoint, no paper
    def test_delete_question(self):
        course = Course.query.first()
        q = cto.create_question1(course)
        self.assertEqual(len(course.questions), 1)
        data = {'question_id':q.id}
        response = self.client.get('/course/{}/library/delete_question'.format(course.id), query_string = data, follow_redirects = True)
        # number of questions in db should be 0
        self.assertEqual(len(course.questions), 0)

    #testing the delete question endpoint, with paper
    def test_delete_question_with_paper(self):
        course = Course.query.first()
        q = cto.create_question1(course)
        p = cto.create_paper(course)
        pq = cto.add_question_to_paper(p, q)
        data = {'question_id':q.id}
        response = self.client.get('/course/{}/library/delete_question'.format(course.id), query_string = data, follow_redirects = True)
        # number of question in db should be 1
        # delete_question is disabled when q is attached to paper
        num_questions = len(course.questions)
        self.assertEqual(num_questions, 1)

if __name__ == '__main__':
    unittest.main()
