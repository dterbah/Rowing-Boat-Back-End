import sys
sys.path.append('../')
import os
from flask_restful import Resource
from flask import Flask, request

from datetime import datetime

class SignUpRoute(Resource):
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

