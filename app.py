#!flask/bin/python
from flask import Flask, session, jsonify, render_template, redirect, request, make_response,session,redirect, url_for, request, abort,flash
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


# def auth_middleware(app):
#     @app.before_request
#     def check_auth():
#         if not session.get('is_authenticated'): # type: ignore
#             # return redirect(url_for('getLoginPage'))
#             pass







def __repr__(self):
    return '<Name %r>' % self.id




# @app.before_request
# @app.route('/login', methods=['GET'])
# def getLoginPage():
#     return render_template('login.html')


@app.route('/login',methods=['GET'])
def getLoginPage():
    return render_template('login.html')

@app.route('/register',methods=['GET'])
def getRegister():
    return render_template('register.html')

@app.route('/dashboard', methods=['GET'])
def getDashboardPage():
    return render_template('dashboard.html')



@app.route('/', methods=['GET'])
def getHomePage():
    return render_template('index.html')
 

@app.route('/logout', methods=['GET'])
def logoutUser():
    return redirect('/login')
 


@app.route('/user/target', methods=['GET'])
def allUserTargets():
    userId=session.get('userId') # type: ignore
    if userId:
        targets=db.targets.find({'user':ObjectId(userId)})
        context={'targets':targets}
        return render_template('targets.html',context=context)




@app.route('/user/target/view/<targetId>', methods=['GET'])
def viewUserTarget(targetId):
    userId=session.get('userId') # type: ignore
    user=db.users.find_one({'_id':ObjectId(userId)})
    if targetId and user:
        target=db.targets.find_one({'_id':ObjectId(targetId)})
        if target:
            context={'target':target}
            return render_template('detail.html',context=context)



@app.route('/user/target/delete/<targetId>', methods=['GET'])
def deleteUserTarget(targetId):
    userId=session.get('userId') # type: ignore
    user=db.users.find_one({'_id':ObjectId(userId)})
    if targetId and user:
        result=db.targets.delete_one({'_id':ObjectId(targetId)})
        if result.deleted_count == 1:
            flash('Target deleted successfully.')
            return redirect('/user/target')



@app.route('/login', methods=['POST'])
def userLogin():
    email = request.form['email'] # type: ignore
    password = request.form['password'] # type: ignore
    if email and password:
        user=db.users.find_one({'email':email,'password':password})
        if user:
            session['is_authenticated'] = True
            session['userId'] = str(user['_id'])
            context={'user':user}
            return render_template('dashboard.html',context=context)
        else:
            return redirect(url_for('getLoginPage'))
    else:
        return redirect(url_for('getLoginPage'))




@app.route('/user/target/keywords', methods=['POST'])
def addUserTarget():
    try:
        targetType = request.form['targetType'] # type: ignore
        targets = request.form['targets']# type: ignore
        limit = request.form['limit']# type: ignore
        userId=ObjectId(session.get('userId')) # type: ignore
        user=db.users.find_one({'_id':userId})
        if targetType and targets and limit and user:
            targetExist=db.targets.find_one({'targetType':targetType,'user':user['_id']})
            if not targetExist:
                    target = Target(targetType=targetType, targets=targets, limit=limit, user=user['_id'])
                    target = db.targets.insert_one(target.toDictionary())
                    flash('Target created successfully!')
                    return redirect('/dashboard')
            else:
                    flash('Target already exists')
                    return redirect('/dashboard')
        else:
            flash('Something went wrong.')
            return redirect('/dashboard')
    except Exception as e:
            flash(str(e))
            return redirect('/dashboard')

 



# @app.route('/login', methods=['POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         try:
#             reqBody = request.get_json()
#             if 'email' not in reqBody:
#                 return Utils.BadRequestResponse('email is required.')
#             if 'password' not in reqBody:
#                 return Utils.BadRequestResponse('password is required.')

