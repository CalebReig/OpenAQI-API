"""
This file initializes the 'forecasts' blueprint and injects some functions to use in jinja2
"""
from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

from . import current_aqi, historic_aqi, forecasts, model_prediction, model_data, new_user