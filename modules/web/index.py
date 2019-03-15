from flask import Blueprint

index_blue = Blueprint('index_blue',import_name=__name__,template_folder='../../templates')

@index_blue.route('/')
def index():
    return 'ok'