"""
This file contains all methods for the '/new-user' api resource
Possible requests
--------------------------
-POST: Creates a new user, generates API token and emails user with token
"""
from flask import request, current_app, make_response
from datetime import datetime, timedelta
from . import api
from ..models import User
from ..email import send_email
from ..http_status import HttpStatus
from ..decorators import *
from .general_resource import GeneralResource
import jwt
from ..schema import NewUserSchema
from marshmallow import ValidationError



class NewUser(GeneralResource):

    @token_required_read
    def post(self):

        self.make_request('/new-user:POST')
        data = request.get_json()

        if not data:
            response = {'message': 'No input data provided'}
            return make_response(response, HttpStatus.bad_request_400.value)

        try:
            NewUserSchema().load(data)
        except ValidationError as err:
            return make_response({'message': 'Incorrect data format'}, HttpStatus.bad_request_400.value)
        
        #checks if the user email already exists in the db and, if yes, sends their email their token
        old_user = User.objects(Email=data['email']).hint([('Email', 1)])
        if old_user.count() == 1:
            last_email = old_user[0].Last_Email
            print(last_email)
            delta = datetime.utcnow() - last_email
            if delta < timedelta(hours=24):
                return make_response({'message': 'Email already sent within the last 24 hours. Please check your email.'},
                                         HttpStatus.expectation_failed_417.value)

            token = old_user[0].Token
            send_email(
                        to=data['email'],
                        subject='OpenAQI Retrieve API Token',
                        token=token
                      )
            old_user[0].update(Last_Email=datetime.utcnow().strftime('%Y-%m-%d'))

            return make_response({'message': 'Existing User - An email with the token has been sent.'}, HttpStatus.ok_200.value)
            
        
        #if the email is not registered, create a new user, token and send an email
        token = jwt.encode({'user': data['email']}, current_app.config['SECRET_KEY'], algorithm="HS256")        
        new_user = User(
                        Email=data['email'],
                        Token=token,
                        Permission=0
                        )
        User.objects.insert(new_user)
        
        send_email(
                    to=data['email'],
                    subject='OpenAQI API Token Request',
                    token=token
                    )

        return make_response({'message': 'New User - An email with the token has been sent.'}, HttpStatus.ok_200.value)


api.add_resource(NewUser, '/new-user')