from flask import Blueprint,make_response,session,request,jsonify
from utils.captcha.captcha import captcha
from utils.response_code import RET,error_map
from database import User
from werkzeug.security import generate_password_hash,check_password_hash
from apps import db


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
@user_blue.route('/logout')
def logout():
    session.pop('user_id')
    msg = {'errno':'200','errmsg':'退出成功'}
    return jsonify(msg)