"""
This file contains all custom decorators
"""
from functools import wraps
from flask import request, make_response
from .models import User
from .http_status import HttpStatus


def token_required_read(f):
    """
    Confirms the user provided a valid token
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return make_response({'message': 'Token is missing'}, HttpStatus.method_not_allowed_405.value)
        
        user_exists = User.objects(Token=token).hint([('Token', 1)]).count() == 1
        if not user_exists:
            return make_response({'message': 'User with this token does not exist'}, HttpStatus.method_not_allowed_405.value)
        
        return f(*args, **kwargs)
    return decorated


def token_required_write(f):
    """
    Confirms the user provided a valid token and has 'write' access
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return make_response({'message': 'Token is missing'}, HttpStatus.method_not_allowed_405.value)

        user = User.objects(Token=token).hint([('Token', 1)])       
        user_exists = user.count() == 1
        if not user_exists:
            return make_response({'message': 'User with this token does not exist'}, HttpStatus.method_not_allowed_405.value)
        
        if user[0].Permission != 1:
            return make_response({'message': 'You do not have permission to access this resource'}, HttpStatus.forbidden_403.value)

        return f(*args, **kwargs)
    return decorated
        
        


