"""
This file contains application tests for '/predict' api resources
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
        self.uri = '/api/v1/predict'

    def test_post(self):
        """
        Tests the POST method for the '/predict' endpoint
        """
        valid_data = {
              "data": [[24 for i in range(30)], [25 for i in range(30)]]
        }
        invalid_data = {
            "data": [['a' for i in range(30)]]
        }

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
        user_without_write, token_without_write = self.get_user(write_access=0)
        user_without_write.save()
        response = self.client.post(    
                                    self.uri+f'?token={token_without_write}',
                                    headers=self.get_api_headers(),
                                    data=json.dumps(valid_data)
                                    )
        self.assertEqual(response.status_code, HttpStatus.forbidden_403.value)

        #test invalid data cannot be posted with valid token
        
        user_with_write, token_with_write = self.get_user(write_access=1)
        user_with_write.save()
        response = self.client.post(
                                    self.uri+f'?token={token_with_write}', 
                                    headers=self.get_api_headers(),
                                    data=json.dumps(invalid_data)
                                    )
        self.assertEqual(response.status_code, HttpStatus.bad_request_400.value)
        #test data can be posted and exists in db with a valid token
        response = self.client.post(
                                    self.uri+f'?token={token_with_write}', 
                                    headers=self.get_api_headers(),
                                    data=json.dumps(valid_data)
                                    )
        self.assertEqual(response.status_code, HttpStatus.ok_200.value)

        prediction_exists = 'Predictions' in response.get_json()
        self.assertTrue(prediction_exists)