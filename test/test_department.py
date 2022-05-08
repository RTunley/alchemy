import os
os.environ['ALCHEMY_CONFIG'] = 'TestConfig'
from alchemy import application as app

from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Department
import test.create_test_objects as cto

class DepartmentTestCase(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        test_department = cto.create_department()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    #Ensure that flask was set up correctly
    def test_index(self):
        department = Department.query.first()
        response = self.client.get('/department/{}'.format(department.id), follow_redirects = True)
        self.assertEqual(response.status_code, 200)

    #Check that the department homepage contains correct data
    def test_department_home(self):
        department = Department.query.first()
        response = self.client.get('/department/{}'.format(department.id), follow_redirects = True)
        department_home_body = b"This is the department homepage - But there's nothing interesting here yet."
        department_home_header = b"Alchemy:"
        department_home_false = b"We will never put these words on the home page"
        self.assertTrue(department_home_body in response.data)
        self.assertTrue(department_home_header in response.data)
        self.assertFalse(department_home_false in response.data)

if __name__ == '__main__':
    unittest.main()
