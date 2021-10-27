from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from RowingBoat.config import Config
from flask_restful import Api

from RowingBoat.user.route import UserRoute


db = SQLAlchemy()

def create_app(config=Config):

    # import models
    from database.models import User
    from database.models import RowingBoat
    from database.models import Booking
    from database.models import Favorite
    from database.models import Notification

    app = Flask(__name__)
    api = Api(app)

    # add the routes of the API
    api.add_resource(UserRoute, "/")

    app.config.from_object(config)
    db.init_app(app)

    return app