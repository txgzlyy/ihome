# coding=utf-8
import json
import logging
from . import api
from flask import jsonify,request,g
from app.utils.response_code import RET
from app import constants,redis_store
from app.utils.comments import logout_req
from app.utils.img_store import img_store
from app.models import Area, HouseInfo,house_facility,Facility
from app import db


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


@api.route('/houses',methods=['GET'])
@logout_req
def get_house():
    '''
     获取房屋信息
    '''
    user_id = g.user_id
    house_o = HouseInfo.query.filter_by(user_id=user_id).first()

    return jsonify(errno=RET.OK, errmsg="ok", data=house_o.to_dict())


@api.route('/houses',methods=['POST'])
@logout_req
def save_house():
    """
    房东发布房源信息
    前端发送过来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
    }
    """
    user_id = g.user_id
    data = request.get_data()
    #data = request.get_json()   # 直接获取json数据
    if not data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    house_info = json.loads(data)
    #house_info = data

    user_id = user_id,
    title = house_info.get("title")
    price = house_info.get("price")
    address = house_info.get("address")
    room_count = house_info.get("room_count")
    acreage = house_info.get("acreage")
    unit = house_info.get("unit")
    capacity = house_info.get("capacity")
    beds = house_info.get("beds")
    deposit = house_info.get("deposit")
    min_days = house_info.get("min_days")
    max_days = house_info.get("max_days")
    area_id = house_info.get("area_id")

    # 校验传入数据
    if not all((title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days)):
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")

    # 前端传过来的单价和押金是以元为单位，转换为分
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 如果该数据以存在
    house_o = HouseInfo.query.filter_by(user_id=user_id)
    if house_o.first():
        #更新操作
        house_o.update({
            'user_id': user_id,
            'title': title,
            'price': price,
            'address': address,
            'room_count': room_count,
            'acreage': acreage,
            'unit': unit,
            'beds': beds,
            'deposit': deposit,
            'min_days': min_days,
            'max_days': max_days,
            'area_id': area_id
        })
        if house_info.get("facilities"):
            # 查询设施id在house_info["facilities"]列表里面  select * from xxx where id in house_info["facilities"]
            try:
                facilities = Facility.query.filter(Facility.id.in_(house_info["facilities"])).all()
                house_o.update({"facilities":facilities})
            except Exception as e:
                logging.error(e)
                return jsonify(errno=RET.DBERR, errmsg='数据库错误')
        # 保存数据库
        try:
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.rollback()
            return jsonify(errno=RET.DBERR, errmsg='数据错误')
        return jsonify(errno=RET.OK, errmsg="ok", data={"house_id":house_o.first().id})

    #  数据库中不存在 新添加
    # 保存房屋基本信息数据到数据库
    house = HouseInfo(
        user_id=user_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days,
        area_id=area_id
    )
    db.session.add(house)
    if house_info.get("facilities"):
        # 查询设施id在house_info["facilities"]列表里面  select * from xxx where id in house_info["facilities"]
        try:
            facilities = Facility.query.filter(Facility.id.in_(house_info["facilities"])).all()
            house.facilities = facilities
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库错误')
    # 保存数据库
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据错误')
    return jsonify(errno=RET.OK, errmsg="ok",data={"house_id": house.id})


@api.route('/houses/<int:house_id>/images',methods=["POST"])
@logout_req
def save_house_img(house_id):
    # request.files.get("house_image") 是一个文件类   ready() 党法读取数据
    img_data = request.files.get("house_image").read()
    if not all([house_id,img_data]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 读取上传的文件内容，并调用自己封装的方法上传到七牛
    try:
        image_name = img_store(img_data)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传失败")

    # 图片名存入数据库
    try:
        HouseInfo.query.filter_by(id=house_id).update({"index_image_url":image_name})
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据存储异常")

    url = constants.QINIUIMGURL + image_name
    return jsonify(errno=RET.OK, errmsg="ok", data={"url":url})