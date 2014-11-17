#!/usr/bin/python

import cgi
import json

from db import *
from gameserver import *

print "content-type: text/plain\n"

# Create instance of FieldStorage
form = cgi.FieldStorage()

name = str(form.getvalue('name'))
pswd = str(form.getvalue('pswd'))
game_id = int(form.getvalue('game'))
data = str(form.getvalue('data'))
game_data = str(form.getvalue('game_data'))

if not data:
	data = ""

if not game_data:
	game_data = ""

text = ''

server = Server()
server.open()

game = server.get_game(game_id)
info = {'status':''}

if game and server.make_move(name, pswd, game, data, game_data):
	info['status'] = 'success'
else:
	info['status'] = server.error

server.close()

text = json.dumps(info)

print text

