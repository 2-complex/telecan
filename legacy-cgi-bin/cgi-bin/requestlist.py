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
title = str(form.getvalue('title'))


text = ''

server = Server()
server.open()
server._db._debug_mode = False

request_map = server.get_request_map(name, pswd, title)

def get_name(player):
	return player.name

def assemble_request_info(request):
	request_info = {}
	request_info['_id'] = request._id
	request_info['number_of_players'] = request.number_of_players
	request_info['created_at'] = request._created_at
	request_info['updated_at'] = request._updated_at
	if request.game:
		request_info['game'] = request.game._id
		request_info['game_data'] = request.game.data
		request_info['players'] = map(get_name, server.get_players(request.game))
	return request_info

info = None

if request_map != None:
	info = map(assemble_request_info, request_map.keys())
else:
	info = {'error' : server.error}

server.close()

text = json.dumps(info)

print text

