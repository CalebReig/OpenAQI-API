"""
This file contains all methods for the '/predict' api resource
Possible requests
--------------------------
-POST: Given AQI data for the past 30 days, returns ML model predictions
"""
from flask import request, make_response
from . import api
from ..decorators import *
from ..http_status import HttpStatus
import numpy as np
from .. import forecast_model
from .general_resource import GeneralResource
from ..schema import ModelPredictSchema
from marshmallow import ValidationError


class ModelPrediction(GeneralResource):

    def __init__(self):
        super().__init__()
        self.AQI_MEAN = 43.467599332161555
        self.AQI_STD = 22.21508718833175

    def preprocess(self, data):
        """
        Standardizes the given data to have mean of ~0 and standard deviation of ~1
        """
        preprocessed_data = ( np.array(data) - self.AQI_MEAN ) / self.AQI_STD
        preprocessed_data = preprocessed_data.reshape(len(data), 30, 1)
        return preprocessed_data

    def postprocess(self, data):
        """
        Converts predicted values to scale between 0-500
        """
        postprocessed_data = data * self.AQI_STD + self.AQI_MEAN
        postprocessed_data = postprocessed_data.astype('int').tolist()
        return postprocessed_data

    @token_required_write
    def post(self):
        self.make_request('/predict:POST')
        data = request.get_json()
        if not data:
            response = {'message': 'No input data provided'}
            return make_response(response, HttpStatus.bad_request_400.value)
        
        try:
            ModelPredictSchema().load(data)
        except ValidationError as err:
            return make_response({'message': 'Incorrect data format'}, HttpStatus.bad_request_400.value)
        
        preprocessed_data = self.preprocess(data['data'])
        predictions = forecast_model.predict(preprocessed_data)
        postprocessed_data = self.postprocess(predictions)

        return make_response({'Predictions': postprocessed_data}, HttpStatus.ok_200.value)
        


api.add_resource(ModelPrediction, '/predict')