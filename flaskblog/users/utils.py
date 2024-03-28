from flask import url_for, current_app
from flask_login import current_user

from flaskblog import mail
import os
import secrets
from PIL import Image
from flask_mail import Message


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    prev_picture = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
    if os.path.exists(prev_picture) and os.path.basename(prev_picture) != 'default.jpg':
        os.remove(prev_picture)

    return picture_fn


def send_reset_email(user):
    reset_token = user.get_reset_token()
    msg = Message('Password Reset Request', recipients=[user.email])
    msg.body = f'''To reset your password, click on the link below:
    {url_for('users.reset_token', sender='hosts2661@gmail.com', reset_token=reset_token, _external=True)}

    If you did not make this request then simply ignore this email.
    '''  # can also use jinja2 template, look for that maybe?
    mail.send(msg)


def send_notification_email(m):
    msg = Message('Failed Log In attempts', recipients=[m])
    msg.body = f'''Alert!!! multiple attempts to log in to a account for {m}, if that was you simply ignore this.'''
    mail.send(msg)

