from flaskblog import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
import os


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    firstname = db.Column(db.String(20), nullable=False)
    middlename = db.Column(db.String(20))
    lastname = db.Column(db.String(20), nullable=False)
    birthdate = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    salt = db.Column(db.String(60), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    online = db.relationship('ActiveUsers', backref='online', lazy=True)
    dislikes = db.relationship('Dislikes', backref='user', passive_deletes=True)

    def get_reset_token(self, expires_sec=1800):  # creating a reset token
        s = Serializer(current_app.config['SECRET_KEY'])  # creating token with app'secret key
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(reset_token, expires_sec=1800):  # 30 mins
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(reset_token, max_age=expires_sec)['user_id']  # check if they match
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}'"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dislikes = db.relationship('Dislikes', backref='post', passive_deletes=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class ActiveUsers(db.Model, UserMixin):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    login_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip = db.Column(db.String(15), nullable=False)  # unique=True,

    def __repr__(self):
        return f"User('{self.login_time}', '{self.ip}')"


class Dislikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Dislike('{self}"
