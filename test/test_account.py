import os
os.environ['ALCHEMY_CONFIG'] = 'TestConfig'
from alchemy import application as app

from alchemy import db
from flask_testing import TestCase
import unittest
from alchemy.models import Account
import test.create_test_objects as cto

class BaseTestCase(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        test_account = cto.create_account()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class FlaskTestCase(BaseTestCase):

    #Ensure that flask was set up correctly
    def test_index(self):
        account = Account.query.first()
        response = self.client.get('/account/{}'.format(account.id), follow_redirects = True)
        self.assertEqual(response.status_code, 200)

    #Check that the account homepage contains correct data
    def test_account_home(self):
        account = Account.query.first()
        response = self.client.get('/account/{}'.format(account.id), follow_redirects = True)
        account_home_body = b"This is the account homepage - But there's nothing interesting here yet."
        account_home_header = b"Alchemy:"
        account_home_false = b"We will never put these words on the home page"
        self.assertTrue(account_home_body in response.data)
        self.assertTrue(account_home_header in response.data)
        self.assertFalse(account_home_false in response.data)

if __name__ == '__main__':
    unittest.main()
