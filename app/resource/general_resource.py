"""
This file contains the 'GeneralResource' class 
-- a parent class hosting commonly used class methods
"""
from flask import request
from flask_restful import Resource
from ..models import Request

class GeneralResource(Resource):
    def make_request(self, request_type):
        """
        Updates the 'resource' collection with whatever api resource was used.
        This is primarily used for trend analysis of api usage
        """
        token = request.args.get('token')
        new_request = Request(
                                User_Token=token,
                                Resource=request_type
                            )
        Request.objects.insert(new_request)

    def get_category(self, aqi):
        """
        Bins aqi values into their given categories
        """
        if aqi <= 50:
            return "Good"
        if aqi <= 100:
            return "Moderate"
        if aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        if aqi <= 200:
            return "Unhealthy"
        if aqi <= 300:
            return "Very Unhealthy"
        return "Hazardous"