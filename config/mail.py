from flask import Flask
from flask_mail import Mail
import os
from dotenv import dotenv_values
env_config = dotenv_values(".env")


template_dir = os.path.abspath('../templates')

app = Flask(__name__, template_folder=template_dir)
app.debug = True
app.config['SECRET_KEY'] = ''
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = env_config["MAIL_USERNAME"]
app.config['MAIL_PASSWORD'] = env_config["MAIL_PASSWORD"]
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
