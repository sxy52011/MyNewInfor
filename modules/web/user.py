from flask import Blueprint,make_response,session,request,jsonify,render_template,g
from utils.captcha.captcha import captcha
from utils.response_code import RET,error_map
from database import User,Category,News
from werkzeug.security import generate_password_hash,check_password_hash
from apps import db,photos
from utils.common import user_islogin
from utils.contants import PAGECOUNT

user_blue = Blueprint("user_blue",import_name=__name__,template_folder='../../templates')


#显示验证码
@user_blue.route('/get_image',methods=['GET','POST'])
def get_image():
    # name, text , StringIO.value
    # text : 验证码图片对应到文本
    # image_url : 验证码图片IO流 理解为：二进制数据，并没有实际转换成图片呢
    name,text,image_url = captcha.generate_captcha()
    session['img_code'] = text
    response = make_response(image_url)   #生成图片到响应
    # 告诉浏览器，我要返回到是一张图片
    response.headers['Content-Type'] = 'image/jpg'
    return response

#注册
@user_blue.route('/register',methods=['GET','POST'])
def register():
    msg= {}
    mobile = request.form.get('mobile')
    smscode = request.form.get('sms_code')
    password = request.form.get('password')
    if all([mobile,smscode,password]):           # 判断数据是否完整
        if session.get('img_code').lower() != smscode:   # 对比验证码 是否 一致
            msg['errno'] = RET.IMGERROR         # 生成验证码错误到 response给jQuery
            msg['errmsg'] = error_map[RET.IMGERROR]
            return jsonify(msg)
        else:         # 数据完整，验证码正确 将手机号、密码 写入到数据库
            user = User.query.filter(User.mobile == mobile).first()
            if user:
                msg['errno'] = RET.MOBILEEXIST
                msg['errmsg'] = error_map[RET.MOBILEEXIST]
                return jsonify(msg)
            else:
                pass_has = generate_password_hash(password)     # 密码加密处理
                u = User(mobile=mobile,password_has = pass_has )
                db.session.add(u)
                db.session.commit()
                msg['errno'] = RET.OK     # 返回成功
                msg['errmsg'] = error_map[RET.OK]

                session['user_id'] = u.id

                return jsonify(msg)
    else:     # 数据不完整
        msg['errno'] = RET.NODATA
        msg['errmsg'] = error_map[RET.NODATA]
    return jsonify(msg)

#登录
@user_blue.route('/login',methods=['GET','POST'])
def login():
    msg={}
    if request.method == 'POST':       #判断请求类型
        mobile = request.form.get('mobile')      #获取手机号
        password = request.form.get('password')     #获取密码
        if all([mobile,password]):      #数据非空
            u = User.query.filter(User.mobile == mobile).first()      #根据手机号进行查询
            if u:
                if check_password_hash(u.password_has,password):      #判断密码是否正确
                    session['user_id'] = u.id                        #session赋值，表示已经登录
                    msg['errno'] = RET.OK                            #登录成功
                    msg['errmsg'] = error_map[RET.OK]
                else:
                    msg['errno'] = RET.PWDERR                         #登录失败，用户名不存在
                    msg['errmsg'] = error_map[RET.PWDERR]
            else:
                msg['errno'] = RET.MOBILENOTEXIST                     #登录失败，信息不全
                msg['errmsg'] = error_map[RET.MOBILENOTEXIST]
        else:
            msg['errno'] = RET.NODATA                                  #返回结果
            msg['errmsg'] = error_map[RET.NODATA]
    return jsonify(msg)

#退出登录
@user_blue.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('user_id')
    msg = {'errno':'200','errmsg':'退出成功'}
    return jsonify(msg)

#用户信息
@user_blue.route('/user_info',methods=['GET','POST'])
@user_islogin
def user_info():
    user_id = session.get('user_id')
    u = User.query.filter(User.id == user_id).first()
    data = {'user_info': u}
    return render_template('/news/user.html',data = data)

#修改基本资料
@user_blue.route('/base_info',methods=['GET','POST'])
@user_islogin
def base_info():
    if request.method == 'POST':
        signature = request.form.get("signature")
        nick_name = request.form.get("nick_name")
        gender = request.form.get("gender")
        msg={}
        if all([signature,nick_name,gender]):
            user_id = session.get('user_id')
            u = User.query.filter(User.id == user_id).first()
            u.signature = signature
            u.nick_name = nick_name
            u.gender = gender
            db.session.commit()
            msg['code'] = RET.OK
            msg['mes'] = error_map[RET.OK]
        else:
            msg['code'] = RET.NODATA
            msg['mes'] = error_map[RET.NODATA]
        return jsonify(msg)
    user_id = session.get('user_id')
    u = User.query.filter(User.id == user_id).first()
    data = {'user_info': u}
    return render_template('/news/user_base_info.html', data=data)

