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
number_of_players = str(form.getvalue('number_of_players'))
data = str(form.getvalue('data'))

text = ''

server = Server()
server.open()

info = {'status' : ''}

if server.create_request(name, pswd, title, number_of_players, data):
	info['status'] = 'success'
else:
	info['status'] = server.error

text = json.dumps(info)

print text

