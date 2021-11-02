import sys
sys.path.append('../')
import datetime
import enum
from RowingBoat import db

STRING_CONSTANTS_USER = {
    'LOW': 1,
    'MODERATE': 2,
    'HIGH': 3
}

REVERSE_STRING_CONSTANTS_USER = {
    1: 'LOW',
    2: 'MODERATE',
    3: 'HIGH'
}

USER_GENDER = {
    'MALE': 1,
    'FEMALE': 2,
    'DIVERSE': 3
}

REVERSE_USER_GENDER = {
    1: 'MALE',
    2: 'FEMALE',
    3: 'DIVERSE'
}

class User(db.Model):
    __tablename__ = "User"
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lastname = db.Column(db.String(80), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    birth_date = db.Column(db.DateTime, nullable=False)
    is_account_valid = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    fitness = db.Column(db.Integer, nullable=False)
    skill_level = db.Column(db.Integer, nullable=False)
    ambitions = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.Integer, nullable=False)

    # relations
    bookings = db.relationship("Booking", back_populates='user', lazy=True, cascade="all, delete")
    notifications = db.relationship("Notification", back_populates='user', lazy=True, cascade="all, delete")
    favorites = db.relationship("Favorite", back_populates='user', lazy=True, cascade="all, delete")

    def to_json(self):
        notifications_json = []
        for notification in self.notifications:
            if not notification.is_read:
                notifications_json.append(notification.to_json())


        return {
            'lastname': self.lastname,
            'firstname': self.firstname,
            'email': self.email,
            'birth_date': self.birth_date.strftime("%d/%m/%Y"),
            'is_account_valid': self.is_account_valid,
            'fitness': REVERSE_STRING_CONSTANTS_USER[self.fitness],
            'skill_level': REVERSE_STRING_CONSTANTS_USER[self.skill_level],
            'ambitions': REVERSE_STRING_CONSTANTS_USER[self.ambitions],
            'gender': REVERSE_USER_GENDER[self.gender],
            'notifications': notifications_json
        }

# Table Rowing Boat
class BoatCondition(enum.IntEnum):
    NEW = 1
    USED = 2
    BAD = 3

class RowingBoat(db.Model):
    __tablename__ = "RowingBoat"

    boat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slots = db.Column(db.Integer, nullable=False)
    image_path = db.Column(db.String(250), nullable=False)
    boat_class = db.Column(db.String(10), nullable=False)
    brand = db.Column(db.String(40), nullable=False)
    built_year = db.Column(db.Integer, nullable=False)

    bookings = db.relationship("Booking", back_populates='boat', lazy=True, cascade="all, delete")
    favorites = db.relationship("Favorite", back_populates='boat', lazy=True, cascade="all, delete")

    def to_json(self):
        return {
            'boat_id': self.boat_id,
            'name': self.name,
            'slots': self.slots,
            'boat_class': self.boat_class,
            'brand': self.brand,
            'built_year': self.built_year
        }

class Booking(db.Model):
    __tablename__ = "Booking"

    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reserved_slots = db.Column(db.Integer, nullable=False)
    google_exported = db.Column(db.Boolean, nullable=False, default=False)
    apple_exported = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    boat_id = db.Column(db.Integer, db.ForeignKey('RowingBoat.boat_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)

    # relations
    boat = db.relationship("RowingBoat", back_populates='bookings', lazy=True, foreign_keys=[boat_id])
    user = db.relationship("User", back_populates='bookings', lazy=True, foreign_keys=[user_id])

class Notification(db.Model):
    __tablename__ = "Notification"

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False, default="")
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)

    # relations
    user = db.relationship('User', back_populates='notifications', foreign_keys=[user_id])

    def to_json(self):
        return {
            'notification_id': self.notification_id,
            'content': self.content,
            'created_at': self.created_at.strftime("%d/%m/%Y")
        }

class Favorite(db.Model):
    __tablename__ = "Favorite"

    favorite_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    boat_id = db.Column(db.Integer, db.ForeignKey('RowingBoat.boat_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)

    user = db.relationship('User', back_populates='favorites', foreign_keys=[user_id])
    boat = db.relationship('RowingBoat', back_populates='favorites', foreign_keys=[boat_id])