#上传头像
@user_blue.route('/pic_info',methods=['GET','POST'])
@user_islogin
def pic_info():
    user_id = session.get('user_id')
    u = User.query.filter(User.id == user_id).first()
    if request.method == 'POST':
        image = request.files.get('avatar')          #获取请求中的头像
        if image:
            image_name = photos.save(image)              #将头像保存到 程序目录下
            image_url = '/static/upload/' + image_name          #生成图片保存到地址
            u.avatar_url = image_url                #将上传的图片地址，保存到用户表中
            db.session.commit()
    data = {'user_info': u}
    return render_template('/news/user_pic_info.html',data=data)

#密码修改
@user_blue.route('/pass_info',methods=['GET','POST'])
@user_islogin
def pass_info():
    if request.method == 'POST':
        old_password = request.form.get('old_password')     #旧密码
        new_password = request.form.get('new_password')     #新密码
        new_password2 = request.form.get('new_password2')   #确认密码
        msg={}                 #给Ajax返回的结果
        if all([old_password,new_password,new_password2]):    #判断非空
            user_id = session.get('user_id')
            u = User.query.filter(User.id == user_id).first()       #读取用户信息
            if check_password_hash(u.password_has,old_password):    #验证旧密码是否正确
                if new_password == new_password2:        #两次密码，是否一致
                    if len(new_password) >=6:       #密码长度 不小于6
                        u.password_has = generate_password_hash(new_password)
                        db.session.commit()                #新密码更新到数据库
                        msg['errno'] = RET.OK
                        msg['errmsg'] = error_map[RET.OK]
                    else:
                        msg['errno'] = RET.PWDERR
                        msg['errmsg'] = '密码长度小于6'
                else:
                    msg['errno'] = RET.PWDERR
                    msg['errmsg'] = '两次密码不一致'
            else:
                msg['errno'] = RET.PWDERR
                msg['errmsg'] = error_map[RET.PWDERR]
        else:
            msg['errno'] = RET.NODATA
            msg['errmsg'] = error_map[RET.NODATA]
        return jsonify(msg)
    return render_template('/news/user_pass_info.html')


#新闻发布
@user_blue.route('/news_release',methods=['GET','POST'])
@user_islogin
def news_release():
    if request.method == 'POST':
        msg={}
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        digest = request.form.get('digest')
        image = request.files.get('index_image')
        image_url = ''
        if image:
            image_name = photos.save(image)  # 将头像保存到 程序目录下
            image_url = '/static/upload/' + image_name  # 生成图片保存到地址
        content = request.form.get('content')
        if all([title,category_id,content]):     #数据不为空
            n = News()
            n.user_id = session.get('user_id')      #新闻发布者ID
            n.title = title                         #新闻标题
            n.category_id = category_id             #分类ID
            n.digest = digest                       #摘要
            n.index_image_u = image_url             #新闻图片
            n.content = content                     #新闻内容
            n.status = 1                            #新闻状态
            db.session.add(n)                       #新闻写入数据库
            msg['errno'] = RET.OK
            msg['errmsg'] = error_map[RET.OK]
        else:
            msg['errno'] = RET.NODATA
            msg['errmsg'] = error_map[RET.NODATA]
        return jsonify(msg)

    c = Category.query.all()
    data ={}
    data['categories'] = c
    return render_template('/news/user_news_release.html',data = data)

#新闻列表
@user_blue.route('/news_list',methods=['GET','POST'])
@user_islogin
def news_list():
    user_id = session.get('user_id')     #用户ID
    current_page = request.args.get('p',1,type=int)        #获取当前页，默认为1.来源：分页插件
    msg_count = PAGECOUNT               #每页显示数据量，全局
    data = {}
    #查询自己发布到新闻列表，并根据发布时间倒叙，使用分页方式查询（paginate(current_page,msg_count,False))
    news_list = News.query.filter(News.user_id == user_id).order_by(News.create_time.desc()).paginate(current_page,msg_count,False)
    data['news_list'] = news_list.items         #items 为分页查询结果到 数据内容
    data['current_page'] = news_list.page9       #page 为当前页（分页插件参数）
    data['total_page'] = news_list.pages        #pages 为总页数（分页插件参数）
    return render_template('/news/user_news_list.html',data = data)