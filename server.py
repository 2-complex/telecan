from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from configuration import Config

app = Flask(__name__, static_url_path = '/static')

app.config.from_object(Config)

db = SQLAlchemy(app)

import endpoints

