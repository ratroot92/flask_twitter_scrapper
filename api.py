#!flask/bin/python
from flask import Flask, jsonify, render_template, redirect, request, make_response
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from flask import request
import asyncio
import json
import snscrape.modules.twitter as sntwitter
from datetime import datetime
import json
from models.user import User
from models.target import Target
from utils.snsscrapper import Scrapper
from config.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime
from multiprocessing import Process
from utils.util import Utils
import time
from apscheduler.schedulers.background import BackgroundScheduler

from jwt.exceptions import ExpiredSignatureError
# Github Token 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
# Github user ratroot92

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'

# innitliaze DB

# userTargetCollection = db['usertargets']
# usersCollection = db['users']


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
        if not token:
            return Utils.UnauthorizedResponse('Missing access token.')
        try:
            tokenPayload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            authUser = db.users.find_one({'_id': ObjectId(tokenPayload['_id'])})
            if authUser:
                authUser['_id'] = str(authUser['_id'])
                return f(authUser, *args, **kwargs)
            else:
                return Utils.UnauthorizedResponse('User not found.')
            # data = {"_id": str(authUser["_id"]), "username": authUser["username"], "first_name": authUser["first_name"], "last_name": authUser["last_name"], "_id": authUser["_id"]}
        except ExpiredSignatureError as e:
            return Utils.UnauthorizedResponse("Error: {}".format(str(e)))

    return decorator


# create a function
def __repr__(self):
    return '<Name %r>' % self.id


@app.route('/user', methods=['POST'])
@token_required
def createUser(authUser):
    try:
        reqBody = request.get_json()
        if reqBody is None:
            return jsonify({"success": False, 'message': 'Invalid JSON'}), 400
        user = User(
            first_name=reqBody["first_name"],
            last_name=reqBody["last_name"],
            username=reqBody["username"],
            password=reqBody["password"],
            email=reqBody["email"]
        )
        exists = User.UserExists(
            {'username': reqBody['username'], 'email': reqBody['email']})
        if not exists:
            user = db.users.insert_one(user.toDictionary())
            user = db.users.find_one({'_id': user.inserted_id})
            user['_id'] = str(user['_id'])
            # data = {"_id": str(user["_id"]), "username": user["username"], "first_name": user["first_name"], "last_name": user["last_name"], "email": user["email"]}
            return Utils.SuccessResponse(user, "User created successfully")
        else:
            return Utils.NotFoundResponse(exists, "User already exists")
    except Exception as e:
        return Utils.ErrorResponse('Someting went wrong.')


@app.route('/user', methods=['GET'])
@token_required
def getAllUsers(authUser):
    try:
        data = []
        users = db.users.find()
        for user in users:
            data.append({"_id": str(user["_id"]), "username": user["username"],
                        "first_name": user["first_name"], "last_name": user["last_name"], "email": user["email"]})
        return Utils.SuccessResponse(data, "All users")
    except Exception as e:
        return Utils.ErrorResponse('Someting went wrong.')


@app.route('/login', methods=['POST'])
def login():
    try:
        reqBody = request.get_json()
        if 'email' not in reqBody:
            return Utils.BadRequestResponse('email is required.')
        if 'password' not in reqBody:
            return Utils.BadRequestResponse('password is required.')

        user = User.UserExists({'email': reqBody['email'], 'password': reqBody['password']})
        print(user)
        if not user:
            return Utils.UnauthorizedResponse('Invalid credentials.')
        else:
            data = {"_id": str(user["_id"]), "email": user["username"], "first_name": user["first_name"], "last_name": user["last_name"], "email": user["email"]}
            token = jwt.encode({'_id': data["_id"], 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=45)}, app.config['SECRET_KEY'], "HS256")
            response = make_response(jsonify({"data": data, "message": "Logged in successfully", "success": True, "token": token}), 200)
            return response
    except Exception as e:
        return Utils.ErrorResponse('Someting went wrong.')


@app.route('/user', methods=['DELETE'])
@token_required
def delete_user(authUser):
    try:
        reqBody = request.get_json()
        if '_id' not in reqBody:
            return Utils.BadRequestResponse('_id is required.')
        user = db.users.find_one({'_id': ObjectId(reqBody['_id'])})
        if user:
            db.targets.delete_many({'user': ObjectId(reqBody['_id'])})
            result = db.users.delete_one({'_id': ObjectId(authUser["_id"])})
            if result.deleted_count == 1:
                return Utils.SuccessResponse({}, "User deleted successfully")
            else:
                return Utils.NotFoundResponse(reqBody, 'Error deleting user')
        else:
            return "User not FOund"

    except Exception as e:
        return Utils.ErrorResponse('Someting went wrong.')


@app.route('/user/seed', methods=['GET'])
def seed():
    try:
        data = User.seed()
        return Utils.SuccessResponse(data, "User seed successfully")
    except Exception as e:
        return Utils.ErrorResponse('Someting went wrong.')
