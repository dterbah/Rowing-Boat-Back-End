from flask_restful import Resource
from flask import Flask, request

class UserRoute(Resource):
    def get(self):
        return {'toto' : "titi"}