from flask import Blueprint
from flaskblog.models import User, Post
from flask import render_template, request

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


@main.route("/about")
def about():
    return render_template('about.html', title='About')


@main.route("/music")
def music():
    return render_template('music.html', title='Music')


@main.route("/etc")
def etc():
    return render_template('gate.html', title='Gate')


@main.route("/secret")
def secret():
    return render_template('secret.html', title='secret')


@main.route("/test", methods=['GET', 'POST'])
def test():
    return render_template('test.html', title='CaptchaTest')
