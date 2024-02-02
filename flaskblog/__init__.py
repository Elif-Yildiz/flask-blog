from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import hashlib
import os
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

app.config['SECRET_KEY'] = 'c0e5d47ecba2b7d97e9434b3f688c629'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = '_info_'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'elify2258@gmail.com'
app.config['MAIL_PASSWORD'] = 'ozvn lqna ouhp xxhk '
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'elify2258@gmail.com'
mail = Mail(app)
#env dosyasına gizli bilgilerini koy

from flaskblog.users.routes import users
from flaskblog.posts.routes import posts
from flaskblog.main.routes import main

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
