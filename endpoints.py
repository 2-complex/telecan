'''
Functions to handle incoming web requests,
then appeal immediately to implentation to do the work.
'''

from flask import render_template
from flask import request
from flask import make_response
from server import app

import implementation
import database

db = database.Database("sqlite:///testing.db")
impl = implementation.Implementation(db.models, db.session)


@app.route('/')
def r_index():
    return render_template('index.html')


@app.route('/<username>', methods=['GET'])
def r_home(username):
    return render_template(
        'home.html',
        username = username)


@app.route('/users', methods=['GET'])
def r_users():
    return impl.users()


@app.route('/games', methods=['GET'])
def r_games():
    criteria = {}
    if request.values.has_key("username"):
        criteria["username"] = request.values["username"]

    return impl.games(criteria)


@app.route('/rounds', methods=['GET'])
def r_rounds():
    criteria = {}
    if request.values.has_key("game_id"):
        criteria["game_id"] = request.values["game_id"]

    return impl.rounds(criteria)


@app.route('/moves', methods=['GET'])
def r_moves():
    return impl.moves()


@app.route('/new-user', methods=['POST'])
def r_new_user():
    return impl.new_user(
        username = request.form['username'],
        password = request.form['password'],
        email = request.form['email'])


@app.route('/sign-in', methods=['POST'])
def r_sign_in():
    r = impl.sign_in(
        username = request.form['username'],
        password = request.form['password'])
    if r.success:
        resp = make_response(r.message)
        resp.set_cookie('.SECURITY', r.key)
    else:
        resp = make_response(r.message)
    return resp


@app.route('/delete-user', methods=['POST'])
def r_delete_user():
    return impl.delete_user(
        delete_id = request.form['id'])


@app.route('/new-game', methods=['POST'])
def new_game():
    return impl.new_game(
        user_id = request.form['user_id'],
        title = request.form['title'],
        description = request.form['description'])


@app.route('/delete-game', methods=['POST'])
def delete_game():
    return impl.delete_game(
        delete_id = request.form['id'])


@app.route('/new-round', methods=['POST'])
def r_new_round():
    return impl.new_round(
        user_id = request.form['user_id'],
        game_id = request.form['game_id'],
        player_id_string = request.form['players'])


@app.route('/delete-round', methods=['POST'])
def r_delete_round():
    return impl.delete_round(
        delete_id = request.form['id'])


@app.route('/new-move', methods=['POST'])
def r_new_move():
    return impl.new_move(
        round_id = request.form['round_id'],
        user_id = request.form['user_id'],
        content = request.form['content'])

