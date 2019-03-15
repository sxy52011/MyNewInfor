from flask import Flask
from modules.web.index import index_blue
from modules.web.user import user_blue
from modules.admin.admin import admin_blue
from flask_sqlalchemy import SQLAlchemy
from  flask_wtf import CSRFProtect
import config

app = Flask(__name__)
app.config.from_object(config.config_dict['config'])
app.register_blueprint(index_blue,url_prefix='/')
app.register_blueprint(user_blue,url_prefix='/user')
app.register_blueprint(admin_blue,url_prefix='/admin')

db = SQLAlchemy(app)
CSRFProtect(app)