"""
This file contains application tests for '/historic-data' api resources
"""
from app.http_status import HttpStatus
from app.models import User, Historic, Location
from app import create_app
import unittest
from mongoengine import connect, disconnect
import json
from general_test import GeneralTestCase

class HistoricDataTestCase(GeneralTestCase):

    def setUp(self):
        """
        Initializes application in testing config
        """
        super().setUp()
        self.uri = '/api/v1/historic-data'

    def test_get(self):
        """
        Tests the GET method for the '/histoic-data' endpoint
        """
        #test resource cannot be accessed without token
        response = self.client.get(self.uri)
        self.assertEquals(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test resource cannot be access with invalid token
        response = self.client.get(self.uri + "?token=invalid")
        self.assertEquals(response.status_code, HttpStatus.method_not_allowed_405.value)


        #insert default data (returns when no parameters given)
        location = Location(Lat=39, Long=-75)
        default_data = Historic(
                                Date="2021-08-01", 
                                AQI=5, Category="Good", 
                                Defining_Parameter="PM10",
                                Location=location
                                )
        Historic.objects().insert(default_data)

        #test resource can be accessed with valid token and no additional parameters
        user, token = self.get_user(write_access=0)
        user.save()
        response = self.client.get(self.uri + f'?token={token}')
        self.assertEquals(response.status_code, HttpStatus.ok_200.value)

        #test that default data is returned
        default_data_was_returned = response.get_json()[0]['AQI'] == 5
        self.assertTrue(default_data_was_returned)

        #insert customdata (will not return when no parameters given -- needs parameters)
        location = Location(Lat=0, Long=0)
        custom_data = Historic(
                                Date="2020-01-01", 
                                AQI=100, Category="Moderate", 
                                Defining_Parameter="PM10",
                                Location=location
                                )
        Historic.objects().insert(custom_data)

        #test resource can be accessed with valid token and additional parameters
        start, end = "2020-01-01", "2020-01-01"
        bLat, tLat = -1, 1
        lLong, rLong = -1, 1

        response = self.client.get(self.uri + \
            f'?token={token}&start={start}&end={end}&bLat={bLat}&tLat={tLat}&lLong={lLong}&rLong={rLong}')
        self.assertEquals(response.status_code, HttpStatus.ok_200.value)

        #test that default data is returned
        custom_data_was_returned = response.get_json()[0]['AQI'] == 100
        self.assertTrue(custom_data_was_returned)


    def test_post(self):
        """
        Tests the POST method for the '/forecasts' endpoint
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

        current_data_exists = Historic.objects().first() is not None
        self.assertTrue(current_data_exists)