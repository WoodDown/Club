import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    send_from_directory,
)
from werkzeug.datastructures import FileStorage

import config
from models.message import Messages

from models.user import User
from routes import login_required
from utils import log

main = Blueprint('reset', __name__)
reset_tokens = {}


@main.route("/send", methods=['POST'])
def send():
    form = request.form
    username = form['username']
    token = str(uuid.uuid4())

    u = User.one(username=username)
    reset_tokens[token] = u.id

    if u is not None:
        # 发邮件
        ip = config.ip
        Messages.send(
            title='重置论坛密码',
            content='点击链接重置论坛密码:\nhttp://{}/reset/view?token={}'.format(ip, token),
            # content='点击链接重置论坛密码:\nhttp://localhost:3000/reset/view?token={}'.format(token),
            sender_id=u.id,
            receiver_id=u.id
        )

        log('user reset', username, token, u.id)

    return redirect(url_for("index.index"))


@main.route("/view", methods=['GET'])
@login_required
def view():
    args = request.args
    token = args['token']

    log('user reset', token)

    if token in reset_tokens:
        return render_template("reset/reset.html", token=token)
    else:
        return redirect(url_for("index.index"))


@main.route("/update", methods=['POST'])
@login_required
def update():
    form = request.form
    token = form['token']
    password = form['password']
    user_id = reset_tokens[token]

    u = User.one(id=user_id)
    if u is not None:
        log('user reset', password, token, u.id)
        pwd = User.salted_password(str(password))
        u.update(u.id, password=pwd)

    return redirect(url_for("index.index"))
