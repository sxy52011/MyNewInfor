from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from  flask_wtf import CSRFProtect
import config

app = Flask(__name__)
app.config.from_object(config.config_dict['config'])


db = SQLAlchemy(app)
