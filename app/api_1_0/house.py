# coding=utf-8
import json
import logging
from . import api
from flask import jsonify,request,g
from app.utils.response_code import RET
from app import constants,redis_store
from app.utils.comments import logout_req
from app.utils.img_store import img_store
from app.models import Area,HouseInfo,HousePic,Facility,house_facility
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


@api.route('/user/houses',methods=['GET'])
@logout_req
def get_house():
    '''
     获取房东所有房屋信息
    '''
    user_id = g.user_id
    house_o = HouseInfo.query.filter_by(user_id=user_id).all()
    houses = []
    for house in house_o:
        obj = house.house_bic()
        houses.append(obj)
    return jsonify(errno=RET.OK, errmsg="ok", data={"houses":houses})


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
    if house_info.get("facility"):
        # 查询设施id在house_info["facilities"]列表里面  select * from xxx where id in house_info["facilities"]
        try:
            facilities = Facility.query.filter(Facility.id.in_(house_info["facility"])).all()
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


@api.route('/houses/index',methods=['GET'])
def house_index():
    '''获取房屋订单数目最多的5条数据'''
    # 尝试从redis获取
    try:
        house_redis_data = redis_store.get("IndexHouseData")
    except Exception as e:
        logging.error(e)
        house_redis_data = None
    if house_redis_data:
        logging.info("hit house index info redis")
        resp = '{"errno":"0", "errmsg":"OK", "data":%s}' % house_redis_data
        return resp, 200, {"Content-Type": "application/json", }

    # 从数据库取
    try:
        houses = HouseInfo.query.order_by(HouseInfo.order_count.desc()).limit(constants.IndexHouseNum)  # 降序
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库")

    house_datas = []
    for house in houses:
        house_datas.append(house.house_bic())

    # 存入redis
    house_datas_str = json.dumps(house_datas)
    try:
        redis_store.setex("IndexHouseData", constants.INDEX_HOUSE_DATA_TIME, house_datas_str)
    except Exception as e:
        logging.error(e)

    resp = '{"errno":"0", "errmsg":"OK", "data":%s}' % house_datas_str
    return resp, 200, {"Content-Type": "application/json", }


@api.route('/houses/<int:house_id>',methods=['GET'])
@logout_req
def detail_house(house_id):
    '''
    获取房屋基本信息
    '''
    user_id = g.user_id
    # 尝试从redis获取
    try:
        house_redis_data = redis_store.get('HouseId='+str(house_id))
    except Exception as e:
        logging.error(e)
        house_redis_data = None
    # 直接加载redis中的数据
    if house_redis_data:
        logging.info("hit house_id=%d redis"%house_id)
        resp = '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, house_redis_data)
        return resp, 200, {"Content-Type": "application/json", }

    try:
        house = HouseInfo.query.get(house_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库错误")

    if not house:
        return jsonify(errno=RET.DATAERR, errmsg="房屋不存在")
    # 获取房屋信息
    house_data = house.to_full_dict()

    # 存入redis
    house_data_str = json.dumps(house_data)
    try:
        redis_store.setex("HouseId="+str(house_id), constants.HOUSE_DATA_STR, house_data_str)
    except Exception as e:
        logging.error(e)

    resp = '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}' % (user_id, house_data_str)
    return resp, 200, {"Content-Type" : "application/json",}


@api.route('/houses/<int:house_id>/images',methods=["POST"])
@logout_req
def save_house_img(house_id):
    try:
        house = HouseInfo.query.filter_by(id=house_id).first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    # 判断房屋是否存在
    if not house:
        return jsonify(errno=RET.DATAERR, errmsg="房屋不存在")

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
    house_pic = HousePic(house_id=house_id, img_url=image_name)
    db.session.add(house_pic)

    # 如果房屋主图片未设置 设置主图
    if house.index_image_url == '':
        house.index_image_url = image_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据存储异常")

    url = constants.QINIUIMGURL + image_name
    return jsonify(errno=RET.OK, errmsg="ok", data={"url":url})








