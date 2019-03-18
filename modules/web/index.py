from flask import Blueprint,render_template,session
from database import  User,Category,News

index_blue = Blueprint('index_blue',import_name=__name__,template_folder='../../templates')

@index_blue.route('/')
def index():
    data ={}
    #判断用户是否登录
    user_id = session.get('user_id')
    #取出用户信息
    if user_id:
        data['user_info'] = User.query.filter(User.id == user_id).first()   #将用户信息 传递到模板 参数中
    #取出点击排行的前10条
    data['click_news_list'] = News.query.filter(News.status == 2).order_by(News.clicks.desc()).limit(10)
    #取出新闻分类  Category，每个分类下边，需要包含 所属他的所有新闻列表
    data['categoies'] = Category.query.all()
    return render_template('/news/index.html',data = data)

