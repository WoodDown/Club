from functools import wraps

from flask import session, request, redirect, url_for

from models.user import User
from routes.redis_cache import cache
from utils import log


def current_user():
    if 'session_id' in request.cookies:
        session_id = request.cookies['session_id']
        # redis session key
        key = 'session_id_{}'.format(session_id)
        user_id = int(cache.get(key))

        if user_id is None:
            return User.guest()
        else:
            u = User.one(id=user_id)
            if u is None:
                return User.guest()
            else:
                return u
    else:
        return User.guest()


def login_required(route_function):
    @wraps(route_function)
    def f(**ars):
        u = current_user()
        # log('login required user u', u)
        if u.username == '【游客】':
            # log('login required index_view')
            return redirect(url_for("index.index"))
        else:
            # log('login required route_function')
            return route_function(**ars)
    return f


def admin_required(route_function):
    @wraps(route_function)
    def f():
        u = current_user()
        if u.username == '【管理员】':
            return redirect(url_for("index.index"))
        else:
            return route_function()
    return f