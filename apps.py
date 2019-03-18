from flask import Flask
from  config import log_file
from flask_sqlalchemy import SQLAlchemy
from  flask_wtf import CSRFProtect
import config

config_obj =config.config_dict['config']
app = Flask(__name__)
app.config.from_object(config_obj)

db = SQLAlchemy(app)
#日志方法调用
log_file(config_obj.LEVEL)