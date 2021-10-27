import os

class Config:
    # secure after
    SECRET_KEY = "mykey"
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.abspath("../database/database.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_UNABLE = True