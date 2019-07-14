import uuid

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    current_app)

from models.user import User
from routes import current_user, login_required
from routes.redis_cache import cache

from utils import log

main = Blueprint('index', __name__)


@main.route("/")
def index():
    u = current_user()
    return render_template("index.html", user=u)


@main.route("/register", methods=['POST'])
def register():
    # form = request.args
    form = request.form
    log('register form', form)

    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/register/view", methods=['POST'])
def register_view():
    return render_template("register.html")


@main.route("/reset/password", methods=['POST'])
def reset_pwd_view():
    return render_template("reset_pwd.html")


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    log('login user <{}>'.format(u))

    if u is None:
        return redirect(url_for('.index'))
    else:
        session_id = str(uuid.uuid4())
        k = 'session_id_{}'.format(session_id)
        v = u.id
        cache.set(k, v)

        redirect_to_index = redirect(url_for('bp_topic.index'))
        response = current_app.make_response(redirect_to_index)
        response.set_cookie('session_id', value=session_id)

        return response


@main.route('/profile')
@login_required
def profile():
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        return render_template('profile.html', user=u)


@main.route('/user/<int:id>')
@login_required
def user_detail(id):
    u = User.one(id=id)
    if u is None:
        abort(404)
    else:
        return render_template('profile.html', user=u)


def not_found(e):
    return render_template('404.html')
