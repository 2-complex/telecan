'''
Functions to handle incoming web requests,
then appeal immediately to implentation to do the work.
'''

from flask import render_template
from flask import request
from flask import redirect
from flask import make_response
from flask import abort
from server import app

import implementation
import database

db = database.Database("sqlite:///testing.db")


def get_impl():
    return implementation.Implementation(
        db.models, db.session, request.cookies.get(".SECURITY"))


def index():
    impl = get_impl()
    if impl.is_signed_in():
        return redirect("/home/" + impl.get_username())
    else:
        return render_template("index.html")


def home(username):
    impl = get_impl()
    if impl.is_signed_in():
        return render_template(
            'home.html',
            username = username)
    else:
        return redirect("/")


def users():
    return get_impl().users()


def games():
    criteria = {}
    if request.values.has_key("username"):
        criteria["username"] = request.values["username"]
    return get_impl().games(criteria)


def rounds():
    criteria = {}

    if request.values.has_key("user_id"):
        criteria["user_id"] = request.values["user_id"]

    if request.values.has_key("game_id"):
        criteria["game_id"] = request.values["game_id"]

    return get_impl().rounds(criteria)


def moves():
    criteria = {}
    if request.values.has_key("round_id"):
        criteria["round_id"] = request.values["round_id"]

    return get_impl().moves(criteria)


def new_user():
    return get_impl().new_user(
        username = request.form['username'],
        password = request.form['password'],
        email = request.form['email'])


def user_info():
    if request.values.has_key("username"):
        return get_impl().user_info(request.values["username"])
    abort(404)


def sign_in():
    username = None
    password = None

    if request.values.has_key("password"):
        password = request.values["password"]

    if request.values.has_key("username"):
        username = request.values["username"]

    r = get_impl().sign_in(
        username = request.form['username'],
        password = request.form['password'])
    resp = make_response(r.blob)
    if r.success:
        resp.set_cookie('.SECURITY', r.key)
    return resp


def delete_user():
    return get_impl().delete_user(
        delete_id = request.form['id'])


def new_game():
    return get_impl().new_game(
        user_id = request.form['user_id'],
        title = request.form['title'],
        description = request.form['description'])


def delete_game():
    return get_impl().delete_game(
        delete_id = request.form['id'])


def new_round():
    return get_impl().new_round(
        user_id = request.form['user_id'],
        game_id = request.form['game_id'],
        player_id_string = request.form['players'])


def delete_round():
    return get_impl().delete_round(
        delete_id = request.form['id'])


def new_move():
    return get_impl().new_move(
        round_id = request.form['round_id'],
        user_id = request.form['user_id'],
        content = request.form['content'])


app.add_url_rule('/', 'index', index)
app.add_url_rule('/home/<username>', 'home', home, methods=['GET'])

app.add_url_rule('/users', 'users', users, methods=['GET'])
app.add_url_rule('/games', 'games', games, methods=['GET'])
app.add_url_rule('/rounds', 'rounds', rounds, methods=['GET'])
app.add_url_rule('/moves', 'moves', moves, methods=['GET'])
app.add_url_rule('/new-user', "new-user", new_user, methods=['POST'])
app.add_url_rule('/user-info', "user-info", user_info, methods=['GET'])
app.add_url_rule('/sign-in', "sign-in", sign_in, methods=['POST'])
app.add_url_rule('/delete-user', "delete-user", delete_user, methods=['POST'])
app.add_url_rule('/new-game', "new-game", new_game, methods=['POST'])
app.add_url_rule('/delete-game', "delete-game", delete_game, methods=['POST'])
app.add_url_rule('/new-round', "new-round", new_round, methods=['POST'])
app.add_url_rule('/delete-round', "delete-round", delete_round, methods=['POST'])
app.add_url_rule('/new-move', "new-move", new_move, methods=['POST'])
