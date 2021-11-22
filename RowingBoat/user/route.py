import sys
sys.path.append('../')
import os
import jwt
from functools import wraps

from distutils.util import strtobool

from flask_restful import Resource
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from middleware import token_required

from flask_cors import cross_origin

class UserRegister(Resource):
    # Route for Sign up
    @cross_origin()
    def post(self):
        from database.models import User, STRING_CONSTANTS_USER, USER_GENDER
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
            is_admin = strtobool(data['is_admin'])


        is_account_valid = False
        if is_admin:
            is_account_valid = True

        # Age data
        if not 'age' in data:
            error_response['message'] = 'The age is missing'
            return error_response

        age = data['age']

        # Phone number
        if not 'phoneNumber' in data:
            error_response['message'] = 'The phone number is missing'
            return error_response

        phoneNumber = data['phoneNumber']

        # Ambitions 
        if not 'ambitions' in data:
            error_response['message'] = 'The ambitions are missing'
            return error_response

        ambitions = data['ambitions'].upper()
        if not ambitions in STRING_CONSTANTS_USER:
            error_response['message'] = f'The value "{ambitions}" for ambitions is not correct'
            return error_response

        # Fitness
        if not 'fitness' in data:
            error_response['message'] = 'The fitness is missing'
            return error_response

        fitness = data['fitness'].upper()
        if not fitness in STRING_CONSTANTS_USER:
            error_response['message'] = f'The value "{fitness}" for fitness is not correct'
            return error_response

        # Skill level
        if not 'skill_level' in data:
            error_response['message'] = 'The skill level is missing'
            return error_response

        skill_level = data['skill_level'].upper()
        if not ambitions in STRING_CONSTANTS_USER:
            error_response['message'] = f'The value "{skill_level}" for the skill level is not correct'
            return error_response

        # Gender
        if not 'gender' in data:
            error_response['message'] = 'The gender is missing'
            return error_response

        gender = data['gender'].upper()
        if not gender in USER_GENDER:
            error_response['message'] = f'The value "{gender}" for the gender is not correct'
            return error_response

        user = User(lastname=lastname,
                    firstname=firstname,
                    password=encrypted_password,
                    email=email,
                    age=age,
                    phoneNumber=phoneNumber,
                    is_admin=is_admin,
                    is_account_valid=is_account_valid,
                    gender=USER_GENDER[gender],
                    fitness=STRING_CONSTANTS_USER[fitness],
                    skill_level=STRING_CONSTANTS_USER[skill_level],
                    ambitions=STRING_CONSTANTS_USER[ambitions]
        )

        db.session.add(user)
        db.session.commit()

        return success_response

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

class UserLogin(Resource):
    
    def post(self):
        from database.models import User
        from RowingBoat import db
        from RowingBoat import bcrypt
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
            'token': token,
            'is_admin': user.is_admin,
            'success': True
        }

class BookingDelete(Resource):
    @token_required
    def delete(current_user, self, booking_id):
        from datababe.models import Booking
        from RowingBoat import db
        
        error_response = {
            'success': False
        }

        booking = Booking.query.filter_by(booking_id=booking_id)
        if booking == None:
            error_response['message'] = f'No booking exists with booking ID : {booking_id}'
            return error_response

        db.session.delete(booking)
        db.session.commit()

        return {
            'success': True,
            'message': 'The booking was successfully deleted'
        }