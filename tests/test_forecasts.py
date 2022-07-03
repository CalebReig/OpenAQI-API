"""
This file contains application tests for '/forecasts' api resources
"""
from app.http_status import HttpStatus
from app.models import Forecast, Location, Prediction
import json
from datetime import datetime, timedelta
from general_test import GeneralTestCase

class ForecastTestCase(GeneralTestCase):

    def setUp(self):
        """
        Initializes application in testing config
        """
        super().setUp()
        self.uri = '/api/v1/forecasts'
    

    def test_get(self):
        """
        Tests the GET method for the '/forecasts' endpoint
        """
        #test resource cannot be accessed without token
        response = self.client.get(self.uri)
        self.assertEquals(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test resource cannot be access with invalid token
        response = self.client.get(self.uri + "?token=invalid")
        self.assertEquals(response.status_code, HttpStatus.method_not_allowed_405.value)

        #insert default data (returns when no parameters given)
        location = Location(Lat=39, Long=-75)
        prediction = Prediction(Days_in_Advance=1, Pred_AQI=5)
        default_data = Forecast(
                                Date=(datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d'), 
                                Predictions=[prediction],
                                Location=location
                                )
        Forecast.objects().insert(default_data)

        #test resource can be accessed with valid token and no additional parameters
        user, token = self.get_user(write_access=0)
        user.save()
        response = self.client.get(self.uri + f'?token={token}')
        self.assertEquals(response.status_code, HttpStatus.ok_200.value)

        #test that default data is returned
        default_data_was_returned = response.get_json()[0]['Predictions'][0]['Pred_AQI'] == 5
        self.assertTrue(default_data_was_returned)

        #insert customdata (will not return when no parameters given -- needs parameters)
        location = Location(Lat=0, Long=0)
        prediction = Prediction(Days_in_Advance=1, Pred_AQI=100)
        custom_data = Forecast(
                                Date=(datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d'), 
                                Predictions=[prediction],
                                Location=location
                                )
        Forecast.objects().insert(custom_data)

        #test resource can be accessed with valid token and additional parameters
        bLat, tLat = -1, 1
        lLong, rLong = -1, 1

        response = self.client.get(self.uri + \
            f'?token={token}&bLat={bLat}&tLat={tLat}&lLong={lLong}&rLong={rLong}')
        self.assertEquals(response.status_code, HttpStatus.ok_200.value)

        #test that default data is returned
        custom_data_was_returned = response.get_json()[0]['Predictions'][0]['Pred_AQI'] == 100
        self.assertTrue(custom_data_was_returned)

    def test_post(self):
        """
        Tests the POST method for the '/forecasts' endpoint
        """
        valid_data = {
                "Date": "2030-01-01",
                "Predictions": {"Days_in_Advance": 7, "Pred_AQI": 55},
                "Location": {"Lat": 12, "Long": 40}
        }
        invalid_data = {
                "Date": 10,
                "Invalid": -1
        }

        #test resource cannot be accessed without token
        response = self.client.post(
                                    self.uri,
                                    headers=self.get_api_headers(),
                                    data=json.dumps([valid_data])
                                )
        self.assertEquals(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test resource cannot be access with invalid token
        response = self.client.post(
                                    self.uri + "?token=invalid",
                                    headers=self.get_api_headers(),
                                    data=json.dumps([valid_data])
                                )
        self.assertEquals(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test resource cannot be accessed with valid read-only token
        user_without_write, token_without_write = self.get_user(write_access=0)
        user_without_write.save()
        response = self.client.post(
                                    self.uri + f"?token={token_without_write}",
                                    headers=self.get_api_headers(),
                                    data=json.dumps([valid_data])
                                )
        self.assertEquals(response.status_code, HttpStatus.forbidden_403.value)

        #test resource can be accessed with valid write access token,
        #but will send bad status if data is invalid format
        user_with_write, token_with_write = self.get_user(write_access=1)
        user_with_write.save()
        response = self.client.post(
                                    self.uri + f"?token={token_with_write}",
                                    headers=self.get_api_headers(),
                                    data=json.dumps([invalid_data])
                                )
        self.assertEquals(response.status_code, HttpStatus.bad_request_400.value)

        #test resource can be accessed with valid write access token,
        #and will send a good status if data is valid format,
        #and data is stored in the db
        response = self.client.post(
                            self.uri + f"?token={token_with_write}",
                            headers=self.get_api_headers(),
                            data=json.dumps([valid_data])
                        )
        self.assertEquals(response.status_code, HttpStatus.ok_200.value)

        forecast_data_exists = Forecast.objects().first() is not None
        self.assertTrue(forecast_data_exists)

    def test_patch(self):
        """
        Tests the PATCH method for the '/forecasts' endpoint
        """
        valid_data_predictions = {
            'Predictions': [{
                "Date": "2030-01-01",
                "Predictions": {"Days_in_Advance": 1, "Pred_AQI": 55},
                "Location": {"Lat": 12, "Long": 40}
        }]
        }
        invalid_data_predictions = {
            'Predictions': [{'Invalid': -1, "Date": "2030-01-01"}]
        }
        valid_data_actual = {
            'Actual': [{
            "Date": "2030-01-01",
            "AQI": 18,
            "Category": "Good",
            "Defining_Parameter": "PM2.5",  
            "Location": {
                    "Lat": 12,    
                    "Long": 40
                    }
        }]
        }
        invalid_data_actual = {
            'Actual': [{'Invalid': -1, "Date": "2030-01-01"}]
        }
        #test resource cannot be accessed without token
        response = self.client.patch(
                            self.uri,
                            headers=self.get_api_headers(),
                            data=json.dumps(valid_data_predictions)
                        )
        self.assertEquals(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test resource cannot be access with invalid token
        response = self.client.patch(
                    self.uri + '?token=invalid',
                    headers=self.get_api_headers(),
                    data=json.dumps(valid_data_predictions)
                )
        self.assertEquals(response.status_code, HttpStatus.method_not_allowed_405.value)

        #test resource cannot be accessed with valid read-only token
        user_without_write, token_without_write = self.get_user(write_access=0)
        user_without_write.save()

        response = self.client.patch(
                    self.uri + f"?token={token_without_write}",
                    headers=self.get_api_headers(),
                    data=json.dumps(valid_data_predictions)
                )
        self.assertEquals(response.status_code, HttpStatus.forbidden_403.value)

        #Create some data to patch~
        prediction = Prediction(Days_in_Advance=7, Pred_AQI=55)
        location = Location(Lat=12, Long=40)
        forecast = Forecast(Date="2030-01-01", Predictions=[prediction], Location=location)
        Forecast.objects.insert(forecast)

        forecast_exists = Forecast.objects().first() is not None
        self.assertTrue(forecast_exists)

        predictions_length_is_1 = len(Forecast.objects().first().Predictions) == 1
        self.assertTrue(predictions_length_is_1)

        #test resource can be accessed with valid write access token,
        #but will send bad status if data is invalid format (Prediction Path)
        user_with_write, token_with_write = self.get_user(write_access=1)
        user_with_write.save()

        response = self.client.patch(
                            self.uri + f"?token={token_with_write}",
                            headers=self.get_api_headers(),
                            data=json.dumps(invalid_data_predictions)
                        )
        self.assertEquals(response.status_code, HttpStatus.bad_request_400.value)


        #test resource can be accessed with valid write access token,
        #and will send a good status if data is valid format,
        #and data is stored in the db (Prediction Path)
        response = self.client.patch(
                    self.uri + f"?token={token_with_write}",
                    headers=self.get_api_headers(),
                    data=json.dumps(valid_data_predictions)
                )
        self.assertEquals(response.status_code, HttpStatus.ok_200.value)

        #check if existing data was updated with another prediciton
        predictions_length_is_2 = len(Forecast.objects().first().Predictions) == 2
        self.assertTrue(predictions_length_is_2)

        
        #test resource can be accessed with valid write access token,
        #but will send bad status if data is invalid format (Actual Path)
        response = self.client.patch(
                            self.uri + f"?token={token_with_write}",
                            headers=self.get_api_headers(),
                            data=json.dumps(invalid_data_actual)
                        )
        self.assertEquals(response.status_code, HttpStatus.bad_request_400.value)

        #test resource can be accessed with valid write access token,
        #and will send a good status if data is valid format,
        #and data is stored in the db (Actual Path)
        response = self.client.patch(
                            self.uri + f"?token={token_with_write}",
                            headers=self.get_api_headers(),
                            data=json.dumps(valid_data_actual)
                        )
        self.assertEquals(response.status_code, HttpStatus.ok_200.value)

        #check if existing data was updated with actual AQI values
    
        actual_aqi_exists = Forecast.objects().first().Real_AQI > -1
        self.assertTrue(actual_aqi_exists)