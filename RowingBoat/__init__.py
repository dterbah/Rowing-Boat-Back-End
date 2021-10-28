from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from RowingBoat.config import Config
from flask_restful import Api

from RowingBoat.user.route import UserSignUpSignIn, UserProfile


db      = SQLAlchemy()
bcrypt  = Bcrypt()

def create_app(config=Config):

    # import models
    from database.models import User
    from database.models import RowingBoat
    from database.models import Booking
    from database.models import Favorite
    from database.models import Notification

    print(config.SQLALCHEMY_DATABASE_URI)

    app = Flask(__name__)
    api = Api(app)

    # add the routes of the API
    api.add_resource(UserSignUpSignIn, "/user")
    api.add_resource(UserProfile, "/user/profile")

    app.config.from_object(config)

    # init
    db.init_app(app)
    bcrypt.init_app(app)

    return app