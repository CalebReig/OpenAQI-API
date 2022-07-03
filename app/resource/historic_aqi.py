"""
This file contains all methods for the '/historic-data' api resource
Possible requests
--------------------------
-GET: Gets historic aqi data based on user given times/locations
-POST: Adds more data do the historic-data collection
"""
from flask import jsonify, request, make_response
from . import api
from ..models import Historic, Location
from ..http_status import HttpStatus
from mongoengine.queryset.visitor import Q
from marshmallow import ValidationError
from ..decorators import *
from .general_resource import GeneralResource
from ..schema import AQIMeasurementSchema, HistoricQuerySchema

class HistoricAQI(GeneralResource):

  @token_required_read
  def get(self):
    self.make_request('/historic-data:GET')
    errors = HistoricQuerySchema().validate(request.args)
    #if the schema is not followed, returns default query (2021/USA-PA region)
    if errors:
      data = list(Historic.objects(
                                  Q(Date__gte="2021-06-30") \
                                  & Q(Date__lte="2021-12-31") \
                                  & Q(Location__Lat__gte=38) \
                                  & Q(Location__Lat__lte=40) \
                                  & Q(Location__Long__gte=-80) \
                                  & Q(Location__Long__lte=-70)) \
                                .hint([('Date', 1), ('Location.Lat', 1), ('Location.Long', 1)]))
    else:
      n_limit = 0
      #limits number of results returned if limit is given
      if ('limit' in request.args) and (request.args['limit']):
        n_limit = 5_000
      data = list(Historic.objects(
                                  Q(Date__gte=request.args['start']) \
                                  & Q(Date__lte=request.args['end']) \
                                  & Q(Location__Lat__gte=request.args['bLat']) \
                                  & Q(Location__Lat__lte=request.args['tLat']) \
                                  & Q(Location__Long__gte=request.args['lLong']) \
                                  & Q(Location__Long__lte=request.args['rLong']) 
                                  ).hint([('Date', 1), ('Location.Lat', 1), ('Location.Long', 1)]).limit(n_limit))
    response =  jsonify(data)
    return make_response(response, HttpStatus.ok_200.value)

  @token_required_write
  def post(self):
      self.make_request('/historic-data:POST')
      data = request.get_json()

      if not data:
          response = {'message': 'No input data provided'}
          return make_response(response, HttpStatus.bad_request_400.value)
      
      try:
          AQIMeasurementSchema(many=True).load(data)
      except ValidationError as err:
          return make_response({'message': 'Incorrect data format'}, HttpStatus.bad_request_400.value)

      hist_objs = [Historic(
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
      Historic.objects.insert(hist_objs)

      return make_response({'message': 'Insert successful'}, HttpStatus.ok_200.value)



api.add_resource(HistoricAQI, '/historic-data', endpoint='historic-data')

