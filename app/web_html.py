# coding=utf-8

from flask import Blueprint,make_response,current_app
import logging
from flask_wtf import csrf

html = Blueprint('html',__name__)


@html.route('/<re(".*"):file_name>')
def html_url(file_name):
    if not file_name:
        file_name = 'index.html'

    if file_name != "favicon.ico":
        file_name = "html/"+file_name

    response = make_response(current_app.send_static_file(file_name))
    # 给cookie 设置 csrftoken   csrf.generate_csrf() 生成token
    csrf_token = csrf.generate_csrf()
    response.set_cookie("csrf_token",csrf_token)

    return response


@html.route('/test')
def test():
    logging.debug('this is debug')
    return 'ok'