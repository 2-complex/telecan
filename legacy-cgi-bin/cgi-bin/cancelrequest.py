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
request_id = str(form.getvalue('request'))

text = ''

server = Server()
server.open()

request = server.get_request(request_id);

info = {'status' : ''}

if server.cancel_request(name, pswd, title, request):
	info['status'] = 'success'
else:
	info['status'] = server.error

text = json.dumps(info)

print text
