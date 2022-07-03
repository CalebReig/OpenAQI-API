"""
This file contains application tests for basic tests
"""
import unittest
from flask import current_app
from general_test import GeneralTestCase

class BasicsTestCase(GeneralTestCase):
    """
    This class tests the initializes a test config application and runs basic tests
    """

    def test_app_exists(self):
        """
        Tests that the application exists/was created successfully
        """
        self.assertFalse(current_app is None)


    def test_app_is_testing(self):
        """
        Tests that the application is in testing configuration
        """
        self.assertTrue(current_app.config['TESTING'])