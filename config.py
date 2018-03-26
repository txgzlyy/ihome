# coding=utf-8
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'yPgEKrTgQ+OlzJOoqCU25w=='
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # MAIL_SERVER = 'smtp.126.com'
    # MAIL_PORT = 465
    # MAIL_USE_SSL = True
    # MAIL_USERNAME = 'ccyznhy'
    # MAIL_PASSWORD = '111qqq'
    # MY_MAIL_SENDER = 'ccy<ccyznhy@126.com>'
    # MY_MAIL_TO = '939064936@qq.com'
    # 创建redis实例用到的参数
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/ihome'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/ihome'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/ihome'


# 方便调用
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}




