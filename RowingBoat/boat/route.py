import sys
sys.path.append('../')
import os
import jwt
from functools import wraps

from flask_restful import Resource
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from middleware import token_required, check_account_valid
from werkzeug.utils import secure_filename
from utils import allowed_file
from flask import send_file

from flask_cors import cross_origin

import datetime

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
        import base64
        from database.models import RowingBoat
        error_response = {
            'success': False
        }
        
        # Retrieve the boat
        boat = RowingBoat.query.filter_by(boat_id=boat_id).first()

        if boat == None:
            error_response['message'] = 'The boat id is invalid'
            return error_response


        image_file = open(boat.image_path, 'rb')
        image = str(base64.b64encode(image_file.read()))
        return {
            'success': True,
            'encoded_image': image
        }

class BoatGetById(Resource):
    def get(self, boat_id):
        from database.models import RowingBoat

        boat = RowingBoat.query.filter_by(boat_id=boat_id).first()
        if boat == None:
            return {
                'sucess': False,
                'message': "You are trying to access to a not existing boat."
            }

        return {
            'success': True,
            'boat': boat.to_json()
        }

class BoatSearch(Resource):
    @cross_origin()
    def get(self):
        from database.models import RowingBoat
        json_boats = []

        args = request.args.to_dict()

        raw_date = request.args.get('date')

        if not 'date' in args:
            return {
                'message': f'The key "date" is missing',
                'success': False
            }

        if not 'type' in args:
            return {
                'message': f'The key "type" is missing',
                'success': False
            }

        boat_type = request.args.get('type')

        if not 'class' in args:
            return {
                'message': f'The key "class" is missing',
                'success': False
            }

        boat_class = request.args.get('class')

        # find boats by class and type
        boats = RowingBoat.query.filter_by(
            boat_type=boat_type,
            boat_class=boat_class
        ).all()

        # filter the boats by the date
        begin_date = datetime.datetime.strptime(raw_date, '%d/%m/%Y %H:%M')
    
        for boat in boats:
            add_boat = True
            available_slots = boat.get_slots_by_date(begin_date)
            if available_slots > 0:
                # apply filters
                if 'gender' in args and args['gender'] != '':
                    add_boat = add_boat and boat.is_corresponding_to_gender(begin_date, args['gender'])
                
                if 'ageGroup' in args and args['ageGroup'] != '':
                    age_group = args['ageGroup'].split("-")
                    add_boat = add_boat and boat.is_corresponding_to_age(begin_date, int(age_group[0]), int(age_group[1]))

                if 'fitness' in args and args['fitness'] != '':
                    add_boat = add_boat and boat.is_corresponding_to_fitness_level(begin_date, args['fitness'])

                if 'skill' in args and args['skill'] != '':
                    add_boat = add_boat and boat.is_corresponding_to_skill_level(begin_date, args['skill'])

            if add_boat:
                json = boat.to_json()
                json['available_slots'] = available_slots
                team_json = []
                for user in boat.get_user_by_booking_date(begin_date):
                    team_json.append(user.to_json())
                json['team'] = team_json
                json_boats.append(json)

        return {
            'success': True,
            'boats': json_boats
        }

class BoatBook(Resource):
    @cross_origin()
    @token_required
    @check_account_valid
    def get(user, self, boat_id):
        from database.models import RowingBoat, Booking
        from RowingBoat import db
        
        args = request.args.to_dict()

        if not 'date' in args:
            return {
                'message': 'The begin date is missing',
                'success': False
            }
    
        begin_date = datetime.datetime.strptime(args['date'], '%d/%m/%Y %H:%M')

        # check if the boat is still available
        boat = RowingBoat.query.filter_by(boat_id=boat_id).first()

        if boat == None:
            return {
                'message': 'The boat id is invalid',
                'success': False
            }

        if boat.get_slots_by_date(begin_date) == 0:
            return {
                'message': 'The boat you want to reserve is not available',
                'success': False
            }

        if boat.has_user_for_date(begin_date, user.user_id):
            return {
                'message': f'You have already booking during the date {begin_date}',
                'success': False
            }

        # Create the booking
        booking = Booking(
            boat_id=boat_id,
            user_id=user.user_id,
            date=begin_date
        )

        db.session.add(booking)
        db.session.commit()

        return {
            'message': 'The boat is now reserved !',
            'success': True
        }