# coding=utf-8
import json
import logging
from . import api
from flask import jsonify,request,g
from app.utils.response_code import RET
from app import constants,redis_store
from app.utils.comments import logout_req
from app.models import Area, HouseInfo


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



@api.route('/houses',methods=['POST'])
@logout_req
def save_house():
    user_id = g.user_id
    data = request.get_data()
    if not data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    house_info = json.loads(data)

    print(house_info)
    # 保存数据库
    house = HouseInfo.query.filter_by(user_id=user_id)
    house.update({
        "title": house_info["title"],
        "price": house_info["price"],
        "address": house_info["address"],
        "room_count": house_info["room_count"],
        "acreage": house_info["acreage"],
        "unit": house_info["unit"],
        "beds": house_info["beds"],
        "deposit": house_info["deposit"],
        "min_days": house_info["min_days"],
        "max_days": house_info["max_days"]
        # "facilities" : house_info['facility'],
        # "area_id" : house_info["area_id"]
    })
    return jsonify(errno=RET.OK, errmsg="ok",data=house.first().to_dict())