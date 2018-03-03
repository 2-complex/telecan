import database
import json

from flask import render_template
from flask import request

from server import app
import json

from models import *

@app.route('/')
def index():
    return render_template('index.html')

def user_info(user):
    return {"username":user.username, "id":user.id}

def game_info(game):
    return {"title":game.title, "id":game.id}


def get_id(obj):
    return obj.id

def round_info(round):
    return {
        "id":round.id,
        "game_id":round.game_id,
        "user_id":round.user_id,
        "players":map(get_id, round.players)}

def move_info(move):
    return {"user_id":move.user_id, "index":move.index, "content":move.content}

@app.route('/users', methods=['GET'])
def r_users():
    users = User.query.all()
    return json.dumps({"users":map(user_info, users)})


@app.route('/games', methods=['GET'])
def r_games():
    games = Game.query.all()
    return json.dumps({"games":map(game_info, games)})


@app.route('/rounds', methods=['GET'])
def r_rounds():
    rounds = Round.query.all()
    return json.dumps({"rounds":map(round_info, rounds)})


@app.route('/moves', methods=['GET'])
def r_moves():
    moves = Move.query.all()
    return json.dumps({"moves":map(move_info, moves)})


@app.route('/new-user', methods=['POST'])
def r_new_user():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    user = User(username, password, email)
    database.session.add(user)
    database.session.commit()

    return json.dumps({"success":"true", "id":user.id})


@app.route('/delete-user', methods=['POST'])
def r_delete_user():
    delete_id = request.form['id']
    users_matching = User.query.filter_by(id=int(delete_id))
    map(database.session.delete, users_matching)
    database.session.commit()
    return json.dumps({"users-deleted":map(lambda u: u.id, users_matching)})


def get_user_by_id(user_id):
    return User.query.filter_by(id=user_id).first()

def get_game_by_id(game_id):
    return Game.query.filter_by(id=game_id).first()

def get_round_by_id(round_id):
    return Round.query.filter_by(id=round_id).first()


@app.route('/new-game', methods=['POST'])
def r_new_game():
    user_id = request.form['user_id']
    title = request.form['title']
    description = request.form['description']

    user = get_user_by_id(user_id)

    game = Game(user, title, description)
    database.session.add(user)
    database.session.commit()

    return json.dumps({"success":"true", "id":game.id})


@app.route('/delete-game', methods=['POST'])
def r_delete_game():
    delete_id = request.form['id']
    games_matching = Game.query.filter_by(id=delete_id)
    map(database.session.delete, games_matching)
    database.session.commit()
    return json.dumps({"games-deleted":map(lambda g: g.id, games_matching)})


@app.route('/new-round', methods=['POST'])
def r_new_round():
    user_id = request.form['user_id']
    game_id = request.form['game_id']
    players_ids = request.form['players']

    user = get_user_by_id(user_id)
    game = get_game_by_id(game_id)
    players = map(int, players_ids.split(','))

    round = Round(user, game)

    for player in map(get_user_by_id, players):
        round.players.append( player )

    database.session.add(round)
    database.session.commit()

    return json.dumps({"success":"true", "id":game.id})


@app.route('/delete-round', methods=['POST'])
def r_delete_round():
    delete_id = request.form['id']
    rounds_matching = Round.query.filter_by(id=delete_id)
    map(database.session.delete, rounds_matching)
    database.session.commit()
    return json.dumps({"rounds-deleted":map(lambda g: g.id, rounds_matching)})


def i_new_move(round_id, user_id, content):
    user = get_user_by_id(user_id)
    round = get_round_by_id(round_id)
    move = Move(round, user, content)
    database.session.add(move)
    database.session.commit()
    return json.dumps({"success":"true", "id":move.id})




@app.route('/new-move', methods=['POST'])
def r_new_move():
    return i_new_move(
        round_id = request.form['round_id'],
        user_id = request.form['user_id'],
        content = request.form['content'])


