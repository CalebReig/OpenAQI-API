"""
This file contains application tests for '/current' api resources
"""
from app.http_status import HttpStatus
from app.models import Current, Location
import json
from general_test import GeneralTestCase


class CurrentTestCase(GeneralTestCase):

    def setUp(self):
        """
        Initializes application in testing config
        """
        super().setUp()
        self.uri = '/api/v1/current'
    
    #Test POST
    def test_post(self):
        """
        Tests the POST method for the '/current' endpoint
        """
        valid_data = {
            "Date": "2022-06-29",
            "AQI": 18,
            "Category": "Good",
            "Defining_Parameter": "PM2.5",  
            "Location": {
                    "Lat": 46.2406,    
                    "Long": -63.1306,    
                    "Site_Name": "CHARLOTTETOWN",    
                    "Full_AQSID": "124000020104"  
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

        current_data_exists = Current.objects().first() is not None
        self.assertTrue(current_data_exists)
       

    #Test GET
    def test_get(self):
        """
        Tests the GET method for the '/current' endpoint
        """
        #test data cannot be queried without token
        response = self.client.get(self.uri)
        self.assertEquals(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test data cannot be queried with invalid token
        response = self.client.get(self.uri + "?token=invalid")
        self.assertEquals(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test data can be queried with valid token
        user_without_write, token_without_write = self.get_user(write_access=0)
        user_without_write.save()
        response = self.client.get(self.uri + f"?token={token_without_write}")
        self.assertEqual(response.status_code, HttpStatus.ok_200.value)


    #Test DELETE
    def test_delete(self):
        """
        Tests the DELETE method for the '/current' endpoint
        """
        #test data cannot be deleted with no token
        response = self.client.delete(self.uri)
        self.assertEquals(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test data cannot be deleted with invalid token
        response = self.client.delete(self.uri + "?token=invalid")
        self.assertEquals(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test data cannot be deleted with token without write access
        user_without_write, token_without_write = self.get_user(write_access=0)
        user_without_write.save()
        response = self.client.delete(self.uri + f"?token={token_without_write}")
        self.assertEquals(response.status_code, HttpStatus.forbidden_403.value)

        #test data can be deleted with a valid token
        user_with_write, token_with_write = self.get_user(write_access=1)
        user_with_write.save()

        location = Location(Lat=12, Long=30)
        data = Current(
            Date="2030-01-01",
            AQI=100,
            Category="Moderate",
            Location=location
        )
        Current.objects.insert(data) #inserts test data

        current_data_exists = Current.objects().first() is not None #checks if data is in db
        self.assertTrue(current_data_exists)

        response = self.client.delete(self.uri+f"?token={token_with_write}")
        self.assertEquals(response.status_code, HttpStatus.ok_200.value)

        
        current_data_not_exists = Current.objects().first() is None #checks if data is deleted
        self.assertTrue(current_data_not_exists)



        



