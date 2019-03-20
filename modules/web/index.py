from flask import Blueprint,render_template,session,request,jsonify
from database import  User,Category,News,Comment
from utils.response_code import RET
from sqlalchemy import and_,or_
from utils.common import user_islogin
from apps import db

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

#首页新闻模板
@index_blue.route('/newslist',methods=['GET','POST'])
def news_list():
    cur_page = request.args.get('page',type=int)
    currentCid = request.args.get('cid')
    per_page = request.args.get('per_page',type=int)
    newsList = News.query.filter(and_(News.category_id == currentCid,News.status == 2 )).paginate(cur_page,per_page,False)

    list = []
    for new in newsList.items:
        list.append(new.to_dict())

    data={}
    data['errno'] = RET.OK
    data['newsList'] = list
    data['totalPage'] = newsList.pages
    return jsonify(data)

@index_blue.route('/news/<int:id>')
def news(id):
    data={}        # 模板参数
    user_id = session.get('user_id')             # 从session中取出，用户ID
    if user_id:
        data['user_info'] = User.query.filter(User.id == user_id).first()         # 将用户信息赋值到 模板的参数中
    data['news'] = News.query.filter(News.id == id).first()           # 将新闻详情传递到模板
    return render_template('/news/detail.html',data = data)

#新闻评论
@index_blue.route('/news_comment',methods=['GET','POST'])
@user_islogin
def news_comment():
    news_id = request.form.get('news_id')             #新闻ID
    news_comment = request.form.get('comment')        #用户输入的评论到具体内容
    user_id = session.get('user_id')                  #用户ID
    c = Comment(news_id = news_id ,user_id = user_id,content=news_comment)         #生成一条评论表对应的数据
    db.session.add(c)            #将评论写入到数据库
    db.session.commit()          #提交

    msg={}
    msg['code'] = '200'
    msg['data'] = c.to_dict()
    return jsonify(msg)