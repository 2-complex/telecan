#!/usr/bin/python

import cgi
import json

from db import *
from gameserver import *

print "content-type: text/plain\n"

form = cgi.FieldStorage()

identifier = str(form.getvalue('identifier'))

server = Server()
server.open()

result = server.delete(identifier)

server.close()

text = '{"error" : "unknown error"}'
if result:
	text = '{"status" : "success"}'
else:
	text = '{"error" : "' + server.error + '"}'

print text

