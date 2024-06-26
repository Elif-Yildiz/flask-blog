from flask import Blueprint
from datetime import datetime

from flaskblog.models import User, Post, ActiveUsers
from flask import Flask, render_template, url_for, flash, request, redirect
from flaskblog import db
from flask_login import login_user, logout_user, current_user, login_required
import hashlib
import os

from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            birthdate_str = form.birthdate.data
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid birthdate format. Please use YYYY-MM-DD.', 'danger')
            return redirect(url_for('users.register'))
        salt = os.urandom(16)
        password = form.password.data.encode('utf-8')
        hashed_password = hashlib.sha256(salt + password).hexdigest()
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password,
                    active=False,
                    firstname=form.firstname.data,
                    lastname=form.lastname.data,
                    middlename=form.middlename.data,
                    birthdate=birthdate,
                    salt=salt)
        db.session.add(user)
        db.session.commit()
        flash(f'{form.username.data}, your account has been created!You can log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        entered_password = form.password.data.encode('utf-8')
        stored_salt = user.salt
        hashed_password = hashlib.sha256(stored_salt + entered_password).hexdigest()
        if user is not None and user.password == hashed_password:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            active_user = ActiveUsers(user_id=user.id, login_time=datetime.utcnow(), ip=request.remote_addr)
            db.session.add(active_user)
            db.session.commit()

            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful!', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    # Remove user from ActiveUsers table
    if current_user.is_authenticated:
        active_user = ActiveUsers.query.filter_by(user_id=current_user.id).first()
        if active_user:
            db.session.delete(active_user)
            db.session.commit()
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

@users.route("/user/list")
def user_list():
    users = User.query.all()
    posts = Post.query.all()
    return render_template('user_list.html', users=users, posts=posts)

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<reset_token>", methods=['GET', 'POST'])
def reset_token(reset_token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(reset_token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        salt = os.urandom(16)
        password = form.password.data.encode('utf-8')
        hashed_password = hashlib.sha256(salt + password).hexdigest()
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
