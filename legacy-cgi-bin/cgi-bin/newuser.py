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
data = str(form.getvalue('data'))

if not data:
	data = ""

text = ''

server = Server()
server.open()

info = {'status' : ''}

if server.create_account(name, pswd, data):
	info['status'] = 'success'
else:
	info['status'] = server.error

server.close()

text = json.dumps(info)

print text
