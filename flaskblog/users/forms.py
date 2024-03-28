import re
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.fields.simple import BooleanField
from flaskblog.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    firstname = StringField('Firstname', validators=[DataRequired(), Length(min=2, max=20)])
    middlename = StringField('Middlename', validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Lastname', validators=[DataRequired(), Length(min=2, max=20)])

    birthdate = StringField('Birthday', validators=[DataRequired()])

    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    #check if user name is valid
    def validate_username(self, username):

        if re.search(r'[\/\\&|]', username.data):
            raise ValidationError('Username cannot contain "/", "\", "&", or "|". Please choose a different one.')
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is taken. Please choose a different one.')

    ##check if mail is valid
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is taken. Please choose a different one.')

    #check password req, 8> 1uppercase 1lowercase 1digit
    def validate_password(self, password):

        if len(password.data) < 8:
            raise ValidationError('Password must be at least 8 characters long.')

        if not re.search(r'[A-Z]', password.data):
            raise ValidationError('Password must contain at least one uppercase letter.')

        if not re.search(r'[a-z]', password.data):
            raise ValidationError('Password must contain at least one lowercase letter.')

        if not re.search(r'[0-9]', password.data):
            raise ValidationError('Password must contain at least one digit.')

    recaptcha = RecaptchaField()


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])

    def validate_username(self, username):
        if username.data != current_user.username:
            if re.search(r'[\/\\&|]', username.data):
                raise ValidationError('Username cannot contain "/", "\", "&", or "|". Please choose a different one.')

            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is taken. Please choose a different one.')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No such user')

    recaptcha = RecaptchaField()


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
