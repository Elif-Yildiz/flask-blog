from flask import url_for
from flaskblog import app, db, mail
import os
import secrets
from PIL import Image
from flask_mail import Message


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn


def send_reset_email(user):
    reset_token = user.get_reset_token()
    msg = Message('Password Reset Request', recipients=[user.email])
    msg.body = f'''To reset your password, click on the link below:
    {url_for('reset_token', sender='elify2258@gmail.com', reset_token=reset_token, _external=True)}

    If you did not make this request then simply ignore this email.
    '''  # can also use jinja2 template, look for that maybe?
    mail.send(msg)
