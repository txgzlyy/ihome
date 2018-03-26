# coding=utf-8
import redis
from flask import Flask
from config import config,Config
from utils.comments import RegexUrl
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
# 日志
import logging
# 日志 控制器中的文件控制器
from logging.handlers import RotatingFileHandler

# 设置日志的记录等级  DEBUG,INFO,WARNING,ERROR,NONE
logging.basicConfig(level=logging.DEBUG)
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小 10M、保存的日志文件个数上限
file_log_handler = RotatingFileHandler('logs/log',maxBytes=1024*1024*10,backupCount=10)

# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formater = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formater)

# 为全局的日志工具对象（flask app使用的）添加日后记录器
logging.getLogger().addHandler(file_log_handler)


db = SQLAlchemy()
csrf = CSRFProtect()

# 创建redis对象
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # 正则
    app.url_map.converters['re'] = RegexUrl

    db.init_app(app)
    csrf.init_app(app)

    from api_1_0 import api as api_buleprint
    app.register_blueprint(api_buleprint,url_prefix='/api/v1.0')

    from web_html import html as html_blueprint
    app.register_blueprint(html_blueprint)

    return app

