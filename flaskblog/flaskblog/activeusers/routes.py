from flask import Blueprint
from flaskblog.models import ActiveUsers
from flask import Flask, render_template


activeusers = Blueprint('activeusers', __name__)


@activeusers.route("/active_users", methods=['GET', 'POST'])
def active_users():
    activeusers = ActiveUsers.query.all()
    return render_template('active_users.html', title='Active Users', activeusers=activeusers)
