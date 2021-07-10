from alchemy import application as app
from alchemy import db
import flask
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
        test_paper = Paper(title = 'Test Paper')
        db.session.add(test_paper)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class FlaskTestCase(BaseTestCase):

    # Check that paper home is working properly
    def test_paper_index(self):
        course = Course.query.first()
        paper = Paper.query.first()
        q_tag_name = b"Difficult"
        q_tag = Tag(name = str(q_tag_name), course_id = course.id)
        db.session.add(q_tag)
        q_content = b"A very challenging question."
        q_soln = b"not an obvious solution"
        q_points = 5
        db.session.add(Question(content = str(q_content), solution = str(q_soln), points = q_points, course_id = course.id, tags = [q_tag]))
        db.session.commit()
        response = self.client.get("/course/{}/paper/{}".format(course.id, paper.id), content_type='html/text', follow_redirects = True)
        self.assertEqual(response.status_code, 200)

    #Testing header and important buttons
    def test_index_contains_info(self):
        course = Course.query.first()
        paper = Paper.query.first()
        response = self.client.get("/course/{}/paper/{}".format(course.id, paper.id), content_type='html/text', follow_redirects = True)
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
        print("In Test")
        print("Course id: ", course.id)
        print("Paper ID: ", paper.id)
        response = self.client.get("/course/{}/paper/{}/edit".format(course.id, paper.id), content_type='html/text')
        assertEqual(response.status_code, 200)

    # def test_edit_title(self):
    #     course = Course.query.first()
    #     paper = Paper.query.first()
    #     new_title = "Edited Title"
    #     response = self.client.post("/course/{}/paper/{}/edit_title".format(course.id, paper.id), content_type='html/text', data = dict(paper_edit_modal_new_title = new_title), follow_redirects = True)
    #
    #     paper = Paper.query.first()
    #     self.assertEqual(paper.title, new_title)

    def test_delete_paper(self):
        course = Course.query.first()
        paper = Paper.query.first()
        response = self.client.get('/course/{}/paper/{}/remove'.format(course.id, paper.id), follow_redirects = True)

        num_papers = len(Paper.query.all())
        self.assertEqual(num_papers, 0)

    def test_printable(self):
        course = Course.query.first()
        paper = Paper.query.first()
        q = Question(content = 'New Question', solution = 'New Solution', points = 5, course_id = course.id)
        db.session.add(q)
        db.session.commit()
        pq = PaperQuestion(paper_id = paper.id, question_id = q.id, order_number = 1)
        db.session.add(pq)
        db.session.commit()
        response = self.client.get('/course/{}/paper/{}/printable'.format(course.id, paper.id), follow_redirects = True)
        self.assertEqual(response.status_code, 200)

        # bytes_q_content = bytes(q.content, 'utf-8')
        # bytes_q_soln = bytes(q.solution, 'utf-8')
        # bytes_q_points = bytes('{} Marks'.format(q.points), 'utf-8')
        # self.assertEqual(len(paper.paper_questions), 1)
        # self.assertTrue(bytes_q_content in response)

    def test_solutions(self):
        course = Course.query.first()
        paper = Paper.query.first()
        q = Question(content = 'New Question', solution = 'New Solution', points = 5, course_id = course.id)
        db.session.add(q)
        db.session.commit()
        pq = PaperQuestion(paper_id = paper.id, question_id = q.id, order_number = 1)
        db.session.add(pq)
        db.session.commit()
        response = self.client.get('/course/{}/paper/{}/solutions_printable'.format(course.id, paper.id), follow_redirects = True)
        self.assertEqual(response.status_code, 200)






if __name__ == '__main__':
    unittest.main()
