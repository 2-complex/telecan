import database

from sqlalchemy import Table, Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from slugify import slugify

import os, base64

_round_players = Table('players', database.Model.metadata,
    Column('round_id', Integer, ForeignKey('rounds.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)


class User(database.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False, server_default='')
    email = Column(String(255), nullable=False, unique=True)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email


def generate_session_key():
    return base64.b64encode(os.urandom(200))[:-2]


class Session(database.Model):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    key = Column(String(200), nullable=False, server_default='')

    user = relationship('User', backref=backref('sessions', lazy='dynamic'))
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, user):
        self.user = user
        self.key = generate_session_key()


class Game(database.Model):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    url_slug = Column(String(200))
    description = Column(Text)

    user = relationship('User', backref=backref('games', lazy='dynamic'))
    user_id = Column(Integer, ForeignKey('users.id'))

    def set_title(self, title):
        self.title = title
        self.url_slug = slugify(unicode(title))

    def __init__(self, user, title, description):
        self.user = user
        self.set_title( title )
        self.description = description

    def __repr__(self):
        return '<Game %s/%s>' % (self.user.username, self.url_slug)


class Round(database.Model):
    __tablename__ = 'rounds'
    id = Column(Integer, primary_key=True)

    game = relationship('Game', backref=backref('rounds', lazy='dynamic'))
    game_id = Column(Integer, ForeignKey('games.id'))

    user = relationship('User', backref=backref('rounds', lazy='dynamic'))
    user_id = Column(Integer, ForeignKey('users.id'))

    players = relationship("User",
        secondary = _round_players,
        backref = "current_rounds")

    def __init__(self, user, game):
        self.user = user
        self.game = game

    def __repr__(self):
        return '<Round %s>'%str(self.id)


class Move(database.Model):
    __tablename__ = 'moves'
    id = Column(Integer, primary_key=True)

    round = relationship('Round', backref=backref('rounds', lazy='dynamic'))
    round_id = Column(Integer, ForeignKey('rounds.id'))

    user = relationship('User', backref=backref('moves', lazy='dynamic'))
    user_id = Column(Integer, ForeignKey('users.id'))

    index = Column(Integer)
    content = Column(Text)

    def __init__(self, round, user, content):
        self.round = round
        self.user = user
        self.content = content

    def __repr__(self):
        return '<Move>'

