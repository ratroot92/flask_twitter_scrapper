
# pylint: wrong-import-order,unused-import
# pylint:  unused-import

#!flask/bin/python
from flask import Flask, session,  render_template, redirect, request, session, redirect, url_for, request,  flash
from bson.objectid import ObjectId
from models.user import User
from models.target import Target
from models.configuration import Confgiuration
from utils.snsscrapper import Scrapper
from config.db import db
from functools import wraps
from utils.util import Utils
from apscheduler.schedulers.background import BackgroundScheduler
from jwt.exceptions import ExpiredSignatureError
import os
from flask_mail import Mail
from flask_mail import Message
from datetime import date
from datetime import datetime, timedelta
from dotenv import dotenv_values
from flask import send_from_directory
env_config = dotenv_values(".env")


def worker():
    pass
    # try:
    #     user_targets = db.targets.find({})
    #     for target in user_targets:
    #         if target['status'] == 0:
    #             db.targets.update_one({'_id': target['_id']}, {'$set': {'status': 1}, })
    #             new_tweets = Scrapper.scrapKeywords(target)
    #             if new_tweets is not None:
    #                 if (len(new_tweets) > 0):
    #                     content = ""
    #                     for tweet in new_tweets:
    #                         content += "\nTweeted By : " + tweet['user']['username'] + "\n"
    #                         content += "\nTweet Content : " + tweet['rawContent'] + "\n"
    #                         content += "\nLikes :" + str(tweet['likeCount']) + "\n"
    #                         content += "\nRetweets:" + str(tweet['retweetCount']) + "\n"
    #                         content += "\nReplies :" + str(tweet['replyCount']) + "\n"
    #                         content += "\nLang :" + tweet['lang'] + "\n"
    #                         content += "\nViews :" + str(tweet['viewCount']) + "\n"
    #                 content += ""
    #                 with app.app_context():
    #                     msg = Message(
    #                         "Alert", sender="maliksblr92@gmail.com", recipients=["maliksblr92@gmail.com"])
    #                     msg.body = content
    #                     mail.send(msg)
    #             else:
    #                 pass
    #         else:
    #             print("Target already in progress.")
    #             pass
    #         print("Process Complete!!! for " +
    #               str(target['_id']) + " " + target['target_type'])
    # except Exception as exception:
    #     app.logger.error(str(exception), exc_info=True)


def activateTaskScheduler():
    # db.targets.update_many({}, {'$set': {'status': 0}})
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=worker, trigger='interval', seconds=20)
    scheduler.start()
    print(">>> Scheduler started")


