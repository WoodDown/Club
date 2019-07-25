from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.board import Board
from routes import current_user, login_required

from models.topic import Topic
from utils import log

main = Blueprint('bp_topic', __name__)


@main.route("/")
@login_required
def index():
    u = current_user()

    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        ms = Topic.all()
    else:
        ms = Topic.all(board_id=board_id)
    bs = Board.all()

    log('login required index route', u, ms)
    return render_template("topic/index.html", u=u, ms=ms, bs=bs, bid=board_id)


@main.route('/<int:id>')
@login_required
def detail(id):
    u = current_user()
    m = Topic.get(id)
    return render_template("topic/detail.html", u=u, topic=m)


@main.route("/add", methods=["POST"])
@login_required
def add():
    form = request.form.to_dict()
    u = current_user()
    m = Topic.add(form, user_id=u.id)
    return redirect(url_for('.detail', id=m.id))


@main.route("/new")
@login_required
def new():
    u = current_user()

    # all board_id: 1
    board_id = request.args.get('board_id', 1)
    bs = Board.all()
    return render_template("reply/new.html", u=u, bs=bs, bid=board_id)

