"""
This file contains general methods for all tests
"""
from app.models import User
import unittest
from app import create_app
from mongoengine import connect, disconnect


class GeneralTestCase(unittest.TestCase):

    def setUp(self):
        """
        Initializes application in testing config
        """
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        disconnect()
        connect('mongoenginetest', host='mongomock://localhost')
        self.client = self.app.test_client()

    def tearDown(self):
        """
        Tears down application after testing is complete
        """
        disconnect()
        self.app_context.pop()


    def get_api_headers(self):
        """
        Creates headers for sending requests to api
        """
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_user(self, write_access=0):
        """
        Creates a new user and their token
        """
        token = "token" + str(write_access)
        user = User(
                    Email='test@gmail.com',
                    Token=token,
                    Permission=write_access
                )
        return user, token