from pickle import TRUE
from flask import Flask
from config import Config
# from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
app.config["DEBUG"] = TRUE
# bootstrap = Bootstrap(app)

from app import routes
