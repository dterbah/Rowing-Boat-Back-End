from flask import request, jsonify
import jwt
from functools import wraps
from datetime import datetime

def check_admin_user(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        from database.models import User
        from RowingBoat.config import Config

        config = Config()
        token = request.headers['x-access-tokens']
        try:
            data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])            
            current_user = User.query.filter_by(user_id=data['user_id']).first()
            if not current_user.is_admin:
                return jsonify({'message': 'Unauthorized access', 'success': 'false'})
        except:
            return jsonify({'message': 'Your session is closed. Try to sign in again.', 'success': 'false'})

        return f(*args, **kwargs)
    return decorator

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        from database.models import User
        from RowingBoat.config import Config

        config = Config()
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])            
            current_user = User.query.filter_by(user_id=data['user_id']).first()
        except:
            return jsonify({'message': 'Your session is closed. Try to sign in again.', 'success': 'false'})
    
        return f(current_user, *args, **kwargs)
    return decorator

def check_account_valid(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        from database.models import User
        from RowingBoat.config import Config

        config = Config()
        token = request.headers['x-access-tokens']
        try:
            data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])            
            current_user = User.query.filter_by(user_id=data['user_id']).first()
            if not current_user.is_account_valid:
                return jsonify({'message': 'Your account is not yet validated. Please ask to an admin to validate your account before trying to book a boat.', 'success': 'false'})
        except:
            pass

        return f(*args, **kwargs)
    return decorator