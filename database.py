
from datetime import datetime
from apps import app,db

# app = Flask(__name__)
# app.config.from_object(config.config_dict['config'])
# db = SQLAlchemy(app)

#父继承
class Base(object):
    create_time = db.Column(db.DateTime,default=datetime.now())
    update_time = db.Column(db.DateTime,default=datetime.now())

#管理员表
class Admin(Base,db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20),nullable=False)
    pass_hash = db.Column(db.String(200),nullable=False)

#用户收藏 多对多
table_user_news = db.Table('user_collection',
                           db.Column('id', db.Integer, primary_key=True),
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),  # 用户Id
                           db.Column('news_id', db.Integer, db.ForeignKey('news.id')))  # 新闻Id

#用户表
class User(Base,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nick_name = db.Column(db.String(20),index=True)
    password_has = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.String(11), nullable=False)
    avatar_url = db.Column(db.String(256))
    last_login = db.Column(db.DateTime)
    signature = db.Column(db.String(512))
    gender = db.Column(db.String(10),default='Man',nullable=False)
    news = db.relationship('News',backref='author',lazy='dynamic')
    news_collection = db.relationship('News',secondary=table_user_news
                                     ,backref='users',lazy='dynamic')

    def to_dict(self):
        user_list = {
            'id': self.id,
            'nick_name' :self.nick_name,
            'password_has' : self.password_has,
            'mobile' : self.mobile,
            'avatar_url' : self.avatar_url,
            'last_login' : self.last_login.strftime('%Y-%m-%d %H:%M:%S'),
            'signature' : self.signature,
            'gender' : self.gender
        }
        return user_list

#新闻分类表
class Category(Base,db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    relate_news = db.relationship('News',backref='relate_category',lazy='dynamic')

#新闻表
class News(Base,db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    source = db.Column(db.String(30))
    index_image_u = db.Column(db.String(100))
    digest = db.Column(db.String(255))
    clicks = db.Column(db.Integer)
    content = db.Column(db.Text)
    category_id = db.Column(db.Integer,db.ForeignKey('category.id'),index=True)
    user_id =db.Column(db.Integer,db.ForeignKey('user.id'),index=True)
    status =db.Column(db.Integer)
    reason = db.Column(db.String(100))

    def to_dict(self):
        new_dict = \
            {
                'id': self.id,
                'title': self.title,
                'source': self.source,
                'index_image_url': self.index_image_u,
                'digest': self.digest,
                'clicks': self.clicks,
                'content': self.content,
                'category_id': self.category_id,
                'user_id': self.user_id,
                'status': self.status,
                'reason': self.reason,
                'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        return new_dict

#新闻评论表
class Comment(Base,db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer,db.ForeignKey('news.id'),index=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),index=True)
    content = db.Column(db.String(255))
    def to_dict(self):
        com_list = {
            'id' : self.id,
            'news_id' : self.news_id,
            'user_id' : self.user_id,
            'content' : self.content,
            'create_time' : self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time' : self.update_time.strftime('%Y-%m-%d %H:%M:%S'),
            'user' : User.query.filter(User.id == self.user_id).first().to_dict()
        }
        return com_list



#
# if __name__ == '__main__':
#     db.drop_all()
#     db.create_all()
#     app.run()