"""
This file contains all methods for the '/current' api resource
Possible requests
--------------------------
-GET: Gets all aqi values from the current collection
-POST: Adds new AQI values to the current collection (only posts most recent AQI values)
-DELETE: Deletes all documents in the current collection
"""
from flask import jsonify, request, make_response
from . import api
from .. import cache
from ..models import Location, Current
from ..http_status import HttpStatus
from ..decorators import *
from .general_resource import GeneralResource
from ..schema import AQIMeasurementSchema
from marshmallow import ValidationError


class CurrentAQI(GeneralResource):

    @token_required_read
    @cache.cached(timeout=3600)
    def get(self):
        self.make_request('/current:GET')
        data = list(Current.objects())
        response = jsonify(data)
        return make_response(response, HttpStatus.ok_200.value)

    @token_required_write
    def post(self):
        self.make_request('/current:POST')
        data = request.get_json()
        if not data:
            return  make_response({'message': 'No input data provided'}, HttpStatus.bad_request_400.value)
        
        try:
            AQIMeasurementSchema(many=True).load(data)
        except ValidationError as err:
            return make_response({'message': 'Incorrect data format'}, HttpStatus.bad_request_400.value)


        curr_objs = [Current(
                            Date=d['Date'],
                            Defining_Parameter=d['Defining_Parameter'], 
                            AQI=d['AQI'], 
                            Category=self.get_category(d['AQI']), 
                            Location=Location(
                              Full_AQSID=d['Location']['Full_AQSID'],
                              Site_Name=d['Location']['Site_Name'],
                              Lat=d['Location']['Lat'],
                              Long=d['Location']['Long'])
                    ) for d in list(data)]
        Current.objects.insert(curr_objs)

        return make_response({'message': 'Insert successful'}, HttpStatus.ok_200.value)

    @token_required_write
    def delete(self):
        self.make_request('/current:DELETE')
        cache.clear()
        Current.objects().delete()
        return make_response({'message': 'Delete successful'}, HttpStatus.ok_200.value)


api.add_resource(CurrentAQI, '/current')