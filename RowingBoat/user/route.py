import sys
sys.path.append('../')
import os
import jwt
from functools import wraps

from flask_restful import Resource
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from middleware.token_required import token_required

class UserSignUpSignIn(Resource):
    # Route for Sign up
    def post(self):
        from database.models import User
        from RowingBoat import bcrypt
        from RowingBoat import db

        user = None
        error_response = {
            'success': False
        }

        success_response = {
            'success': True,
            'message': 'Account successfully created !'
        }
        
        data = request.form.to_dict()

        # Lastname
        if not 'lastname' in data:
            error_response['message'] = "The lastname is missing"
            return error_response

        lastname = data['lastname']
        
        # Firstname
        if not 'firstname' in data:
            error_response['message'] = "The firstname is missing"
            return error_response
            
        firstname = data['firstname']
        
        # Email
        if not 'email' in data:
            error_response['message'] = "The email is missing"
            return error_response
        
        email = data['email']
        user = User.query.filter_by(email=email).first()
        if user != None:
            # The email is already used
            error_response['message'] = f'The email "{email}" is not available.'
            return error_response

        # Password
        if not 'password' in data:
            error_response['message'] = 'The password is missing'
            return error_response

        password = data['password']
        encrypted_password = bcrypt.generate_password_hash(password)

        # Is Admin
        is_admin = False
        if 'is_admin' in data:
            is_admin = request.form.is_admin

        is_account_valid = False
        if is_admin:
            is_account_valid = True

        # Birth data
        if not 'birth_date' in data:
            error_response['message'] = 'The birth date is missing'
            return error_response

        birth_date = data['birth_date']
        formatted_birth_date = datetime.strptime(birth_date, "%d/%m/%Y")

        user = User(lastname=lastname,
                    firstname=firstname,
                    password=encrypted_password,
                    email=email,
                    birth_date=formatted_birth_date,
                    is_admin=is_admin,
                    is_account_valid=is_account_valid
        )

        db.session.add(user)
        db.session.commit()

        return success_response

    def get(self):
        from database.models import User
        from RowingBoat import db
        from RowingBoat.config import Config

        config = Config()
        user = None
        error_response = {
            'success': False
        }

        data = request.form.to_dict()

        if not 'email' in data:
            error_response['message'] = 'The email is missing'
            return error_response

        email = data['email']

        if not 'password' in data:
            error_response['message'] = 'The password is missing'
            return error_response

        password = data['password']

        user = User.query.filter_by(email=email).first()
        if user == None:
            error_response['message'] = f'The email {email} does not exist'
            return error_response

        # check the password
        if (not bcrypt.check_password_hash(user.password, password)):
            error_response['message'] = 'The password is not correct'
            return error_response

        # Create the token
        token = jwt.encode({'user_id' : user.user_id, 'exp' : datetime.utcnow() + timedelta(minutes=300)}, config.SECRET_KEY, "HS256")
        return {
            'token': token
        }

    @token_required
    def patch(user, self):
        from RowingBoat import db
        from RowingBoat import bcrypt

        data = request.form.to_dict()

        email = data['email'] if 'email' in data else user.email
        lastname = data['lastname'] if 'lastname' in data else user.lastname
        firstname = data['firstname'] if 'firstname' in data else user.firstname
        password = bcrypt.generate_password_hash(data['password']) if 'password' in data else user.password

        user.email = email
        user.lastname = lastname
        user.firstname = firstname
        user.password = password

        db.session.commit()

        return {
            'success': True,
            'message': 'Account updated successfully'
        }

class UserProfile(Resource):
    @token_required
    def get(user, self):
        return {
            'success': True,
            'data': user.to_json()
        }