#             user = User.UserExists(
#                 {'email': reqBody['email'], 'password': reqBody['password']})
#             if not user:
#                 error = "Invalid credentials. Please try again."
#                 return Utils.UnauthorizedResponse('Invalid credentials.')
#             else:
#                 data = {"_id": str(user["_id"]), "email": user["username"], "firstName": user["firstName"],
#                         "lastName": user["lastName"], "email": user["email"]}
#                 token = jwt.encode({'_id': data["_id"], 'exp': datetime.datetime.utcnow(
#                 ) + datetime.timedelta(minutes=45)}, app.config['SECRET_KEY'], "HS256")
#                 response = make_response(jsonify(
#                     {"data": data, "message": "Logged in successfully", "success": True, "token": token}), 200)
#                 session['is_authenticated'] = True
#                 print(">>>>>>>>>>>>>>>>>>>>>>>>")
#                 print(">>>>>>>>>>>>>>>>>>>>>>>>")
#                 print(">>>>>>>>>>>>>>>>>>>>>>>>")
#                 print(">>>>>>>>>>>>>>>>>>>>>>>>")

#                 return render_template('dashboard.html')
#         except Exception as e:
#             return Utils.ErrorResponse('Someting went wrong.')
#     return render_template("login.html", error=error)


# @app.route('/user', methods=['DELETE'])
# def delete_user(authUser):
#     try:
#         reqBody = request.get_json()
#         if '_id' not in reqBody:
#             return Utils.BadRequestResponse('_id is required.')
#         user = db.users.find_one({'_id': ObjectId(reqBody['_id'])})
#         if user:
#             db.targets.delete_many({'user': ObjectId(reqBody['_id'])})
#             result = db.users.delete_one({'_id': ObjectId(authUser["_id"])})
#             if result.deleted_count == 1:
#                 return Utils.SuccessResponse({}, "User deleted successfully")
#             else:
#                 return Utils.NotFoundResponse(reqBody, 'Error deleting user')
#         else:
#             return "User not FOund"

#     except Exception as e:
#         return Utils.ErrorResponse('Someting went wrong.')


# @app.route('/user/seed', methods=['GET'])
# def seed():
#     try:
#         data = User.seed()
#         return Utils.SuccessResponse(data, "User seed successfully")
#     except Exception as e:
#         return Utils.ErrorResponse('Someting went wrong.')
# # Define some heavy function


# def scrapLater(exist):
#     Scrapper.scrapKeywords(exist)
#     print("Process Complete!!! for "+exist['_id']+" " + exist['targetType'])


# @app.route('/user/target/keywords', methods=['POST'])
# def setUserTargets(authUser):
#     try:
#         reqBody = request.get_json()
#         if 'targetType' not in reqBody:
#             return Utils.BadRequestResponse('targetType is required.')

#         if reqBody['targetType'] != 'keywords' and reqBody['targetType'] != 'twitter-hashtag' and reqBody['targetType'] != 'twitter-user':
#             return Utils.BadRequestResponse('Invalid "targetType" .')

#         if 'targets' not in reqBody and len(reqBody['targets']) == 0:
#             return Utils.BadRequestResponse('targets is required.')

#         if 'limit' not in reqBody:
#             return Utils.BadRequestResponse('limit is required.')

#         if reqBody['limit'] > 1000:
#             return Utils.BadRequestResponse('maximum limit is 1000.')

#         exist = Target.TargetExist(reqBody)
#         if not exist:
#             target = Target(
#                 targetType=reqBody["targetType"], targets=reqBody["targets"], limit=reqBody['limit'], user=authUser['_id'])
#             target = db.targets.insert_one(target.toDictionary())
#             target = db.targets.find_one({'_id': target.inserted_id})
#             target['_id'] = str(target['_id'])
#             target['user'] = str(target['user'])
#             heavyTask = Process(target=scrapLater, args=(target,))
#             heavyTask.start()
#             return Utils.SuccessResponse(target, "Target created successfully")
#         else:
#             response = Utils.NotFoundResponse(
#                 exist, "Target Type '" + reqBody["targetType"]+"' already exists.")
#             return response

#     except Exception as e:
#         return Utils.ErrorResponse('Someting went wrong.')


# @app.route('/user/target/keywords', methods=['GET'])
# def getUserTargets():
#     try:
#         # data = Target.GetUserTargets(authUser)
#         # return Utils.SuccessResponse(data, "All user targets.")
#         return render_template("dashboard.html")
#     except Exception as e:
#         return Utils.ErrorResponse('Someting went wrong.')


# @app.route('/user/target/keywords', methods=['PUT'])
# def updateUserTargets(authUser):
#     try:
#         reqBody = request.get_json()
#         if 'targetType' not in reqBody:
#             return Utils.BadRequestResponse('targetType is required.')

