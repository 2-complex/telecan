from flask import Flask
from configuration import Config

app = Flask(__name__, static_url_path = '/static')
app.config.from_object(Config)

import endpoints
