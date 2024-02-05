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

activeusers = Blueprint('activeusers', __name__)


@activeusers.route("/active_users", methods=['GET', 'POST'])
def active_users():
    activeusers = ActiveUsers.query.all()
    return render_template('active_users.html', title='Active Users', activeusers=activeusers)
