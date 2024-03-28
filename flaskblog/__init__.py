from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config
from flask_restful import Resource, Api
from flask_hcaptcha import hCaptcha


import logging

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = '_info_'
mail = Mail()
logger = logging.getLogger()
logFormatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")

# add console handler to the root logger
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

# add file handler to the root logger
fileHandler = logging.FileHandler("logs.log")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)


# capthca


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    api = Api(app)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors
    from flaskblog.activeusers.routes import activeusers

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(activeusers)

    return app

# todo end pointleri degistir/restful a geç
# todo data formatını json olarak değiştir

# todo postsql e geç

# todo ngix ile herkese aç
# https://www.youtube.com/watch?v=_Nq_n6Uk8WA
