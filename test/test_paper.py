import os
os.environ['ALCHEMY_CONFIG'] = 'TestConfig'
from alchemy import application as app

from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account, Course, Question, Tag, Paper, PaperQuestion
import test.create_test_objects as cto

class BaseTestCase(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        test_account = cto.create_account()
        test_course = cto.create_course(test_account)
        test_paper = cto.create_paper(test_course)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class FlaskTestCase(BaseTestCase):

    # Check that paper home is working properly
    def test_paper_index(self):
        course = Course.query.first()
        paper = Paper.query.first()
        q = cto.create_question1(course)
        tag = cto.create_attached_tag(course, q, "Difficult")
        response = self.client.get("/course/{}/paper/{}".format(course.id, paper.id), follow_redirects = True)
        self.assertEqual(response.status_code, 200)

    #Testing header and important buttons
    def test_index_contains_info(self):
        course = Course.query.first()
        paper = Paper.query.first()
        response = self.client.get("/course/{}/paper/{}".format(course.id, paper.id), follow_redirects = True)
        header_text = "{} - {}".format(course.name, paper.title)
        header_text_bytes = bytes(header_text, 'utf-8')
        profile_btn = b"Profile"
        edit_btn = b"Edit"
        dup_btn = b"Duplicate"
        print_btn = b"Print Assessment"
        print_soln_btn = b"Print Solutions"
        self.assertTrue(header_text_bytes in response.data)
        self.assertTrue(profile_btn in response.data)
        self.assertTrue(edit_btn in response.data)
        self.assertTrue(dup_btn in response.data)
        self.assertTrue(print_btn in response.data)
        self.assertTrue(print_soln_btn in response.data)

    def test_edit_paper_response(self):
        course = Course.query.first()
        paper = Paper.query.first()
        response = self.client.get("/course/{}/paper/{}/edit".format(course.id, paper.id), content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_edit_title(self):
        course = Course.query.first()
        paper = Paper.query.first()
        new_title = "Edited Title"
        response = self.client.post("/course/{}/paper/{}/edit_title".format(course.id, paper.id), data = dict(paper_edit_modal_new_title = new_title), follow_redirects = True)
        paper = Paper.query.first()
        self.assertEqual(paper.title, new_title)

    def test_delete_paper(self):
        course = Course.query.first()
        paper = Paper.query.first()
        response = self.client.get('/course/{}/paper/{}/remove'.format(course.id, paper.id), follow_redirects = True)

        num_papers = len(Paper.query.all())
        self.assertEqual(num_papers, 0)

    def test_printable(self):
        course = Course.query.first()
        paper = Paper.query.first()
        q = cto.create_question1(course)
        cto.add_question_to_paper(paper, q)
        response = self.client.get('/course/{}/paper/{}/printable'.format(course.id, paper.id), follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(paper.paper_questions), 1)
        self.assertTrue(bytes(q.content, "utf-8") in response.data)

    def test_solutions(self):
        course = Course.query.first()
        paper = Paper.query.first()
        q = cto.create_question1(course)
        cto.add_question_to_paper(paper, q)
        response = self.client.get('/course/{}/paper/{}/solutions_printable'.format(course.id, paper.id), follow_redirects = True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(bytes(q.content, "UTF-8") in response.data)
        self.assertTrue(bytes(q.solution, "UTF-8") in response.data)

    def test_add_question(self):
        course = Course.query.first()
        paper = Paper.query.first()
        q = cto.create_question1(course)
        data = {'question_id': q.id}
        response = self.client.get('/course/{}/paper/{}/add_question'.format(course.id, paper.id), query_string = data)

        self.assertEqual(len(paper.paper_questions), 1)
        added_pq = PaperQuestion.query.filter_by(paper_id = paper.id).first()
        added_q = added_pq.question
        self.assertEqual(added_q.content, q.content)
        self.assertEqual(added_q.solution, q.solution)
        self.assertEqual(added_q.points, q.points)

    def test_remove_question(self):
        course = Course.query.first()
        paper = Paper.query.first()
        q = cto.create_question1(course)
        cto.add_question_to_paper(paper, q)
        data = {'question_id': q.id}
        self.assertEqual(len(paper.paper_questions), 1)
        response = self.client.get('/course/{}/paper/{}/remove_question'.format(course.id, paper.id), query_string = data)
        self.assertEqual(len(paper.paper_questions), 0)

    def test_duplicate(self):
        course = Course.query.first()
        paper = Paper.query.first()
        q = cto.create_question1(course)
        cto.add_question_to_paper(paper, q)
        response = self.client.get('/course/{}/paper/{}/duplicate'.format(course.id, paper.id))
        self.assertEqual(len(course.papers), 2)
        paper_duplicate = Paper.query.filter_by(id = 2).first()
        self.assertEqual(paper_duplicate.title, paper.title + ' (duplicate)')
        duplicate_pq = PaperQuestion.query.filter_by(paper_id = paper_duplicate.id).first()
        duplicate_q = duplicate_pq.question
        self.assertEqual(duplicate_q, q)

if __name__ == '__main__':
    unittest.main()
