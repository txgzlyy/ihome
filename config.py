# coding=utf-8
import os
import redis

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

    # flask_session 和redis的关联和设置参数
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True  # 是否为session_id加密 True: 是
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)  # 保存session的redis
    PERMANENT_SESSION_LIFETIME = 86400  # session 数据的有效期 （秒）


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




