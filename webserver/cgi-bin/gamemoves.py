#!/usr/bin/python

import cgi
import json

from db import *
from gameserver import *

print "content-type: text/plain\n"

form = cgi.FieldStorage()

game_id = str(form.getvalue('game'))

server = Server()
server.open()

moves = server.get_game_moves(game_id)
game = server.get_game(game_id)

l = []
for m in moves:
	l.append(m._value_dict())

server.close()

text = json.dumps({'game': game_id, 'moves' : l, 'data' : game.data})

print text

