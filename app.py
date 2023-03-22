#!flask/bin/python
from flask import Flask, session, jsonify, render_template, redirect, request, make_response, session, redirect, url_for, request, abort, flash
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
from models.configuration import TargetConfiguration

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
import os
from flask_mail import Mail
from flask_mail import Message


def worker():
    try:
        targets = db.targets.find({})
        for target in targets:
            print("1", type(target['_id']))
            if target['status'] == 0:
                db.targets.update_one({'_id': target['_id']}, {'$set': {'status': 1}, })
                newTweets = Scrapper.scrapKeywords(target)
                if newTweets is not None:
                    if (len(newTweets) > 0):
                        content = "<ul>"
                        for tweet in newTweets:
                            content += "<li> Tweet Content"+tweet['rawContent']+"</li>"
                        content += "</ul>"
                        with app.app_context():
                            msg = Message("Alert", sender="maliksblr92@gmail.com", recipients=["rizwanhussain4426@gmail.com"])
                            msg.body = content
                            mail.send(msg)
                else:
                    pass
            else:
                print("Target already in progress.")
                pass
        print("Process Complete!!! for "+str(target['_id'])+" " + target['targetType'])
    except Exception as e:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print("worker >>> ", e)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")


def activateTaskScheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=worker, trigger='interval', seconds=10)
    scheduler.start()
    print(">>> Scheduler started")


class MyFlaskApp(Flask):
    def run(self, host=None, port=5000, debug=True, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                activateTaskScheduler()
        super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = MyFlaskApp(__name__)
app.debug = True
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'maliksblr92@gmail.com'
app.config['MAIL_PASSWORD'] = 'sfyftjqdwkqmizbm'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


def protectedRoute(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        isAuthenticated = session.get('isAuthenticated')
        userId = session.get('userId')
        if isAuthenticated and userId:
            return func(userId, *args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper


def unprotectedRoute(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        isAuthenticated = session.get('isAuthenticated')
        userId = session.get('userId')
        if isAuthenticated and userId:
            return redirect(url_for('getDashboardPage'))
        else:
            return func(*args, **kwargs)

    return wrapper

#     return wrapper


# if __name__ == '__main__':


def __repr__(self):
    return '<Name %r>' % self.id


@app.route('/login', methods=['GET'])
@unprotectedRoute
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def userLogin():
    email = request.form['email']  # type: ignore
    password = request.form['password']  # type: ignore
    if email and password:
        user = db.users.find_one({'email': email, 'password': password})
        if user:
            session['isAuthenticated'] = True
            session['userId'] = str(user['_id'])
            session['username'] = user['username']
            session['email'] = user['email']

            return redirect(url_for('getDashboardPage'))
        else:
            flash('Invalid Credentials.')
            return redirect(url_for('login'))
    elif email == "":
        flash("Email is required")
        return redirect(url_for('login'))
    elif password == "":
        flash("Password is required")
        return redirect(url_for('login'))
    else:
        flash("Credentials are invalid")
        return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET'])
@protectedRoute
def getDashboardPage(userId):
    targets = db.targets.find({'user': ObjectId(userId)})
    context = {'targets': targets}
    return render_template('dashboard.html', context=context)


@app.route('/configurations', methods=['GET'])
@protectedRoute
def getConfigPage(userId):
    # targets = db.targets.find({'user': ObjectId(userId)})
    # context = {'targets': targets}
    return render_template('configuration.html', context={})


@app.route('/user/target/configuration', methods=['POST'])
@protectedRoute
def setConfgurations():
    try:
        likeCount = request.form['likeCount']  # type: ignore
        retweetCount = request.form['retweetCount']  # type: ignore
        location = request.form['location']  # type: ignore
        viewCount = request.form['viewCount']  # type: ignore
        inKeywords = request.form['inKeywords']  # type: ignore
        outKeywords = request.form['outKeywords']  # type: ignore
        if likeCount:
            flash('likeCount is required.')
            return redirect(url_for('getConfigPage'))
        if retweetCount:
            flash('retweetCount is required.')
        if viewCount:
            flash('viewCount is required.')
            return redirect(url_for('getConfigPage'))
        targetConfiguration = TargetConfiguration(likeCount=likeCount, retweetCount=retweetCount, location=location, viewCount=viewCount, inKeywords=inKeywords, outKeywords=outKeywords)
        targetConfiguration = db.target_configurations.insert_one(targetConfiguration.toDictionary())
        return redirect(url_for('getConfigPage'))
    except Exception as e:
        flash('TargetConfguration creation failed...')
        return redirect(url_for('getConfigPage'))


@app.route('/register', methods=['GET'])
@unprotectedRoute
def getRegisterPage():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
@unprotectedRoute
def registerUser():
    try:
        firstName = request.form['firstName']  # type: ignore
        lastName = request.form['lastName']  # type: ignore
        username = request.form['username']  # type: ignore
        password = request.form['password']  # type: ignore
        confirmPassword = request.form['confirmPassword']  # type: ignore
        email = request.form['email']  # type: ignore
        if password == confirmPassword:
            if firstName and lastName and username and password and confirmPassword and email:
                exist = db.users.find_one({'email': email})
                if not exist:
                    user = User(firstName=firstName, lastName=lastName, username=username, password=password, email=email)
                    user = db.users.insert_one(user.toDictionary())
                    flash('User created sucessfully.')
                    return redirect(url_for('login'))
                else:
                    flash('User already exists.')
                    return redirect(url_for('getRegisterPage'))
        else:
            flash('Password mismatch.')
            return redirect(url_for('getRegisterPage'))
    except Exception as e:
        flash('User creation failed...')
        return redirect(url_for('getRegisterPage'))


@app.route('/', methods=['GET'])
@unprotectedRoute
def getHomePage():
    return render_template('index.html')


@app.route('/logout', methods=['GET'])
def logoutUser():
    session['isAuthenticated'] = False
    session['userId'] = ''
    session['username'] = ''
    session['email'] = ''
    return redirect(url_for('login'))


@app.route('/user/target/view/<targetId>', methods=['GET'])
@protectedRoute
def viewUserTarget(userId, targetId):
    if targetId:
        target = db.targets.find_one({'_id': ObjectId(targetId)})
        if target:
            context = {'target': target}
            return render_template('detail.html', context=context)
    else:
        flash('Target not found.')
        return redirect('getDashboardPage')


@app.route('/user/target/delete/<targetId>', methods=['GET'])
@protectedRoute
def deleteUserTarget(userId, targetId):
    if targetId:
        result = db.targets.delete_one({'_id': ObjectId(targetId)})
        if result.deleted_count == 1:
            flash('Target deleted successfully.')
            return redirect(url_for('getDashboardPage'))
    else:
        flash('Target not found.')
        return redirect('getDashboardPage')


@app.route('/user/target/keywords', methods=['POST'])
@protectedRoute
def addUserTarget(userId):
    try:
        targetType = request.form['targetType']  # type: ignore
        targets = request.form['targets']  # type: ignore
        if not targets:
            flash('Targets are required.')
            return redirect(url_for('getDashboardPage'))
        targets = targets.split(',')
        if (len(targets)):
            for target in targets:
                target = target.strip()
            user = db.users.find_one({'_id': ObjectId(userId)})
            target = Target(targetType=targetType, targets=targets, limit=int(100000), user=user['_id'])
            target = db.targets.insert_one(target.toDictionary())
            flash('Target created successfully!')
        return redirect(url_for('getDashboardPage'))
    except Exception as e:
        flash(str(e))
        return redirect(url_for('getDashboardPage'))


app.run()
