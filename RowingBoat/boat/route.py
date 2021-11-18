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

class BoatGet(Resource):
    def get(self):
        from database.models import RowingBoat

        boats_json = []

        boats = RowingBoat.query.all()
        for boat in boats:
            boats_json.append(boat.to_json())

        return {
            'success': True,
            'boats': boats_json
        }


class BoatImageGet(Resource):
    def get(self, boat_id):
        from database.models import RowingBoat
        error_response = {
            'success': False
        }
        
        # Retrieve the boat
        boat = RowingBoat.query.filter_by(boat_id=boat_id).first()

        if boat == None:
            error_response['message'] = 'The boat id is invalid'
            return error_response

        # Send the image
        image_path = boat.image_path
        return send_file(image_path, mimetype='image/gif')