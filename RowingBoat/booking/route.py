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

class BookingGet(Resource):
    @token_required
    def get(user, self):
        from database.models import RowingBoat

        bookings_json = []
        for booking in user.bookings:
            bookings_json.append(booking.to_json())

        return {
            'success': True,
            'bookings': bookings_json
        }
