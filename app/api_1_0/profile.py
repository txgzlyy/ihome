# coding=utf-8
from . import api
from app import db
from flask import request,jsonify,g,session
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
        #  update 方法 第一次添加 第二次可以修改
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


@api.route('/user/name',methods=['PUT'])
@logout_req
def set_user_name():
    '''修改用户名'''
    user_id = g.user_id
    data = json.loads(request.get_data())
    if not data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    name = data['name']
    # 跟新数据库中的用户名
    try:
        UserInfo.query.filter_by(id=user_id).update({"user_name":name})
        db.session.commit()
        session["name"] = name
    except Exception as e:
        logging.error(e)
        db.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据错误")
    return jsonify(errno=RET.OK, errmsg="ok")


@api.route('/user/auth',methods=['POST','GET'])
@logout_req
def rel_auth():
    '''用户实名认证'''
    user_id = g.user_id
    user = UserInfo.query.filter_by(id=user_id)
    if request.method == 'POST':
        data = json.loads(request.get_data())
        real_name = data.get('real_name')
        id_card = data.get('id_card')
        # 保存数据库
        try:
            user.update({'real_name':real_name,"id_card":id_card})
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.rollback()
            return jsonify(errno=RET.DBERR,errmsg='数据错误')
    return jsonify(errno=RET.OK,errmsg='ok',data=user.first().get_dict())







