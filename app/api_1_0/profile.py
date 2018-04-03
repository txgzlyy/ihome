# coding=utf-8
from . import api
from app import db
from flask import request,jsonify,g
from app.utils.img_store import img_store
from app.utils.comments import logout_req
from app.utils.response_code import RET
from app import constants
from app.models import UserInfo
import logging
import json


@api.route('/user/avatar',methods=['POST'])
@logout_req
def get_avatar():
    # 获取头像图片数据  上传文件的数据
    data = request.files.get('avatar')
    if not data:
        return jsonify(errno=RET.PARAMERR, errmsg="未传头像")

    try:
        # 读取上传的文件内容，并调用自己封装的方法上传到七牛
        avatar_img_name = img_store(data.read())
    except Exception as e:
        return jsonify(errno=RET.THIRDERR,errmsg="上传失败")

    # 存入数据库
    user_id = g.user_id
    try:
        UserInfo.query.filter_by(id=user_id).update({"author_url": avatar_img_name})
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库错误")

    # 通用域名 + 图片名字
    avatar_url = constants.QINIUIMGURL + avatar_img_name
    return jsonify(errno=RET.OK,errmsg="头像上传成功",data={"avatar_url":avatar_url})


@api.route('/user',methods=['GET'])
@logout_req
def get_user():
    """获取个人信息"""
    user_id = g.user_id
    try:
        user = UserInfo.query.get(user_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if user is None:
        return jsonify(errno=RET.DATAERR, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="ok",data=user.get_dict())


@api.route('user/name',methods=['PUT'])
@logout_req
def set_user_name():
    '''修改用户名'''
    name = json.loads(request.get_data('name'))
    print(name)
    return jsonify(errno=RET.OK, errmsg="ok")