# Define some heavy function


def scrapLater(exist):
    Scrapper.scrapKeywords(exist)
    print("Process Complete!!! for "+exist['_id']+" " + exist['target_type'])


@app.route('/user/targets/keywords', methods=['POST'])
@token_required
def setUserTargets(authUser):
    try:
        reqBody = request.get_json()
        if 'target_type' not in reqBody:
            return Utils.BadRequestResponse('target_type is required.')

        if reqBody['target_type'] != 'keywords' and reqBody['target_type'] != 'twitter-hashtag' and reqBody['target_type'] != 'twitter-user':
            return Utils.BadRequestResponse('Invalid "target_type" .')

        if 'targets' not in reqBody and len(reqBody['targets']) == 0:
            return Utils.BadRequestResponse('targets is required.')

        if 'limit' not in reqBody:
            return Utils.BadRequestResponse('limit is required.')

        if reqBody['limit'] > 1000:
            return Utils.BadRequestResponse('maximum limit is 1000.')

        exist = Target.TargetExist(reqBody)
        if not exist:
            target = Target(target_type=reqBody["target_type"], targets=reqBody["targets"], limit=reqBody['limit'], user=authUser['_id'])
            target = db.targets.insert_one(target.toDictionary())
            target = db.targets.find_one({'_id': target.inserted_id})
            target['_id'] = str(target['_id'])
            target['user'] = str(target['user'])
            heavyTask = Process(target=scrapLater, args=(target,))
            heavyTask.start()
            return Utils.SuccessResponse(target, "Target created successfully")
        else:
            response = Utils.NotFoundResponse(exist, "Target Type '" + reqBody["target_type"]+"' already exists.")
            return response

    except Exception as e:
        return Utils.ErrorResponse('Someting went wrong.')


@app.route('/user/targets/keywords', methods=['GET'])
@token_required
def getUserTargets(authUser):
    try:
        data = Target.GetUserTargets(authUser)
        return Utils.SuccessResponse(data, "All user targets.")
    except Exception as e:
        return Utils.ErrorResponse('Someting went wrong.')


@app.route('/user/targets/keywords', methods=['PUT'])
@token_required
def updateUserTargets(authUser):
    try:
        reqBody = request.get_json()
        if 'target_type' not in reqBody:
            return Utils.BadRequestResponse('target_type is required.')

        if reqBody['target_type'] != 'keywords' and reqBody['target_type'] != 'twitter-hashtag' and reqBody['target_type'] != 'twitter-user':
            return Utils.BadRequestResponse('Invalid "target_type" .')

        if 'targets' not in reqBody and len(reqBody['targets']) == 0:
            return Utils.BadRequestResponse('targets is required.')

        if 'limit' not in reqBody:
            return Utils.BadRequestResponse('limit is required.')

        if reqBody['limit'] > 1000:
            return Utils.BadRequestResponse('maximum limit is 1000.')
        exist = Target.TargetExist(reqBody)
        if exist:
            target = db.targets.update_one({'_id': ObjectId(exist['_id'])}, {"$set": {'targets': reqBody['targets'], 'tweets': [], 'limit': reqBody['limit'], 'status': 0}})
            if target.matched_count > 0 and target.modified_count > 0:
                target = db.targets.find_one({'_id': ObjectId(exist['_id'])})
                target['_id'] = str(target['_id'])
                target['user'] = str(target['user'])
                return Utils.SuccessResponse(target, "Target updated successfully")
            else:
                return Utils.NotFoundResponse(exist, "Failed to update target.")
        else:
            return Utils.NotFoundResponse({}, "Target not found.")
    except Exception as e:
        return Utils.ErrorResponse('Someting went wrong.')


@app.route('/user/targets/keywords', methods=['DELETE'])
@token_required
def deleteUserTargets(authUser):
    try:
        reqBody = request.get_json()
        if 'target_type' not in reqBody:
            return Utils.BadRequestResponse('target_type is required.')
        else:
            userTarget = db.targets.find_one({'user': authUser['_id'], 'target_type': reqBody['target_type']})
            if userTarget:
                result = db.targets.delete_one({'user': authUser['_id'], 'target_type': reqBody['target_type']})
                if result.deleted_count == 1:
                    return Utils.SuccessResponse(reqBody, 'Target deleted successfully.')
                else:
                    return Utils.NotFoundResponse('Failed to delete '+reqBody['target_type']+" target.")
            else:
                return Utils.NotFoundResponse("Target not found")
    except Exception as e:
        return Utils.ErrorResponse('Someting went wrong.')


def my_scheduler():
    targets = db.targets.find({})
    for target in targets:
        target['_id'] = str(target['_id'])
        scrapLater(target)


@app.before_first_request
def activate_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=my_scheduler, trigger='interval', seconds=60)
    scheduler.start()
    print(" >>> Scheduler started")


if __name__ == '__main__':
    app.run(port=5000, debug=True)