#         if reqBody['targetType'] != 'keywords' and reqBody['targetType'] != 'twitter-hashtag' and reqBody['targetType'] != 'twitter-user':
#             return Utils.BadRequestResponse('Invalid "targetType" .')

#         if 'targets' not in reqBody and len(reqBody['targets']) == 0:
#             return Utils.BadRequestResponse('targets is required.')

#         if 'limit' not in reqBody:
#             return Utils.BadRequestResponse('limit is required.')

#         if reqBody['limit'] > 1000:
#             return Utils.BadRequestResponse('maximum limit is 1000.')
#         exist = Target.TargetExist(reqBody)
#         if exist:
#             target = db.targets.update_one({'_id': ObjectId(exist['_id'])}, {"$set": {
#                                            'targets': reqBody['targets'], 'tweets': [], 'limit': reqBody['limit'], 'status': 0}})
#             if target.matched_count > 0 and target.modified_count > 0:
#                 target = db.targets.find_one({'_id': ObjectId(exist['_id'])})
#                 target['_id'] = str(target['_id'])
#                 target['user'] = str(target['user'])
#                 return Utils.SuccessResponse(target, "Target updated successfully")
#             else:
#                 return Utils.NotFoundResponse(exist, "Failed to update target.")
#         else:
#             return Utils.NotFoundResponse({}, "Target not found.")
#     except Exception as e:
#         return Utils.ErrorResponse('Someting went wrong.')


# @app.route('/user/target/keywords', methods=['DELETE'])
# def deleteUserTargets(authUser):
#     try:
#         reqBody = request.get_json()
#         if 'targetType' not in reqBody:
#             return Utils.BadRequestResponse('targetType is required.')
#         else:
#             userTarget = db.targets.find_one(
#                 {'user': authUser['_id'], 'targetType': reqBody['targetType']})
#             if userTarget:
#                 result = db.targets.delete_one(
#                     {'user': authUser['_id'], 'targetType': reqBody['targetType']})
#                 if result.deleted_count == 1:
#                     return Utils.SuccessResponse(reqBody, 'Target deleted successfully.')
#                 else:
#                     return Utils.NotFoundResponse('Failed to delete '+reqBody['targetType']+" target.")
#             else:
#                 return Utils.NotFoundResponse("Target not found")
#     except Exception as e:
#         return Utils.ErrorResponse('Someting went wrong.')


# def my_scheduler():
#     targets = db.targets.find({})
#     for target in targets:
#         target['_id'] = str(target['_id'])
#         scrapLater(target)


# @app.before_first_request
# def activate_scheduler():
#     scheduler = BackgroundScheduler(daemon=True)
#     scheduler.add_job(func=my_scheduler, trigger='interval', seconds=60)
#     scheduler.start()
#     print(" >>> Scheduler started")




# @app.route('/user', methods=['POST'])
# def createUser(authUser):
#     try:
#         reqBody = request.get_json()
#         if reqBody is None:
#             return jsonify({"success": False, 'message': 'Invalid JSON'}), 400
#         user = User(
#             firstName=reqBody["firstName"],
#             lastName=reqBody["lastName"],
#             username=reqBody["username"],
#             password=reqBody["password"],
#             email=reqBody["email"]
#         )
#         exists = User.UserExists(
#             {'username': reqBody['username'], 'email': reqBody['email']})
#         if not exists:
#             user = db.users.insert_one(user.toDictionary())
#             user = db.users.find_one({'_id': user.inserted_id})
#             user['_id'] = str(user['_id'])
#             # data = {"_id": str(user["_id"]), "username": user["username"], "firstName": user["firstName"], "lastName": user["lastName"], "email": user["email"]}
#             return Utils.SuccessResponse(user, "User created successfully")
#         else:
#             return Utils.NotFoundResponse(exists, "User already exists")
#     except Exception as e:
#         return Utils.ErrorResponse('Someting went wrong.')


# @app.route('/user', methods=['GET'])
# def getAllUsers(authUser):
#     try:
#         data = []
#         users = db.users.find()
#         for user in users:
#             data.append({"_id": str(user["_id"]), "username": user["username"],
#                         "firstName": user["firstName"], "lastName": user["lastName"], "email": user["email"]})
#         return Utils.SuccessResponse(data, "All users")
#     except Exception as e:
#         return Utils.ErrorResponse('Someting went wrong.')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
