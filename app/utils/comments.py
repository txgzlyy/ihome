# coding=utf-8

from werkzeug.routing import BaseConverter
from flask import session,jsonify,g
from .response_code import RET
import functools

class RegexUrl(BaseConverter):
    def __init__(self,map_url,*args):
        super(RegexUrl, self).__init__(map_url)
        self.regex = args[0]


# 判断登录状态

def logout_req(func):
    """要求用户登录的验证装饰器"""
    @functools.wraps(func)
    def inner(*args, **kwargs):
        '''进行登陆与否的判断'''
        user_id = session.get('user_id')
        if not user_id:
            return jsonify(errno=RET.SESSIONERR,errmsg="你没有登陆")
        else:
            # 表示用户已登录，将可能用到的user_id用户编号保存到g中，供视图函数使用
            g.user_id = user_id
            return func(*args, **kwargs)

    return inner
