import time

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# web framework
# web application
# __main__
import secret
from config import db_name
from models.base_model import db
from models.board import Board
from models.reply import Reply
from models.topic import Topic
from models.user import User
from routes import index, admin_required
from utils import log

from routes.index import main as index_routes
from routes.topic import main as topic_routes
from routes.reply import main as reply_routes
from routes.user import main as user_routes
from routes.message import main as mail_routes
from routes.reset import main as reset_routes
from routes.index import not_found


# @app.template_filter()
def count(input):
    log('count using jinja filter')
    return len(input)


def format_time(unix_timestamp):
    # enum Year():
    #     2013
    #     13
    # f = Year.2013
    f = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(unix_timestamp)
    formatted = time.strftime(f, value)
    return formatted


def configured_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:{}@localhost/{}?charset=utf8mb4'.format(
        secret.database_password,
        db_name,
    )
    db.init_app(app)

    app.register_blueprint(index_routes)
    app.register_blueprint(topic_routes, url_prefix='/topic')
    app.register_blueprint(reply_routes, url_prefix='/reply')
    app.register_blueprint(user_routes, url_prefix='/user')
    app.register_blueprint(mail_routes, url_prefix='/mail')
    app.register_blueprint(reset_routes, url_prefix='/reset')
    log('url map', app.url_map)

    app.template_filter()(count)
    app.template_filter()(format_time)
    app.errorhandler(404)(not_found)

    admin = Admin(app, name=db_name, template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Topic, db.session))
    admin.add_view(ModelView(Reply, db.session))
    admin.add_view(ModelView(Board, db.session))

    return app


if __name__ == '__main__':
    app = configured_app()
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    config = dict(
        debug=True,
        host='0.0.0.0',
        port=80,
    )
    app.run(**config)
