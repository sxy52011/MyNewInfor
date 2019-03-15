# -*- encoding: utf-8 -*-


class Config(object):
    """工程配置信息"""
    DEBUT = True
    """SQLAlchemy 配置"""
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@127.0.0.1:3306/mynewlnfor'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True # 数据库内容发送改变之后,自动提交
    SQLALCHEMY_ECHO = True
    SECRET_KEY = '1810'


class ProductionConfig(object):
    """工程配置信息"""
    DEBUT = False
    """SQLAlchemy 配置"""
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@127.0.0.1:3306/mynewlnfor'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True # 数据库内容发送改变之后,自动提交
    SQLALCHEMY_ECHO = True
    SECRET_KEY = '1810'

config_dict = {
    'config': Config,
    'product': ProductionConfig
}
