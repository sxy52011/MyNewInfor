from flask import Flask
from  config import log_file
from flask_sqlalchemy import SQLAlchemy
from  flask_wtf import CSRFProtect
import config
from flask_uploads import UploadSet, IMAGES, configure_uploads
import sys
import os

config_obj =config.config_dict['config']
app = Flask(__name__)
app.config.from_object(config_obj)

db = SQLAlchemy(app)
#日志方法调用
log_file(config_obj.LEVEL)

#图片上传配置
fn = getattr(sys.modules['__main__'], '__file__')
root_path = os.path.abspath(os.path.dirname(fn)) + "/static/upload"

app.config['UPLOADED_PHOTO_DEST'] = root_path
app.config['UPLOADED_PHOTO_ALLOW'] = IMAGES
photos = UploadSet('PHOTO')
configure_uploads(app, photos)