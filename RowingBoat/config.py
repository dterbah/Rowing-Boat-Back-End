import os

UPLOAD_BOAT_FOLDER = os.path.abspath(f'images')

class Config:
    # secure after
    SECRET_KEY = "mykey"
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_UNABLE = True