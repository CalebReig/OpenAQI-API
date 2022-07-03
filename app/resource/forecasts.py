"""
This file contains all methods for the '/forecasts' api resource
Possible requests
--------------------------
-GET: Gets forecasted aqi data for the next 7 days based on user given locations
-POST: Adds new predictions to the forecasts collection
-PATCH: Either updates the forecast collection documents with actual aqi values (for model evaluation)
        or will append updated forecasts to existing documents. The action depends on payload keys passsed.
"""
from flask import jsonify, request, make_response
from mongoengine.queryset.visitor import Q
from . import api
from ..models import Location, Prediction, Forecast
from ..http_status import HttpStatus
from marshmallow import ValidationError
from datetime import datetime
from ..decorators import *
from .general_resource import GeneralResource
from ..schema import ForecastQuerySchema, ForecastSchema, AQIMeasurementSchema


class ForecastAQI(GeneralResource):

    @token_required_read
    def get(self):

        self.make_request('/forecasts:GET')
        errors = ForecastQuerySchema().validate(request.args)
        today = datetime.utcnow().strftime('%Y-%m-%d')
        #if schema validation is wrong, will return the default query (USA-PA region)
        if errors:
            data = list(Forecast.objects(
                                        Q(Date__gte=today) \
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
            data = list(Forecast.objects(
                                        Q(Date__gte=today) \
                                        & Q(Location__Lat__gte=request.args['bLat']) \
                                        & Q(Location__Lat__lte=request.args['tLat']) \
                                        & Q(Location__Long__gte=request.args['lLong']) \
                                        & Q(Location__Long__lte=request.args['rLong']) 
                                        ).hint([('Date', 1), ('Location.Lat', 1), ('Location.Long', 1)]).limit(n_limit))
        response =  jsonify(data)
        return make_response(response, HttpStatus.ok_200.value)

    @token_required_write
    def post(self):

        self.make_request('/forecasts:POST')
        data = request.get_json()
        if not data:
            response = {'message': 'No input data provided'}
            return make_response(response, HttpStatus.bad_request_400.value)

        try:
            ForecastSchema(many=True).load(data)
        except ValidationError as err:
            return make_response({'message': 'Incorrect data format'}, HttpStatus.bad_request_400.value)

        forecast_objs = [Forecast(
                        Date=d['Date'],
                        Predictions=[Prediction(
                            Days_in_Advance=d['Predictions']['Days_in_Advance'],
                            Pred_AQI=d['Predictions']['Pred_AQI'],
                            Pred_Category=self.get_category(d['Predictions']['Pred_AQI'])
                            )],
                        Location=Location(
                            Lat=d['Location']['Lat'],
                            Long=d['Location']['Long']
                            )
                        ) 
                        for d in list(data)]

        Forecast.objects.insert(forecast_objs)
        return make_response({'message': 'Insert successful'}, HttpStatus.ok_200.value)
    
    @token_required_write
    def patch(self):

        self.make_request('/forecasts:PATCH')
        data = request.get_json()
        if not data:
            response = {'message': 'No input data provided'}
            return make_response(response, HttpStatus.bad_request_400.value)

        # if 'Prediction' in payload key will append updated predictions to existing documents
        if 'Predictions' in data:
            try:
                ForecastSchema(many=True).load(data['Predictions'])
            except ValidationError as err:
                return make_response({'message': 'Incorrect data format'}, HttpStatus.bad_request_400.value)

            for d in data['Predictions']:
                forecast = Forecast.objects(Q(Date=d['Date']) \
                                        & Q(Location__Lat=d['Location']['Lat']) \
                                        & Q(Location__Long=d['Location']['Long'])
                                        ).hint([('Date', 1), ('Location.Lat', 1), ('Location.Long', 1)])
                prediction = Prediction(Days_in_Advance=d['Predictions']['Days_in_Advance'], 
                                        Pred_AQI=d['Predictions']['Pred_AQI'], 
                                        Pred_Category=self.get_category(d['Predictions']['Pred_AQI']))
                if forecast.count() > 0:
                    forecast.update_one(push__Predictions=prediction)

        # if 'Actual' in payload key will update real aqi values to old forecasts
        if 'Actual' in data:

            try:
                AQIMeasurementSchema(many=True).load(data['Actual'])
            except ValidationError as err:
                return make_response({'message': 'Incorrect data format'}, HttpStatus.bad_request_400.value)

            for d in data['Actual']:
                forecast = Forecast.objects(Q(Date=d['Date']) \
                        & Q(Location__Lat=d['Location']['Lat']) \
                        & Q(Location__Long=d['Location']['Long']) 
                            ).hint([('Date', 1), ('Location.Lat', 1), ('Location.Long', 1)])
                if forecast.count() > 0:
                    forecast.update_one(set__Real_AQI=d['AQI'], set__Real_Category=self.get_category(d['AQI']))

        return make_response({'message': 'Insert successful'}, HttpStatus.ok_200.value)

api.add_resource(ForecastAQI, '/forecasts', endpoint='forecasts')