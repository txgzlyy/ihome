# coding=utf-8
from app import db
from . import api
from flask import request,jsonify,session
from app.utils.response_code import RET
from app import redis_store
from ..models import UserInfo
import json
import logging


@api.route('/users/',methods=['POST'])
def register_api():
    '''用户注册'''
    # 接收 {"mobile": mobile,"password": passwd,"sms_code": phoneCode}
    data = json.loads(request.get_data())   # 字典类型
    if data == None:
        return jsonify({"errcode":RET.DATAERR,"errmsg":"数据获取失败"})
    mobile = data.get('mobile')
    password = data.get('password')
    sms_code = data.get('sms_code')

    if not all([mobile, password, sms_code]):
        return jsonify({"errcode": RET.DATAERR, "errmsg": "参数错误"})

    # 检验 短信验证码
    try:
        redis_sms_code = redis_store.get('SMSCode_'+mobile)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据异常")

    # 验证码过期
    if redis_sms_code=='':
        return jsonify(errno=RET.DBERR, errmsg="短信验证码已经失效")

    # 在redis删除短信验证码
    try:
        redis_store.delete('SMSCode_'+mobile)
    except Exception as e:
        logging.error(e)

    if redis_sms_code != sms_code:
        return jsonify(errno=RET.DBERR, errmsg="短信验证码输入不正确")

    #手机号和密码存入数据库
    try:
        user = UserInfo(user_name=mobile, user_mobile=mobile, password=password)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DATAERR, errmsg="手机号已存在")

    # 保存登陆信息
    # print(user.id)
    session['user_id'] = user.id
    session['name'] = mobile
    session['mobile'] = mobile

    return jsonify(errno=RET.OK, errmsg="保存成功")


@api.route('/sessions/',methods=['POST'])
def login_api():
    '''用户登陆'''
    data = json.loads(request.get_data())
    if data == None:
        return jsonify({"errcode":RET.DATAERR,"errmsg":"数据获取失败"})
    mobile = data.get('mobile')
    password = data.get('password')

    if not all([mobile, password]):
        return jsonify({"errcode": RET.DATAERR, "errmsg": "参数错误"})

    # 检验用户名密码
    try:
        user = UserInfo.query.filter_by(user_mobile=mobile).first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='查询数据异常,该手机号不存在')

    if not user.check_password(password):      #  user.check_password(password)  密码检验函数 通过返回真
        return jsonify(errno=RET.DATAERR, errmsg='密码错误！')

    # 用户验证成功，保存用户的session数据
    session["user_id"] = user.id
    session["name"] = user.user_name
    session["mobile"] = user.user_mobile

    return jsonify(errno=RET.OK, errmsg="登陆",data={"user_id":user.id})