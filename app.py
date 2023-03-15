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
    scheduler.add_job(func=worker, trigger='interval', seconds=60)
    scheduler.start()
    print(" >>> Scheduler started")


class MyFlaskApp(Flask):
    def run(self, host=None, port=5000, debug=True, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                activateTaskScheduler()
        super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = MyFlaskApp(__name__)
app.debug = True
app.config['SECRET_KEY'] = '004f2af45d3a4e161a7dd2d17fdae47f'


# if __name__ == '__main__':
app.run()


def __repr__(self):
    return '<Name %r>' % self.id


@app.route('/login', methods=['GET'])
def getLoginPage():
    print(">>>>>>>>>>>>>>>>>>>>>>>")
    # session['isAuthenticated'] = True
    return render_template('login.html')
    # return redirect(url_for('/dashboard'))


@app.route('/register', methods=['GET'])
def getRegister():
    return render_template('register.html')


@app.route('/dashboard', methods=['GET'])
def getDashboardPage():
    userId = session.get('userId')  # type: ignore
    if userId:
        targets = db.targets.find({'user': ObjectId(userId)})
        context = {'targets': targets}
        # return render_template('targets.html', context=context)
        return render_template('dashboard.html', context=context)
    else:
        return render_template('dashboard.html', context={'targets': {}})


@app.route('/', methods=['GET'])
def getHomePage():
    return render_template('index.html')


@app.route('/logout', methods=['GET'])
def logoutUser():
    return redirect('/login')


@app.route('/user/target', methods=['GET'])
def allUserTargets():
    userId = session.get('userId')  # type: ignore
    if userId:
        targets = db.targets.find({'user': ObjectId(userId)})
        context = {'targets': targets}
        return render_template('targets.html', context=context)


@app.route('/user/target/view/<targetId>', methods=['GET'])
def viewUserTarget(targetId):
    userId = session.get('userId')  # type: ignore
    user = db.users.find_one({'_id': ObjectId(userId)})
    if targetId and user:
        target = db.targets.find_one({'_id': ObjectId(targetId)})
        if target:
            context = {'target': target}
            return render_template('detail.html', context=context)


@app.route('/user/target/delete/<targetId>', methods=['GET'])
def deleteUserTarget(targetId):
    userId = session.get('userId')  # type: ignore
    user = db.users.find_one({'_id': ObjectId(userId)})
    if targetId and user:
        result = db.targets.delete_one({'_id': ObjectId(targetId)})
        if result.deleted_count == 1:
            flash('Target deleted successfully.')
            return redirect('/user/target')


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
            return render_template('dashboard.html', context=context)
        else:
            flash('Invalid Credentials.')
            return redirect(url_for('getLoginPage'))
    elif email == "":
        flash("Email is required")
        return redirect(url_for('getLoginPage'))
    elif password == "":
        flash("Password is required")
        return redirect(url_for('getLoginPage'))
    else:
        flash("Credentials are invalid")
        return redirect(url_for('getLoginPage'))


@app.route('/user/target/keywords', methods=['POST'])
def addUserTarget():
    try:
        targetType = request.form['targetType']  # type: ignore
        targets = request.form['targets']  # type: ignore
        if not targets:
            flash('Targets are required.')
            return redirect('/dashboard')

        if not limit:
            flash('Limit are required.')
            return redirect('/dashboard')

        limit = request.form['limit']  # type: ignore
        userId = ObjectId(session.get('userId'))  # type: ignore
        targets = targets.split(',')
        if (len(targets)):
            for target in targets:
                target = target.strip()
            user = db.users.find_one({'_id': userId})
            if targetType and targets and limit and user:
                targetExist = db.targets.find_one({'targetType': targetType, 'user': user['_id']})
                if not targetExist:
                    target = Target(targetType=targetType, targets=targets, limit=int(limit), user=user['_id'])
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