class MyFlaskApp(Flask):
    def run(self, host=None, port=5000, debug=True, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                activateTaskScheduler()
        super(MyFlaskApp, self).run(host=host, port=port,
                                    debug=debug, load_dotenv=load_dotenv, **options)


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


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def protectedRoute(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        isAuthenticated = session.get('isAuthenticated')
        user_id = session.get('user_id')
        if isAuthenticated and user_id:
            return func(user_id, *args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper


def unprotectedRoute(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        isAuthenticated = session.get('isAuthenticated')
        user_id = session.get('user_id')
        if isAuthenticated and user_id:
            return redirect(url_for('get_dashboard_page'))
        else:
            return func(*args, **kwargs)

    return wrapper



# if __name__ == '__main__':


def __repr__(self):
    return '<Name %r>' % self.id


@app.route('/login', methods=['GET'])
@unprotectedRoute
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def userLogin():
    email = request.form['email']
    password = request.form['password']
    if email and password:
        user = db.users.find_one({'email': email, 'password': password})
        if user:
            session['isAuthenticated'] = True
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['email'] = user['email']
            return redirect(url_for('get_dashboard_page'))
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
def get_dashboard_page(user_id):
    targets = db.targets.find({'user': ObjectId(user_id)})
    configuration = {
        "like_count": int(env_config["TARGET_CONFIG_LIKES_COUNT"]),
        "retweet_count": int(env_config["TARGET_CONFIG_RETWEET_COUNT"]),
        "view_count": int(env_config["TARGET_CONFIG_VIEW_COUNT"]),
        "in_keywords": env_config["TARGET_CONFIG_VIEW_IN_KEYWQORDS"].split(","),
        "out_keywords": env_config["TARGET_CONFIG_VIEW_OUT_KEYWQORDS"].split(","),
    }
    context = {'targets': targets, 'configuration': configuration}
    return render_template('dashboard.html', context=context)




    
@app.route('/user/target/edit/<target_id>', methods=['GET'])
@protectedRoute
def edit_user_target(user_id, target_id):
    try:
        if target_id:
            target = db.targets.find_one({'_id': ObjectId(target_id)})
            if target:
                return render_template('configuration.html', target=target)
            else:
                flash('Target not found.')
                return redirect(url_for('get_dashboard_page'))
        else:
            flash('Target not found.')
            return redirect(url_for('get_dashboard_page'))
    except Exception as exception:
        return redirect(url_for('get_dashboard_page'))
    
    
    
@app.route('/user/target/edit/<target_id>', methods=['POST'])
@protectedRoute
def edit_target_configuration(user_id,target_id):

    try:  
        like_count = int(request.form['like_count'])
        if not like_count:
            flash('"like_count" is required.')
            return redirect('/user/target/edit/' + str(target_id))
        retweet_count = int(request.form['retweet_count'])
        if not retweet_count:
            flash('"retweet_count" is required.')
            return redirect('/user/target/edit/' + str(target_id))
        view_count = int(request.form['view_count'])
        if not view_count:
            flash('"view_count" is required.')
            return redirect('/user/target/edit/' + str(target_id))
        view_count = int(request.form['view_count'])
        if not view_count:
            flash('"view_count" is required.')
            return redirect('/user/target/edit/' + str(target_id))
        in_keywords = request.form['in_keywords'].split(",")
        if len(in_keywords) < 1:
            flash('"in_keywords" is required.')
            return redirect(url_for('get_dashboard_page'))
        out_keywords = request.form['out_keywords'].split(",")
        if len(out_keywords) < 1:
            flash('"out_keywords" is required.')
            return redirect(url_for('get_dashboard_page'))
        
        if len(in_keywords) > 0 and len(out_keywords) > 0:
            trimed_in_keywords = []
            trimed_out_keywords = []
            for keyword in in_keywords:
                trimed_in_keywords.append(keyword.strip())
            for keyword in out_keywords:
                trimed_out_keywords.append(keyword.strip())
            update=db.targets.update_one({'_id': ObjectId(target_id)}, 
                                  {'$set': {
                                    'configuration.like_count': like_count,
                                    'configuration.retweet_count': retweet_count,
                                    'configuration.view_count': view_count,
                                    'configuration.in_keywords': trimed_in_keywords, 
                                    'configuration.out_keywords': trimed_out_keywords, 
                                    'tweets': [],
                                    'status': 0
                                       }, 
                                  })
            print("update",update)
                               
        flash('Target Confguration updated successfully...')
        return redirect('/user/target/edit/' + str(target_id))
    except Exception as exception:
        print('error.....', exception)
        flash('Failed to update target configurations.')
        return redirect('/user/target/edit/' + str(target_id))


@app.route('/register', methods=['GET'])
@unprotectedRoute
def get_registertion_page():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
@unprotectedRoute
def register_user():
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        if password == confirm_password:
            if first_name and last_name and username and password and confirm_password and email:
                exist = db.users.find_one({'email': email})
                if not exist:
                    user = User(first_name=first_name, last_name=last_name, username=username, password=password, email=email)
                    user = db.users.insert_one(user.toDictionary())
                    flash('User created sucessfully.')
                    return redirect(url_for('login'))
                else:
                    flash('User already exists.')
                    return redirect(url_for('get_registertion_page'))
        else:
            flash('Password mismatch.')
            return redirect(url_for('get_registertion_page'))
    except Exception as exception:
        app.logger.error(str(exception), exc_info=True)
        flash('User creation failed...')
        return redirect(url_for('get_registertion_page'))


@app.route('/', methods=['GET'])
@unprotectedRoute
def get_homepage():
    return render_template('index.html')


@app.route('/logout', methods=['GET'])
def logout_user():
    session['isAuthenticated'] = False
    session['user_id'] = ''
    session['username'] = ''
    session['email'] = ''
    return redirect(url_for('login'))


@app.route('/user/target/view/<target_id>', methods=['GET'])
@protectedRoute
def view_user_details(user_id, target_id):
    if target_id:
        target = db.targets.find_one({'_id': ObjectId(target_id)})
        if target:
            context = {'target': target}
            return render_template('detail.html', context=context)
    else:
        flash('Target not found.')
        return redirect(url_for('get_dashboard_page'))
    



@app.route('/user/target/delete/<target_id>', methods=['GET'])
@protectedRoute
def delete_target(user_id, target_id):
    if target_id:
        result = db.targets.delete_one({'_id': ObjectId(target_id)})
        if result.deleted_count == 1:
            flash('Target deleted successfully.')
            return redirect(url_for('get_dashboard_page'))
    else:
        flash('Target not found.')
        return redirect(url_for('get_dashboard_page'))


@app.route('/user/target/keywords', methods=['POST'])
@protectedRoute
def add_target(user_id):
    try:
        like_count = int(request.form['like_count'])
        if not like_count:
            flash('"like_count" is required.')
            return redirect(url_for('get_dashboard_page'))
        retweet_count = int(request.form['retweet_count'])

        if not retweet_count:
            flash('"retweet_count" is required.')
            return redirect(url_for('get_dashboard_page'))

        view_count = int(request.form['view_count'])
        if not view_count:
            flash('"view_count" is required.')
            return redirect(url_for('get_dashboard_page'))

        in_keywords = request.form['in_keywords'].split(",")
        if len(in_keywords) < 1:
            flash('"in_keywords" is required.')
            return redirect(url_for('get_dashboard_page'))

        out_keywords = request.form['out_keywords'].split(",")
        if len(out_keywords) < 1:
            flash('"out_keywords" is required.')
            return redirect(url_for('get_dashboard_page'))

        target_type = request.form['target_type']
        if not target_type:
            flash('"target_type" is required.')
            return redirect(url_for('get_dashboard_page'))

        targets = request.form['targets']
        if not targets:
            flash('Twitter "target" is required.')
            return redirect(url_for('get_dashboard_page'))

        targets = targets.split(',')
        if (len(targets) < 1):
            flash('target is required.')
            return redirect(url_for('get_dashboard_page'))

        if (len(targets) > 1):
            flash('Only one target can be set.')
            return redirect(url_for('get_dashboard_page'))

        if (len(targets)):
            for target in targets:
                target = target.strip()
            user = db.users.find_one({'_id': ObjectId(user_id)})
            configuration = {
                "like_count": like_count,
                "retweet_count": retweet_count,
                "view_count": view_count,
                "in_keywords": in_keywords,
                "out_keywords": out_keywords,
            }
            """target_type, targets, user, limit, configuration, tweets=[], status=0,"""
            target = Target(target_type, targets,
                            user['_id'], int(100000), configuration)
            target = db.targets.insert_one(target.toDictionary())
            flash('Target created successfully!')
        return redirect(url_for('get_dashboard_page'))
    except Exception as exception:
        flash(str(exception))
        return redirect(url_for('get_dashboard_page'))


app.run()
