# coding=utf-8

from flask import Blueprint,make_response,current_app
import logging

html = Blueprint('html',__name__)


@html.route('/<re(".*"):file_name>')
def html_url(file_name):
    if not file_name:
        file_name = 'index.html'

    if file_name != "favicon.ico":
        file_name = "html/"+file_name

    response = make_response(current_app.send_static_file(file_name))

    return response


@html.route('/test')
def test():
    logging.debug('this is debug')
    return 'ok'