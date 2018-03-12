#!/usr/bin/python

import cgi
import sqlite3
import hashlib
import json

from db import *
from gameserver import *

print "content-type: text/plain\n"

# Create instance of FieldStorage
form = cgi.FieldStorage()

name = str(form.getvalue('name'))
pswd = str(form.getvalue('pswd'))
game_id = int(form.getvalue('game'))

text = ''

server = Server()
server.open()


game = server.get_game(game_id)

def make_move_info(move):
	move_info = {}
	move_info['player'] = move.player.name
	move_info['data'] = move.data
	return move_info

info = None

if game:
	moves = server.get_moves(name, pswd, game)
	if moves != None:		
		info = map(make_move_info, moves)
	else:
		info = {'error' : server.error}
else:
	info = {'error' : server.error}

text = json.dumps(info)

print text

