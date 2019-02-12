from flask import Flask
from configuration import Config

import endpoints

app = Flask(__name__, static_url_path = '/static')
app.config.from_object(Config)
endpoints.assign_to_app(app)
