import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    send_from_directory)
from werkzeug.datastructures import FileStorage


from models.reply import Reply
from models.topic import Topic
from routes import current_user, login_required

from models.user import User
from routes.redis_cache import cache
from utils import log


main = Blueprint('bp_user', __name__)


@main.route("/")
@login_required
def index():
    u = current_user()

    ms, ts = data_form_user(u)
    return render_template("user/user.html", u=u, ms=ms, ts=ts)


def new_csrf_token():
    u = current_user()
    token = str(uuid.uuid4())

    csrf_token = 'csrf_token_{}'.format(token)
    cache.set(csrf_token, u.id)

    log('cache token', cache, cache.get(csrf_token), u.id)
    return csrf_token


@main.route("/setting")
@login_required
def setting():
    u = current_user()
    token = new_csrf_token()

    return render_template("user/setting.html", u=u, token=token)


@main.route("/change_name", methods=['POST'])
@login_required
def change_name():
    u: User = current_user()
    form = request.form
    u.update(u.id, **form)

    return redirect(url_for(".setting"))


@main.route("/reset_password", methods=['POST'])
@login_required
def reset_password():
    form = request.form
    password = form['new_pass']
    token = form['token']

    user_id = cache.get(token)
    log('reset_pwd token', token, user_id)
    u = User.one(id=user_id)

    if u is not None:
        pwd = User.salted_password(str(password))
        u.update(u.id, password=pwd)

    return redirect(url_for(".setting"))


@main.route('/image/add', methods=['POST'])
@login_required
def avatar_add():
    file: FileStorage = request.files['avatar']
    suffix = file.filename.split('.')[-1]
    filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
    path = os.path.join('static/images', filename)
    log('path', path)
    file.save(path)

    u = current_user()
    User.update(u.id, image='/static/images/{}'.format(filename))

    return redirect(url_for('.index'))


@main.route('/images/<filename>')
@login_required
def image(filename):
    log('images path', filename)
    return send_from_directory('images', filename)


@main.route('/view/<int:id>')
@login_required
def detail(id):
    u = User.one(id=id)

    ms, ts = data_form_user(u)
    return render_template("user/user.html", u=u, ms=ms, ts=ts)


def data_form_user(u):
    ms = Topic.all(user_id=u.id)
    rs = Reply.all(user_id=u.id)
    ms = reverse(ms)
    ts = reply_filter(rs)
    ts = reverse(ts)
    return ms, ts


def reverse(arr):
    l = arr
    result = []
    for i in range(len(l)):
        result.append(l[len(l) - i - 1])
    return result


def reply_filter(reply):
    rs = reply
    ts = []
    result = []
    for r in rs:
        t = Topic.one(id=r.topic_id)
        ts.append(t)
    for t in ts:
        if len(result) == 0:
            result.append(t)
        elif t not in result:
            result.append(t)
    return result
