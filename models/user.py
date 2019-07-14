import hashlib

from sqlalchemy import Column, String, Text
from werkzeug.datastructures import ImmutableMultiDict

import config
import secret
from models.base_model import SQLMixin, db
from utils import log


class User(SQLMixin, db.Model):
    __tablename__ = 'User'
    username = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)
    image = Column(String(100), nullable=False, default='/static/user.jpg')
    signature = Column(String(100), nullable=False, default='这家伙很懒，什么个性签名都没有留下。')
    email = Column(String(50), nullable=False, default=config.test_mail)

    @staticmethod
    def salted_password(password, salt='$!@><?>HUI&DWQa`'):
        salted = hashlib.sha256((password + salt).encode('ascii')).hexdigest()
        return salted

    @classmethod
    def register(cls, form):
        name = form.get('username', '')
        print('register', form)
        if len(name) > 2 and User.one(username=name) is None:
            d = {}
            d['username'] = form['username']
            d['password'] = User.salted_password(form['password'])
            u = User.new(d)
            return u
        else:
            return None

    @classmethod
    def validate_login(cls, form):
        query = dict(
            username=form['username'],
            password=User.salted_password(form['password']),
        )
        log('validate_login', form, query)
        return User.one(**query)

    @classmethod
    def guest(cls):
        u = User()
        u.username = '【游客】'
        return u
