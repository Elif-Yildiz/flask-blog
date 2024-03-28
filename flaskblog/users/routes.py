from flask import Blueprint, current_app, session
from datetime import datetime

from flaskblog.models import User, Post, ActiveUsers
from flask import Flask, render_template, url_for, flash, request, redirect, abort
from flaskblog import db
from flask_login import login_user, logout_user, current_user, login_required
import hashlib
import os

from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import save_picture, send_reset_email, send_notification_email
import requests

users = Blueprint('users', __name__)  # Blue print


# register route
@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))  # if user is already logged in no need register again

    form = RegistrationForm()

    if form.validate_on_submit():

        try:  # date data formating
            birthdate_str = form.birthdate.data
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid birthdate format. Please use YYYY-MM-DD.', 'danger')
            return redirect(url_for('users.register'))

        salt = os.urandom(16)  # generate salt
        password = form.password.data.encode('utf-8')
        hashed_password = hashlib.sha256(salt + password).hexdigest()  # add salt and hash the pswd
        # create user
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password,
                    active=False,
                    firstname=form.firstname.data,
                    lastname=form.lastname.data,
                    middlename=form.middlename.data,
                    birthdate=birthdate,
                    salt=salt)
        # save user to db
        db.session.add(user)
        db.session.commit()

        flash(f'{form.username.data}, your account has been created!You can log in.', 'success')  # msg
        current_app.logger.info(f"A NEW ACCOUNT HAS BEEN CREATED: {user.username}")  # LOG
        return redirect(url_for('users.login'))  # redirect them to login page so they can log in
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # do not allow second login
        return redirect(url_for('main.home'))
    form = LoginForm()
    recaptcha_site_key = current_app.config.get('reCAPTCHA_SITE_KEY')
    if form.validate_on_submit():  # check if data matches, then allow to log in
        user = User.query.filter_by(email=form.email.data).first()
        entered_password = form.password.data.encode('utf-8')
        stored_salt = user.salt
        hashed_password = hashlib.sha256(stored_salt + entered_password).hexdigest()

        # recaptcha verifying part
        secret_response = request.form['g-recaptcha-response']
        recaptcha_verify_url = current_app.config.get('reCAPTCHA_VERIFY_URL')
        recaptcha_secret_key = current_app.config.get('reCAPTCHA_SECRET_KEY')
        verify_response = requests.post(
            url=f'https://www.google.com/recaptcha/api/siteverify?secret=6Le1GaUpAAAAAFmYnBByF57FFGa8C1Vnbnfe7vDy&response={secret_response}',
            verify=False).json()
        current_app.logger.info(verify_response)

        if user is not None and user.password == hashed_password:  # compare pswds
            if verify_response['success'] is not True or verify_response['score'] < 0.85:
                flash('YOU CAN NOT FOOL ME, ROBOT!')
                current_app.logger.info(f"Bot Attack attempt")
                abort(401)

            login_user(user, remember=form.remember.data)  # login
            next_page = request.args.get('next')
            # add user to active users
            active_user = ActiveUsers(user_id=user.id, login_time=datetime.utcnow(), ip=request.remote_addr)
            db.session.add(active_user)
            db.session.commit()
            current_app.logger.info(f"USER {user.username}:{user.id} logged in")  # LOG
            session.pop('login_attempts', None)  # clear failed login attempts
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful!', 'danger')
            current_app.logger.info(f"USER FAILED TO LOG IN, Entered Password: {entered_password}")  # LOG
            # Increment the login attempt counter
            session['login_attempts'] = session.get('login_attempts', 0) + 1
            # Inform user after 3 unsuccessful login attempts
            if session.get('login_attempts') >= 3:
                # Send notification to the user
                send_notification_email(request.form['email'])
                flash('OPEN UP FBI!', 'danger')

    return render_template('login.html', title='Login', form=form, site_key=recaptcha_site_key)


@users.route("/logout")
@login_required
def logout():
    # Remove user from ActiveUsers table
    if current_user.is_authenticated:
        active_user = ActiveUsers.query.filter_by(user_id=current_user.id).first()
        if active_user:
            db.session.delete(active_user)
            db.session.commit()
    logout_user()
    current_app.logger.info(f"USER LOGGED OUT")  # LOG
    return redirect(url_for('main.home'))


''' displays user info(username,mail,profile pic) and can change the info, if logged in'''


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():  # saving any change made
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
def user_posts(username):  # displaying a user's all posts
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/user/list")
def user_list():  # displaying all users
    users = User.query.all()
    posts = Post.query.all()
    return render_template('user_list.html', users=users, posts=posts)


''' sending reset mail'''


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        current_app.logger.info(f"RESET MAIL SENT")  # LOG
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)
    # return render_template('coming_soon.html', title='Reset Password', form=form) #anything bad happens quick mesure


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
        user.salt = salt
        db.session.commit()
        current_app.logger.info(f"PASSWORD HAS BEEN CHANGED")  # LOG
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
    # return render_template('coming_soon.html', title='Reset Password', form=form) #quick change for anything bag happens
