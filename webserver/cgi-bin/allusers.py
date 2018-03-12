#!/usr/bin/python

import cgi
import json

from db import *
from gameserver import *

print "content-type: text/plain\n"

form = cgi.FieldStorage()

text = ''

server = Server()
server.open()

allusers = server.get_all_users()

userdictlist = []
for u in allusers:
	userdictlist.append(u._value_dict())

server.close()

text = json.dumps(userdictlist)

print text

