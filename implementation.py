'''
Functions implementing server endpoints,
but without the flask/internet-communication part

These functions interact with the database and return
json blobs.
'''

import json
import hashlib
import re


def merge(dictA, dictB):
    result = dictA.copy()
    result.update(dictB)
    return result


def user_info(user):
    return {"username":user.username, "id":user.id}


def game_info(game):
    return {"title":game.title, "id":game.id}


def get_id(obj):
    return obj.id


def get_name(obj):
    return obj.name


def round_info(round):
    return {
        "id":round.id,
        "game_id":round.game_id,
        "user_id":round.user_id,
        "players":map(user_info, round.players)
    }


def move_info(move):
    return {"user_id":move.user_id, "index":move.index, "content":move.content}


def valid_email(email):
    return None != re.match("[a-zA-Z0-9_\.]+@[a-zA-Z0-9_\.]+$", email)


def valid_username(username):
    return username == username.strip() and None != re.match("[a-zA-Z0-9 _-]+", username)


def salt(password):
    return hashlib.sha256("bananas1312"
        + password
        + "apples132424").hexdigest()


class Implementation:

    def __init__(self, models, session):
        self.models = models
        self.session = session


    def get_user_by_login(self, username, password):
        return self.models.User.query.filter_by(
            username=username, password=password).first()


    def get_user_by_name(self, username):
        return self.models.User.query.filter_by(username=username).first()


    def get_game_by_id(self, game_id):
        return self.models.Game.query.filter_by(id=game_id).first()


    def get_round_by_id(self, round_id):
        return self.models.Round.query.filter_by(id=round_id).first()


    def get_user_by_id(self, user_id):
        return self.models.User.query.filter_by(id=user_id).first()


    def users(self):
        users = self.models.User.query.all()
        return json.dumps({"users":map(user_info, users)})


    def user_info(self, username):
        user = self.get_user_by_name(username)
        if user:
            return json.dumps({
                "username":user.username,
                "id":user.id,
                "email":user.email,
            })

        return json.dumps({"success":False, "reason":"User does not exist"})


    def sign_in(self, username, password):
        user = self.get_user_by_login(username, password)
        if user == None:
            return json.dumps({"success":False, "reason":"Username and password do not match"})

        return json.dumps({"success":True, "sessionid":"ASDFJKLSEMICOLON"})


    def games(self, criteria):
        user = None
        if criteria.has_key("username"):
            user = self.get_user_by_name(criteria["username"])
            if user == None:
                return '{"success" : false}'
            games = self.models.Game.query.filter_by(user_id=user.id)
            return json.dumps({"games":map(game_info, games)})

        games = self.models.Game.query.all()
        return json.dumps(merge( criteria, {"games":map(game_info, games)} ))


    def rounds(self, criteria):
        game = None
        if criteria.has_key("game_id") and criteria.has_key("user_id"):
            game_id = criteria["game_id"]
            user_id = criteria["user_id"]

            rounds = self.models.Round.query.filter_by(game_id=game_id).intersect(
                self.models.Round.query.filter(self.models.Round.players.any(id=user_id)))

            return json.dumps({"rounds":map(round_info, rounds)})

        if criteria.has_key("game_id"):
            rounds = self.models.Round.query.filter_by(game_id=criteria["game_id"])
            return json.dumps({"rounds":map(round_info, rounds)})

        rounds = self.models.Round.query.all()
        return json.dumps({"rounds":map(round_info, rounds)})


    def moves(self, criteria):
        round = None
        if criteria.has_key("round_id"):
            moves = self.models.Move.query.filter_by(round_id=criteria["round_id"])
            return json.dumps({"moves":map(move_info, moves)})

        return json.dumps({"success":False, "reason":"round_id not provided."})


    def new_user(self, username, password, email):
        if len(list(self.models.User.query.filter_by(username=username))) > 0:
            return json.dumps({"success":False, "reason":"A user with this username already exists."})

        if len(list(self.models.User.query.filter_by(email=email))) > 0:
            return json.dumps({"success":False, "reason":"A user with this email already exists."})

        if not valid_username(username):
            return json.dumps({"success":False, "reason":"Username invalid."})

        if not valid_email(email):
            return json.dumps({"success":False, "reason":"Email address not in the form of an email address."})

        user = self.models.User(username, salt(password), email)
        self.session.add(user)
        self.session.commit()
        return json.dumps({"success":True, "id":user.id})


    def delete_user(self, delete_id):
        if type(delete_id) in [str, unicode] and None == re.match("\d+$", delete_id):
            return json.dumps({"success":False, "reason":"User id non-numerical"})

        matching = self.models.User.query.filter_by(id=int(delete_id))
        deleted_ids = map(lambda u: u.id, matching)
        if not len(list(matching)):
            return json.dumps({"success":False, "reason": "User not found."})
        map(self.session.delete, matching)
        self.session.commit()
        return json.dumps({"success":True, "deleted":deleted_ids})


    def new_game(self, user_id, title, description):
        user = self.get_user_by_id(user_id)

        if user == None:
            return json.dumps({"success":False, "reason":"User not found."})

        if len(list(self.models.Game.query.filter_by(user=user, title=title))) > 0:
            return json.dumps({"success":False, "reason":"Duplicate game name " + str(title)})

        game = self.models.Game(user, title, description)
        self.session.add(game)
        self.session.commit()
        return json.dumps({"success":True, "id":game.id})


    def delete_game(self, delete_id):
        if type(delete_id) in [str, unicode] and None == re.match("\d+$", delete_id):
            return json.dumps({"success":False, "reason":"id non-numerical"})

        games = list(self.models.Game.query.filter_by(id=delete_id))

        if len(games) != 1:
            return json.dumps({"success":False})

        rounds = list(self.models.Round.query.filter_by(game_id=delete_id))

        moves = []
        for round in rounds:
            moves += list( self.models.Move.query.filter_by(round_id=round.id) )

        deleted_ids = map(lambda g: g.id, games)

        map(self.session.delete, games + rounds + moves)
        self.session.commit()

        return json.dumps({"success":True, "deleted":deleted_ids})


    def new_round(self, user_id, game_id, player_id_string):
        if type(user_id) in [str, unicode] and None == re.match("\d+$", user_id):
            return json.dumps({"success":False, "reason":"User id non-numerical."})

        if type(game_id) in [str, unicode] and None == re.match("\d+$", game_id):
            return json.dumps({"success":False, "reason":"Game id non-numerical."})

        user = self.get_user_by_id(int(user_id))
        game = self.get_game_by_id(int(game_id))

        if user == None:
            return json.dumps({"success":False, "reason":"User id invalid."})

        if game == None:
            return json.dumps({"success":False, "reason":"Game id invalid."})

        player_ids = map(int, [m.string[m.span()[0]:m.span()[1]] for m in re.finditer("\d+", player_id_string)])

        if len(player_ids) == 0:
            return json.dumps({"success":False, "reason":"Player ids invalid."})

        players = []
        for player_id in map(int, player_ids):
            if player_id == 0:
                return json.dumps({"success":False, "reason":"Player id 0"})
            player = self.get_user_by_id(player_id)
            if player == None:
                return json.dumps({"success":False, "reason":"Player not found: " + str(player_id)})
            players.append( player )

        round = self.models.Round(user, game)
        for player in players:
            round.players.append(player)

        self.session.add(round)
        self.session.commit()

        return json.dumps({"success":True, "id":round.id})


    def delete_all_rounds(self):
        map(self.session.delete, self.models.Round.query.all())
        map(self.session.delete, self.models.Move.query.all())
        self.session.commit()
        return json.dumps({"success" : True, "deleted" : "everything"})


    def delete_round(self, delete_id):
        if type(delete_id) in [str, unicode] and None == re.match("\d+$", delete_id):
            return json.dumps({"success":False, "reason":"id non-numerical"})

        rounds = list(self.models.Round.query.filter_by(id=delete_id))
        if len(rounds) != 1:
            return json.dumps({"success" : False})

        round = rounds[0]
        deleted_ids = map(lambda g: g.id, rounds)
        moves = list(self.models.Move.query.filter_by(round_id=round.id))
        map(self.session.delete, rounds + moves)

        self.session.commit()
        return json.dumps({"success" : True, "deleted" : deleted_ids})


    def new_move(self, round_id, user_id, content):
        user = self.get_user_by_id(user_id)
        round = self.get_round_by_id(round_id)
        move = self.models.Move(round, user, content)
        self.session.add(move)
        self.session.commit()
        return json.dumps({"success":True, "id":move.id})

