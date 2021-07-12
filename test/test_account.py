from alchemy import application as app
from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account
import test.sample_data as data

class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('alchemy.config.TestConfig')
        return app

    def setUp(self):
        db.create_all()
        test_account = Account(name = "Test School")
        db.session.add(test_account)
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

if __name__ == '__main__':
    unittest.main()
