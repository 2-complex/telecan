'''
Functions implementing server endpoints,
but without the flask/internet-communication part

These functions interact with the database and return
json blobs.
'''

from models import *
import json
import sqlalchemy
import re

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


def valid_email(email):
    return None != re.match("[a-zA-Z0-9_\.]+@[a-zA-Z0-9_\.]+$", email)


def valid_username(username):
    return username == username.strip() and None != re.match("[a-zA-Z0-9 _-]+", username)


def capitalize(s):
    return s[0].upper() + s[1:]


class Implementation:

    def __init__(self, models, session):
        self.models = models
        self.session = session


    def get_game_by_id(self, game_id):
        return self.models.Game.query.filter_by(id=game_id).first()


    def get_round_by_id(self, round_id):
        return self.models.Round.query.filter_by(id=round_id).first()


    def get_user_by_id(self, user_id):
        return self.models.User.query.filter_by(id=user_id).first()


    def users(self):
        users = self.models.User.query.all()
        return json.dumps({"users":map(user_info, users)})


    def games(self):
        games = self.models.Game.query.all()
        return json.dumps({"games":map(game_info, games)})


    def rounds(self):
        rounds = self.models.Round.query.all()
        return json.dumps({"rounds":map(round_info, rounds)})


    def moves(self, round_id):
        moves = self.models.Move.query.filter_by(round_id=round_id)
        return json.dumps({"moves":map(move_info, moves)})


    def new_user(self, username, password, email):
        if len(list(self.models.User.query.filter_by(username=username))) > 0:
            return json.dumps({"success":False, "reason":"A user with this username already exists."})

        if len(list(self.models.User.query.filter_by(email=email))) > 0:
            return json.dumps({"success":False, "reason":"A user with this email already exists."})

        if not valid_username(username):
            return json.dumps({"success":False, "reason":"Username invalid."})

        if not valid_email(email):
            return json.dumps({"success":False, "reason":"Email address not in the form of an email address."})

        user = User(username, password, email)
        self.session.add(user)
        self.session.commit()
        return json.dumps({"success":True, "id":user.id})


    def delete_object(self, Class, name, delete_id):
        matching = Class.query.filter_by(id=int(delete_id))
        deleted_ids = map(lambda u: u.id, matching)
        if not len(list(matching)):
            return json.dumps({"success":False, "reason": capitalize(name) + " not found."})
        map(self.session.delete, matching)
        self.session.commit()
        return json.dumps({"success":True, "deleted":deleted_ids})


    def delete_user(self, delete_id):
        return self.delete_object(self.models.User, "User", delete_id)


    def new_game(self, user_id, title, description):
        user = self.get_user_by_id(user_id)

        if user == None:
            return json.dumps({"success":False, "reason":"User not found."})

        game = Game(user, title, description)
        self.session.add(game)
        self.session.commit()
        return json.dumps({"success":True, "id":game.id})


    def delete_game(self, delete_id):
        games = list(Game.query.filter_by(id=delete_id))

        if len(games) != 1:
            return json.dumps({"success":False})

        rounds = list(Round.query.filter_by(game_id=delete_id))

        moves = []
        for round in rounds:
            moves += list( Move.query.filter_by(round_id=round.id) )

        deleted_ids = map(lambda g: g.id, games)

        map(self.session.delete, games + rounds + moves)
        self.session.commit()

        return json.dumps({"success":True, "deleted":deleted_ids})


    def new_round(self, user_id, game_id, player_ids):
        user = self.get_user_by_id(user_id)
        game = self.get_game_by_id(game_id)
        players = map(int, player_ids.split(','))

        round = Round(user, game)

        for player in map(self.get_user_by_id, players):
            round.players.append( player )

        self.session.add(round)
        self.session.commit()

        return json.dumps({"success":True, "id":round.id})


    def delete_round(self, delete_id):
        rounds = list(Round.query.filter_by(id=delete_id))
        if len(rounds) != 1:
            return json.dumps({"success" : False})

        deleted_ids = map(lambda g: g.id, rounds)

        moves = []
        for round in rounds:
            moves += Move.query.filter_by(round_id=round.id)

        map(self.session.delete, rounds + moves)

        self.session.commit()
        return json.dumps({"success" : True, "deleted" : deleted_ids})


    def new_move(self, round_id, user_id, content):
        user = self.get_user_by_id(user_id)
        round = self.get_round_by_id(round_id)
        move = Move(round, user, content)
        self.session.add(move)
        self.session.commit()
        return json.dumps({"success":True, "id":move.id})

