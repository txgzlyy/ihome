# coding=utf-8
from flask import Flask
from config import config
from utils.comments import RegexUrl
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect


db = SQLAlchemy()
csrf = CSRFProtect()

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

