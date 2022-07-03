"""
This file contains models of all collections + embedded documents
housed within the MongoDB cluster. 
"""
from . import db 
from datetime import datetime


class Location(db.EmbeddedDocument):
    CBSA_Code = db.IntField()
    City = db.StringField()
    State = db.StringField()
    Lat = db.FloatField(required=True)
    Long = db.FloatField(required=True)
    Population = db.IntField()
    Density = db.IntField()
    Timezone = db.StringField()
    Site_Name = db.StringField()
    Full_AQSID = db.StringField()



class Historic(db.Document):

    meta = {
        'collection': 'historic-data'
    }

    Date = db.StringField(required=True)
    AQI = db.IntField(required=True)
    Category = db.StringField(required=True)
    Defining_Parameter = db.StringField()
    Number_of_Sites_Reporting = db.IntField()
    Location = db.EmbeddedDocumentField(Location, required=True)



class Current(db.Document):

    meta = {
        'collection': 'current'
    }

    Date = db.StringField(required=True)
    AQI = db.IntField(required=True)
    Category = db.StringField(required=True)
    Defining_Parameter = db.StringField()
    Location = db.EmbeddedDocumentField(Location, required=True)



class Prediction(db.EmbeddedDocument):
    Days_in_Advance = db.IntField(required=True)
    Pred_AQI = db.IntField(required=True)
    Pred_Category = db.StringField(required=True)



class Forecast(db.Document):

    meta = {
        'collection': 'forecast'
    }

    Date = db.StringField(required=True)
    Real_AQI = db.IntField(default=-1)
    Real_Category = db.StringField(default='N/A')
    Predictions = db.ListField(db.EmbeddedDocumentField(Prediction), required=True)
    Location = db.EmbeddedDocumentField(Location, required=True)


class User(db.Document):

    meta = {
        'collection': 'users'
    }

    Email = db.EmailField(required=True)
    Token = db.StringField(required=True)
    Date_Joined = db.DateTimeField(default=datetime.utcnow(), required=True)
    Permission = db.IntField(default=0, required=True)
    Last_Email = db.DateTimeField(default=datetime.utcnow(), required=True)



class Request(db.Document):

    meta = {
        'collection': 'requests'
    }

    User_Token = db.StringField(required=True)
    Resource = db.StringField(required=True)
    Time_Used = db.DateTimeField(default=datetime.utcnow(), required=True)

  




   