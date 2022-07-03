"""
This file contains application tests for '/model-data' api resources
"""
from app.http_status import HttpStatus
import json
from general_test import GeneralTestCase

class ModelDataTestCase(GeneralTestCase):

    def setUp(self):
        """
        Initializes application in testing config
        """
        super().setUp()
        self.uri = '/api/v1/model-data'
    
    def test_post(self):
        """
        Tests the POST method for the '/model-data' endpoint
        """
        valid_data = {
            "Start": "2021-06-29",
            "End": "2021-07-29",
            "Location": {
                    "Lat": 46.2406,    
                    "Long": -63.1306 
                    }
        }
        invalid_data = {'Invalid': -1, 'AQI': 'abc'}

        #test data cannot be posted with no token
        response = self.client.post(
                                    self.uri, 
                                    headers=self.get_api_headers(),
                                    data=json.dumps([valid_data])
                                    )
        
        self.assertEqual(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test data cannot be posted with invalid token
        response = self.client.post(
                                    self.uri+"?token=invalid",
                                    headers=self.get_api_headers(),
                                    data=json.dumps([valid_data])
                                     )
        
        self.assertEqual(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test data cannot be posted with token without write access
        user_without_write, token_without_write = self.get_user(write_access=0)
        user_without_write.save()
        response = self.client.post(    
                                    self.uri+f'?token={token_without_write}',
                                    headers=self.get_api_headers(),
                                    data=json.dumps([valid_data])
                                    )
        self.assertEqual(response.status_code, HttpStatus.forbidden_403.value)

        #test invalid data cannot be posted with valid token
        
        user_with_write, token_with_write = self.get_user(write_access=1)
        user_with_write.save()
        response = self.client.post(
                                    self.uri+f'?token={token_with_write}', 
                                    headers=self.get_api_headers(),
                                    data=json.dumps([invalid_data])
                                    )
        self.assertEqual(response.status_code, HttpStatus.bad_request_400.value)
        #test data can be posted and exists in db with a valid token
        response = self.client.post(
                                    self.uri+f'?token={token_with_write}', 
                                    headers=self.get_api_headers(),
                                    data=json.dumps([valid_data])
                                    )
        self.assertEqual(response.status_code, HttpStatus.ok_200.value)