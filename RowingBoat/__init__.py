from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

from RowingBoat.config import Config
from flask_restful import Api

from RowingBoat.user.route import UserSignUpSignIn, UserProfile
from RowingBoat.boat.route import BoatGet, BoatImageGet
from RowingBoat.admin.route import AdminCreateBoat
from RowingBoat.admin.route import AdminDeleteBoat


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
    
    # User routes
    api.add_resource(UserSignUpSignIn, "/user")
    api.add_resource(UserProfile, "/user/profile")

    # Boats routes
    api.add_resource(BoatGet, "/boat")
    api.add_resource(BoatImageGet, "/boat/<int:boat_id>/image")

    # Admin routes
    api.add_resource(AdminCreateBoat, "/admin/create_boat")
    api.add_resource(AdminDeleteBoat, "/admin/<int:boat_id>/delete_boat")


    app.config.from_object(config)

    # init
    db.init_app(app)
    bcrypt.init_app(app)

    return app