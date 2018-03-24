# coding=utf-8
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CsrfProtect


db = SQLAlchemy()
csrf = CsrfProtect()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    csrf.init_app(app)

    from api_1_0 import api as api_buleprint
    app.register_blueprint(api_buleprint,url_prefix='/api/v1.0')

    return app

