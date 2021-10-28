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

class BoatAddAndGet(Resource):
    @token_required
    @check_admin_user
    def post(self, user):
        from database.models import RowingBoat
        from RowingBoat.config import UPLOAD_BOAT_FOLDER
        from RowingBoat import db

        error_response = {
            'success': False
        }

        data = request.form.to_dict()
        
        # Name of the boat
        if not 'name' in data:
            error_response['message'] = "The boat's name is missing"
            return error_response

        name = data['name']
        # Check if the name is available
        boat = RowingBoat.query.filter_by(name=name).first()
        if boat != None:
            error_response['message'] = f"The name {name} is already used"
            return error_response

        # Slots of the boats
        if not 'slots' in data:
            error_response['message'] = "The boat's slots are missing"
            return error_response

        slots = data['slots']

        # Boat class
        if not 'boat_class' in data:
            error_response['message'] = "The boat's class is missing"
            return error_response

        boat_class = data['boat_class']

        # Brand
        if not 'brand' in data:
            error_response['message'] = "The boat's brand is missing"
            return error_response

        brand = data['brand']

        # Built year
        if not 'built_year' in data:
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
                              built_year=built_year
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

        
