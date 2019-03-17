from flask import Blueprint,session,render_template,redirect,url_for,request,flash,jsonify
import apps
from utils.contants import PAGECOUNT
from utils.response_code import RET,error_map
from werkzeug.security import generate_password_hash,check_password_hash
from database import Admin,Category,User,News
from datetime import datetime

admin_blue = Blueprint("admin_blue",import_name=__name__,template_folder='../../templates')

@admin_blue.route('/')
def index():
    user_id = session.get('a_user_id')
    if user_id:
        return render_template('/admin/index.html')
    else:
        return redirect(url_for('admin_blue.login'))


@admin_blue.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if not all([user,pwd]):
            flash('信息不全')
        else:
            a = Admin.query.filter(Admin.name==user).first()
            if not a :
                flash('用户名不存在')
            else:
                if check_password_hash(a.pass_hash,pwd):
                    session['a_user_id'] = a.id
                    return redirect(url_for('admin_blue.index'))
                else:
                    flash('密码错误')
    return render_template('/admin/login.html')


@admin_blue.route('/add')
def add():
    pwd =generate_password_hash('123')
    a = Admin(name = 'ljj',pass_hash = pwd)
    apps.db.session.add(a)
    return 'okkkkkk'

#新闻分类
@admin_blue.route('/newscate',methods=['GET','POST'])
def news_cate():
    if request.method == 'POST':
        msg = {}   #Ajax调用时的返回结果
        name = request.form.get('name')
        id = request.form.get('id')
        if name:
            cate = Category.query.filter(Category.name == name).first()   #判断是否有同名
            if cate:     #同名返回失败
                msg['code'] = RET.DATAEXIST
                msg['message'] = error_map[RET.DATAEXIST]
            else:
                if not id: #通过ID来判断，操作类型（新增，修改）
                    c = Category(name=name)
                    apps.db.session.add(c)
                else:
                    #更新新闻分类
                    Category.query.filter(Category.id == id).update({'name': name})
                msg['code'] = RET.OK
                msg['message'] = error_map[RET.OK]
        else:
            msg['code'] = RET.NODATA
            msg['message'] = error_map[RET.NODATA]
        return jsonify(msg)
    cate = Category.query.all()
    return render_template('admin/news_type.html',category=cate)

#删除分类
@admin_blue.route('/deletecate',methods=['GET','POST'])
def delete_cate():
    msg={}
    id = request.form.get('id')
    try:
        Category.query.filter(Category.id == id).delete()
    except Exception as e:
        # print(e)
        msg['code'] = RET.TRYAGAIN
        msg['message'] = error_map[RET.TRYAGAIN]
        return jsonify(msg)
    msg['code'] = RET.OK
    msg['message'] = error_map[RET.OK]
    return jsonify(msg)

#用户列表展示
@admin_blue.route('/user_list',methods=['GET','POST'])
def user_list():
    current_page = int(request.args.get('p',1))
    page_count = PAGECOUNT
    data = {}
    users = User.query.paginate(current_page,page_count,False)
    data['user_list'] = users.items      #
    data['current_page'] = users.page   #获取当前页
    data['total_page'] = users.pages     #获取总页数
    return render_template('/admin/user_list.html',data = data)

#用户统计
@admin_blue.route('/user_count',methods=['GET','POST'])
def user_count():
    data={}
    #总用户数量
    total = User.query.count()
    data['total'] = total
    #当月活跃用户数量
    month_day =datetime.strftime(datetime.now(),'%Y-%m-01')
    month_count = User.query.filter(User.last_login >= month_day).count()
    data['month_total'] = month_count
    #当天活跃用户数量
    day = datetime.strftime(datetime.now(),'%Y-%m-%d')
    day_count =User.query.filter(User.last_login >= day).count()
    data['day_total'] = day_count

    return render_template('/admin/user_count.html',data = data)

#新闻审核
@admin_blue.route('/newsreview',methods=['GET','POST'])
def news_review():
    data ={}
    current_page = int(request.args.get('page',1))  # 当前页，通过分页按钮传递，默认打开第一页
    key_word = request.args.get('keyword','')  # 搜索关键字，来源：输入框（通过点击搜索 或 分页按钮传递）
    page_count = PAGECOUNT
    if key_word:
        news = News.query.filter(News.title.like('%'+ key_word +'%')).paginate(current_page,page_count,False)
    else:
        news = News.query.paginate(current_page,page_count,False)
    data['news_list'] = news.items
    data['current_page'] = news.page
    data['total_page'] =news.pages
    return render_template('/admin/news_review.html',data = data)

@admin_blue.route('news_review_detail',methods=['GET','POST'])
def news_review_detail():
    if request.method == 'POST':   #post方式为Ajax调用
        msg = {}
        id = request.form.get('id')    #获取新闻ID
        action = request.form.get('action')    # radio 单选按钮，2-通过，3-拒绝
        if action == '3':     #拒绝时，需要获取‘理由’
            reason = request.form.get('reason')     #拒绝 理由
            News.query.filter(News.id == id).update({'status':action,'reason':reason})    #数据库更新
        else:
            News.query.filter(News.id == id).update({'status':action})    #通过审核，数据库更新
        msg['code'] = RET.OK     #返回结果给Ajax(jQuery)
        msg['message'] = error_map[RET.OK]
        return jsonify(msg)
    else:
        data={}
        id = request.args.get('id')    #页面默认展示（get方式）
        news = News.query.filter(News.id == id).first()    #根据id 查询一条新闻
        data['news'] = news   #模板参数
        return render_template('/admin/news_review_detail.html',data = data)