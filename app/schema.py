"""
This file contains schema for validation for all inputs to the api
"""
from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from datetime import datetime


class LocationSchema(Schema):
    #Schema for location sub-document
    Lat = fields.Float(required=True, validate=validate.Range(-90, 90))   
    Long = fields.Float(required=True, validate=validate.Range(-180, 180))

    Site_Name = fields.String(required=False)
    Full_AQSID = fields.String(required=False)
    CBSA_Code = fields.Integer(required=False)
    City = fields.String(required=False)
    State = fields.String(required=False)
    Population = fields.Float(required=False)
    Density = fields.Float(required=False)
    Timezone = fields.String(required=False)

class PredictionSchema(Schema):
    #Schema for Prediction sub-document
    
    Days_in_Advance = fields.Integer(required=True,
                                        validate=validate.Range(1, 7))
    Pred_AQI = fields.Integer(required=True)
    Pred_Category = fields.String(required=False,
                            validate=validate.OneOf(["Good", "Moderate", "Unhealthy for Sensitive Groups", 
                                                    "Unhealthy", "Very Unhealthy", "Hazardous"]))



class AQIMeasurementSchema(Schema):
    #Schema for current collection
    Date = fields.String(required=True)
    AQI = fields.Integer(required=True)
    Category = fields.String(required=False,
                            validate=validate.OneOf(["Good", "Moderate", "Unhealthy for Sensitive Groups", 
                                                    "Unhealthy", "Very Unhealthy", "Hazardous"]))
    Defining_Parameter = fields.String(required=True,
                                        validate=validate.OneOf(["PM10", "PM2.5", "OZONE", "CO", "SO2", "NO2"])) 
    Location = fields.Nested(LocationSchema(), required=True)

    Number_of_Sites_Reporting = fields.Integer(required=False)

class ForecastQuerySchema(Schema):
    #Forecast query schema validation for user GET requests

    token = fields.Str(required=True)
    bLat = fields.Float(required=True, validate=validate.Range(-90, 90))
    tLat = fields.Float(required=True, validate=validate.Range(-90, 90))
    lLong = fields.Float(required=True, validate=validate.Range(-180, 180))
    rLong = fields.Float(required=True, validate=validate.Range(-180, 180))
    limit = fields.Boolean(required=False)
    
    @validates_schema
    def validate_coords(self, data, **kwargs):
        if data["bLat"] > data["tLat"]:
            raise ValidationError("Top latitude must be greater than bottom latitude")
        if data["lLong"] > data["rLong"]:
            raise ValidationError("Right longitude must be greater than left longitude")



class HistoricQuerySchema(ForecastQuerySchema):
    #Query Schema validation for user queries
    start = fields.Str(required=True, 
                        validate=validate.Range("1980-01-01", datetime.utcnow().strftime('%Y-%m-%d')))
    end = fields.Str(required=True, 
                        validate=validate.Range("1980-01-01", datetime.utcnow().strftime('%Y-%m-%d')))

    @validates_schema
    def validate_times(self, data, **kwargs):
        if data["start"] > data["end"]:
            raise ValidationError("Start must be after end")


class ForecastSchema(Schema):
    #schema for forecast collection

    Date = fields.String(required=True)
    Real_AQI = fields.Integer(required=False)
    Real_Category = fields.String(required=False,
                            validate=validate.OneOf(["Good", "Moderate", "Unhealthy for Sensitive Groups", 
                                                    "Unhealthy", "Very Unhealthy", "Hazardous", "N/A"]))
    Predictions = fields.Nested(PredictionSchema(), required=True)
    Location = fields.Nested(LocationSchema, required=True)


class ModelDataSchema(Schema):
    Start = fields.Str(required=True, 
                        validate=validate.Range("1980-01-01", datetime.utcnow().strftime('%Y-%m-%d')))
    End = fields.Str(required=True, 
                        validate=validate.Range("1980-01-01", datetime.utcnow().strftime('%Y-%m-%d')))

    Location = fields.Nested(LocationSchema(), required=True)

    @validates_schema
    def validate_times(self, data, **kwargs):
        if data["Start"] > data["End"]:
            raise ValidationError("Start must be after end")



class ModelPredictSchema(Schema):
    data = fields.List(
                        fields.List(
                                fields.Integer(required=True),
                                    required=True, validate=validate.Length(equal=30)),
                     required=True)

class NewUserSchema(Schema):
    email = fields.Email(required=True)