import sys
sys.path.append('../')
import os
import jwt
from functools import wraps

from flask_restful import Resource
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from middleware import token_required
from middleware import check_admin_user
from werkzeug.utils import secure_filename
from utils import allowed_file
from flask import send_file

from flask_cors import cross_origin

class AdminCreateBoat(Resource):
    @token_required
    @check_admin_user
    def post(self, user):
        from database.models import RowingBoat, BOATS_CONDITION, BOAT_TYPE
        from RowingBoat.config import UPLOAD_BOAT_FOLDER
        from RowingBoat import db

        error_response = {
            'success': False
        }

        data = request.form.to_dict()
        
        # Name of the boat
        if not 'name' in data or data['name'].strip() == '':
            error_response['message'] = "The boat's name is missing"
            return error_response

        name = data['name']
        # Check if the name is available
        boat = RowingBoat.query.filter_by(name=name).first()
        if boat != None:
            error_response['message'] = f"The name {name} is already used"
            return error_response

        # Slots of the boats
        if not 'slots' in data or data['slots'].strip() == '':
            error_response['message'] = "The boat's slots are missing"
            return error_response

        slots = int(data['slots'])
        if slots < 1:
            error_response['message'] = f"The value {slots} for the slots is incorrect"
            return error_response

        # Boat class
        if not 'boat_class' in data or data['boat_class'].strip() == '':
            error_response['message'] = "The boat's class is missing"
            return error_response

        boat_class = data['boat_class']

        # boat condition
        if not 'condition' in data or data['boat_class'].strip() == '':
            error_response['message'] = "The condition is missing"
            return error_response
        
        condition = data['condition']
        if not condition in BOATS_CONDITION:
            error_response['message'] = f"The condition {condition} is a bad value"
            return error_response

        # boat type
        if not 'boat_type' in data or data['boat_type'].strip() == '':
            error_response['message'] = "The boat type is missing"
            return error_response

        boat_type = data['boat_type']
        if not boat_type in BOAT_TYPE:
            error_response['message'] = f"The boat type {boat_type} is a bad value"
            return error_response

        # Brand
        if not 'brand' in data:
            error_response['message'] = "The boat's brand is missing"
            return error_response

        brand = data['brand']

        # Built year
        if not 'built_year' in data or data['built_year'].strip() == '':
            error_response['message'] = "The built year is missing"
            return error_response
        
        built_year = data['built_year']

        # Image of the boat
        image_data = request.files.to_dict()
        if not 'image' in image_data:
            error_response['message'] = "The boat's image is missing"
            return error_response

        file = request.files.get('image')
        if file.filename == '':
            error_response['message'] = 'No selected file'
            return error_response

        image_path = ''
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            extension = filename.rsplit('.', 1)[1].lower()
            filename = f'{name}.{extension}'
            print(filename)
            image_path = os.path.join(UPLOAD_BOAT_FOLDER, filename)
            file.save(image_path)

            boat = RowingBoat(slots=slots,
                              name=name,
                              image_path=image_path,
                              boat_class=boat_class,
                              brand=brand,
                              built_year=built_year,
                              boat_type=boat_type,
                              condition=condition
            )

            try:
                db.session.add(boat)
                db.session.commit()
            except:
                pass

            return {
                'success': True,
                'message': 'Boat successfully created !'
            }
        else:
            error_response['message'] = 'The allowed extensions are : png, svg, jpg and jpeg'
            return error_response



class AdminDeleteBoat(Resource):
    @token_required
    @check_admin_user
    def delete(current_user, self, boat_id):
        from database.models import RowingBoat
        from RowingBoat.config import UPLOAD_BOAT_FOLDER
        from RowingBoat import db

        error_response = {
            'success': False
        }

        boat = RowingBoat.query.filter_by(boat_id=boat_id).first()
        if boat == None:
            error_response['message'] = f'The boat with the id {boat_id} is not existing.'
            return error_response

        # Remove the image associated to the boat
        os.remove(boat.image_path)

        db.session.delete(boat)
        db.session.commit()

        return {
            'success': True,
            'message': f'The boat {boat.name} is correctly deleted'
        }


class AdminGetAccountToValidate(Resource):
    @token_required
    @check_admin_user
    @cross_origin()
    def get(current_user, self):
        from database.models import User
        result = []
        users = User.query.filter_by(is_account_valid=False)

        for user in users:
            result.append(user.to_json())

        return {
            'success': True,
            'users': result
        }

VALID_ACCOUNT_NOTIFICATION_ACCOUNT = "Your account is valid, you can now book boats."

class AdminValidateAccount(Resource):
    @token_required
    @check_admin_user
    def post(current_user, self, user_id):
        from database.models import User, Notification
        from RowingBoat import db
        error_response = {
            'success': False
        }
        
        # Try to get the user by his id
        user = User.query.filter_by(user_id=user_id).first()
        if user == None:
            error_response['message'] = f'The user with the id {user_id} does not exist'
            return error_response

        if user.is_account_valid:
            error_response['message'] = 'This account is already validated'
            return error_response

        # Update the user and create a notification
        user.is_account_valid = True

        notification = Notification(
            content=VALID_ACCOUNT_NOTIFICATION_ACCOUNT,
            user_id=user_id
        )

        db.session.add(notification)
        db.session.commit()

        return {
            'success': True,
            'message': 'Account validated successfully'
        }

class AdminDeclineAccount(Resource):
    @token_required
    @check_admin_user
    def post(current_ser, self, user_id):
        from database.models import User, Notification
        from RowingBoat import db
        error_response = {
            'success': False
        }

         # Try to get the user by his id
        user = User.query.filter_by(user_id=user_id).first()
        if user == None:
            error_response['message'] = f'The user with the id {user_id} does not exist'
            return error_response

        notification = Notification(
            content="Your account had not been validated by an admin. Please contact them for more information.",
            user_id=user_id
        )

        db.session.add(notification)
        db.session.commit()

        return {
            'success': True,
            'message': 'Request declined'
        }