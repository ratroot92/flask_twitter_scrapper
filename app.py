#!flask/bin/python
from flask import Flask, session, jsonify, render_template, redirect, request, make_response, session, redirect, url_for, request, abort, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from flask import request
import snscrape.modules.twitter as sntwitter
from datetime import datetime
import json
from models.user import User
from models.target import Target
from utils.snsscrapper import Scrapper
from config.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from multiprocessing import Process
from apscheduler.schedulers.background import BackgroundScheduler
from jwt.exceptions import ExpiredSignatureError
import os


def worker():
    try:
        targets = db.targets.find({})
        for target in targets:
            # if target['status'] == 0:
            target['_id'] = str(target['_id'])
            Scrapper.scrapKeywords(target)
            print("Process Complete!!! for "+target['_id']+" " + target['targetType'])
    except Exception as e:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(e)
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
            context = {'user': user}
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
        flash('User creattion failed.')
        return redirect(url_for('getRegisterPage'))


@app.route('/', methods=['GET'])
@unprotectedRoute
def getHomePage():
    return render_template('index.html')


@app.route('/logout', methods=['GET'])
def logoutUser():
    session['isAuthenticated'] = False
    session['userId'] = ''
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
        limit = request.form['limit']
        if not targets:
            flash('Targets are required.')
            return redirect(url_for('getDashboardPage'))
        if not limit:
            flash('Limit are required.')
            return redirect(url_for('getDashboardPage'))
        targets = targets.split(',')
        if (len(targets)):
            for target in targets:
                target = target.strip()
            user = db.users.find_one({'_id': ObjectId(userId)})
            target = Target(targetType=targetType, targets=targets, limit=int(limit), user=user['_id'])
            target = db.targets.insert_one(target.toDictionary())
            flash('Target created successfully!')
            return redirect(url_for('getDashboardPage'))
    except Exception as e:
        flash(str(e))
        return redirect(url_for('getDashboardPage'))


app.run()
