"""
This file contains all methods for the '/model-data' api resource
Possible requests
--------------------------
-POST: Given datetime/location parameters, returns the last 30 days of 
aqi values for the given dates/locations
"""
from flask import jsonify, request, make_response
from . import api
from ..models import Historic
from mongoengine.queryset.visitor import Q
from ..http_status import HttpStatus
from ..decorators import *
from .general_resource import GeneralResource
from ..schema import ModelDataSchema
from marshmallow import ValidationError



class ModelData(GeneralResource):

    @token_required_write
    def post(self):
        self.make_request('/model-data:POST')
        data = request.get_json()
        if not data:
            response = {'message': 'No input data provided'}
            return make_response(response, HttpStatus.bad_request_400.value)

        try:
            ModelDataSchema(many=True).load(data)
        except ValidationError as err:
            return make_response({'message': 'Incorrect data format'}, HttpStatus.bad_request_400.value)

        model_data = []
        for d in data:
            query = list(Historic.objects(
                            Q(Date__gte=d['Start']) \
                            & Q(Date__lte=d['End']) \
                            & Q(Location__Lat=d['Location']['Lat']) \
                            & Q(Location__Long=d['Location']['Long']) 
                            ).hint([('Date', 1), ('Location.Lat', 1), ('Location.Long', 1)]))
            model_data += query

        response =  jsonify(model_data)
        return make_response(response, HttpStatus.ok_200.value)



api.add_resource(ModelData, '/model-data')