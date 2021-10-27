import sys
import datetime
sys.path.append('../')

import enum

from RowingBoat import db

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
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # relations
    bookings = db.relationship("Booking", back_populates='user', lazy=True, cascade="all, delete")
    notifications = db.relationship("Notification", back_populates='user', lazy=True, cascade="all, delete")


# Table Rowing Boat
class BoatCondition(enum.IntEnum):
    NEW = 1
    USED = 2
    BAD = 3

class RowingBoat(db.Model):
    __tablename__ = "RowingBoat"

    boat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    slots = db.Column(db.Integer, nullable=False)
    image_path = db.Column(db.String(250), nullable=False)
    boat_class = db.Column(db.String(10), nullable=False)
    brand = db.Column(db.String(40), nullable=False)
    built_year = db.Column(db.Integer, nullable=False)

    bookings = db.relationship("Booking", back_populates='boat', lazy=True, cascade="all, delete")
    favorites = db.relationship("Favorite", back_populates='boat', lazy=True, cascade="all, delete")

class Booking(db.Model):
    __tablename__ = "Booking"

    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reserved_slots = db.Column(db.Integer, nullable=False)
    google_exported = db.Column(db.Boolean, nullable=False, default=False)
    apple_exported = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    boat_id = db.Column(db.Integer, db.ForeignKey('RowingBoat.boat_id'), nullable=False)

    # relations
    boat = db.relationship("RowingBoat", back_populates='bookings', lazy=True, foreign_keys=[boat_id])

class Notification(db.Model):
    __tablename__ = "Notification"

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False, default="")
    is_read = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)

    # relations
    user = db.relationship('User', back_populates='notifications', foreign_keys=[user_id])

class Favorite(db.Model):
    __tablename__ = "Favorite"

    favorite_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    boat_id = db.Column(db.Integer, db.ForeignKey('RowingBoat.boat_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)

    user = db.relationship('User', back_populates='favorites', foreign_keys=[user_id])
    boat = db.relationship('RowingBoat', back_populates='favorites', foreign_keys=[boat_id])