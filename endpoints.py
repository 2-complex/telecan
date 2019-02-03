'''
Functions to handle incoming web requests,
then appeal immediately to implentation to do the work.
'''

from flask import render_template
from flask import request
from flask import make_response
from flask import abort
from server import app

import implementation
import database

db = database.Database("sqlite:///testing.db")
impl = implementation.Implementation(db.models, db.session)



def index():
    return render_template('index.html')


def home(username):
    return render_template(
        'home.html',
        username = username)


def users():
    return impl.users()


def games():
    criteria = {}
    if request.values.has_key("username"):
        criteria["username"] = request.values["username"]
    return impl.games(criteria)


def rounds():
    criteria = {}

    if request.values.has_key("user_id"):
        criteria["user_id"] = request.values["user_id"]

    if request.values.has_key("game_id"):
        criteria["game_id"] = request.values["game_id"]

    return impl.rounds(criteria)


def moves():
    criteria = {}
    if request.values.has_key("round_id"):
        criteria["round_id"] = request.values["round_id"]

    return impl.moves(criteria)


def new_user():
    return impl.new_user(
        username = request.form['username'],
        password = request.form['password'],
        email = request.form['email'])


def user_info():
    if request.values.has_key("username"):
        return impl.user_info(request.values["username"])
    abort(404)


def sign_in():
    username = None
    password = None

    if request.values.has_key("password"):
        password = request.values["password"]

    if request.values.has_key("username"):
        username = request.values["username"]

    if username!=None and password!=None:
        print repr(username)
        print repr(password)

        return impl.sign_in(username, password)

    abort(404)


def delete_user():
    return impl.delete_user(
        delete_id = request.form['id'])


def new_game():
    return impl.new_game(
        user_id = request.form['user_id'],
        title = request.form['title'],
        description = request.form['description'])


def delete_game():
    return impl.delete_game(
        delete_id = request.form['id'])


def new_round():
    return impl.new_round(
        user_id = request.form['user_id'],
        game_id = request.form['game_id'],
        player_id_string = request.form['players'])


def delete_round():
    return impl.delete_round(
        delete_id = request.form['id'])


def new_move():
    return impl.new_move(
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
app.add_url_rule('/sign-in', "sign-in", sign_in, methods=['GET'])
app.add_url_rule('/delete-user', "delete-user", delete_user, methods=['POST'])
app.add_url_rule('/new-game', "new-game", new_game, methods=['POST'])
app.add_url_rule('/delete-game', "delete-game", delete_game, methods=['POST'])
app.add_url_rule('/new-round', "new-round", new_round, methods=['POST'])
app.add_url_rule('/delete-round', "delete-round", delete_round, methods=['POST'])
app.add_url_rule('/new-move', "new-move", new_move, methods=['POST'])

