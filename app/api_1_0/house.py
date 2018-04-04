# coding=utf-8
import json
import logging
from . import api
from flask import jsonify
from app.utils.response_code import RET
from app import constants,redis_store
from app.models import Area


@api.route('/areas')
def get_areas():
    '''获取地区
        使用redis缓存数据库
        访问redis 如果redis中没有就访问mysql，再把数据存入redis
    '''
    areas = []
    # 查询redis
    try:
        if redis_store.get('areas'):
            # 转成列表
            areas = json.loads(redis_store.get('areas'))
            return jsonify(errno=RET.OK, errmsg='ok', data=areas)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据错误')

    # 查询mysql
    try:
        areas_list = Area.query.all()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据错误')

    for area in areas_list:
        areas.append(area.to_dict())
    # 转成字符串存入 redis
    try:
        redis_store.setex("areas", constants.AreasTime, json.dumps(areas))
    except Exception as e:
        logging.error(e)
    return jsonify(errno=RET.OK, errmsg='ok', data=areas)
