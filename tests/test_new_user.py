"""
This file contains application tests for '/new-user' api resources
"""
from app.http_status import HttpStatus
import json
from general_test import GeneralTestCase


class ModelPredictionTestCase(GeneralTestCase):

    def setUp(self):
        """
        Initializes application in testing config
        """
        super().setUp()
        self.uri = '/api/v1/new-user'

    def test_post(self):
        """
        Tests the POST method for the '/predict' endpoint
        """
        valid_data = {"email": "reigadacaleb@gmail.com" }
        invalid_data = {"email": "this is a fake email"}

        #test data cannot be posted with no token
        response = self.client.post(
                                    self.uri, 
                                    headers=self.get_api_headers(),
                                    data=json.dumps(valid_data)
                                    )
        
        self.assertEqual(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test data cannot be posted with invalid token
        response = self.client.post(
                                    self.uri+"?token=invalid",
                                    headers=self.get_api_headers(),
                                    data=json.dumps(valid_data)
                                     )
        
        self.assertEqual(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test data cannot be posted with token without write access
        user, token = self.get_user(write_access=0)
        user.save()

        response = self.client.post(
                                    self.uri+f'?token={token}', 
                                    headers=self.get_api_headers(),
                                    data=json.dumps(invalid_data)
                                    )
        self.assertEqual(response.status_code, HttpStatus.bad_request_400.value)

        #test data can be posted with a valid token
        response = self.client.post(
                                    self.uri+f'?token={token}', 
                                    headers=self.get_api_headers(),
                                    data=json.dumps(valid_data)
                                    )
        self.assertEqual(response.status_code, HttpStatus.ok_200.value)


        #test that email will not be sent if account created within 24 hrs
        response = self.client.post(
                            self.uri+f'?token={token}', 
                            headers=self.get_api_headers(),
                            data=json.dumps(valid_data)
                            )
        self.assertEqual(response.status_code, HttpStatus.expectation_failed_417.value)

        