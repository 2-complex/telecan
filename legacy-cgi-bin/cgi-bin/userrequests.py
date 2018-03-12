#!/usr/bin/python

import cgi
import json

from db import *
from gameserver import *

print "content-type: text/plain\n"

form = cgi.FieldStorage()

name = str(form.getvalue('name'))

server = Server()
server.open()

requests = server.get_user_requests(name)

l = []
for r in requests:
	l.append(r._value_dict())

text = json.dumps({'user':name, 'requests':l})

server.close()

print text

