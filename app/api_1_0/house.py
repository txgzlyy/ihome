# coding=utf-8
import json
import logging
from . import api
from flask import jsonify,request,g
from app.utils.response_code import RET
from app import constants,redis_store
from app.utils.comments import logout_req
from app.utils.img_store import img_store
from app.models import Area,HouseInfo,HousePic,Facility,Order
from app import db
from datetime import datetime


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


@api.route('/houses/',methods=['GET'])
def serch_house():
    '''
    不需要登录
    ?aid=&sd=2018-04-11&ed=2018-04-20&sk=new&p=1
    params = {
        aid:areaId,  地区id
        sd:startDate,  开始入住时间
        ed:endDate,    结束时间
        sk:sortKey,    排序关键字
        p:next_page    下一页
    }
    '''
    aid = request.args.get("aid",'')
    start_date = request.args.get("sd",'')
    end_date = request.args.get("ed",'')
    order_key = request.args.get("sk",'new') # 默认是new
    page_num = request.args.get('p','1')

    # 查询条件
    params = []
    try:
        # 找出搜寻条件和订单时间冲突的所有房屋id
        if start_date and end_date:
            # 开始时间和结束时间都有
            # 字符串转成时间格式   2018-04-11 00:00:00
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            house_ids = [house_id for house_id in Order.query.filter(Order.begin_date < end_date and Order.end_date > start_date).all()]
        elif start_date:
            # 只有开始时间
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            house_ids = [house_id for house_id in Order.query.filter(Order.end_date > start_date).all()]
        elif end_date:
            # 只有结束时间
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            house_ids = [house_id for house_id in Order.query.filter(Order.begin_date < end_date).all()]
        else:
            # 全部 满足没有冲突的订单
            house_ids = ['']
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库错误')

    # 区域
    if aid:
        params.append(HouseInfo.area_id == aid)

    if page_num:
        page_num = int(page_num)
    else:
        page_num = 1

    # 参数检验完毕  尝试从redis获取数据
    hash_key = "HOUSES_%s_%s_%s_%s" % (aid, start_date, end_date, order_key)
    try:
        redis_datas = redis_store.hget(hash_key, str(page_num))
    except Exception as e:
        logging.error(e)
        redis_datas = None

    if redis_datas:
        logging.info("hit house list redis")
        return redis_datas, 200 , {"Content-Type" : "application/json",}


    # 把冲突的排除并添加到查询条件 params
    params.append(HouseInfo.id.notin_(house_ids))

    # 判断关键字
    if order_key == 'booking':
        # 入住最多
        # 满足条件的房屋
        houses = HouseInfo.query.filter(*params).order_by(HouseInfo.order_count.desc())

    elif order_key == 'price-inc':
        # 价格 低-高
        houses = HouseInfo.query.filter(*params).order_by(HouseInfo.price.asc())
    elif order_key == 'price-des':
        # 价格 高-低
        houses = HouseInfo.query.filter(*params).order_by(HouseInfo.price.desc())
    else:
        # 默认最新上线
        houses = HouseInfo.query.filter(*params).order_by(HouseInfo.create_time.desc())

    # 处理分页
    # 常见分页对象 参数 page 当前页  per_page 每页几条数据   error_out=False 当page和pre_page为None是不报错
    page_obj = houses.paginate(page=page_num,per_page=constants.PAGE_DATAS,error_out=False)

    # 获取总页数
    total_page = page_obj.pages
    # 获取每一业的数据
    page_datas = page_obj.items
    try:
        house_data = [house.house_bic() for house in page_datas]
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库错误')

    # 使用redis 缓存数据  使用 hash  hset key 属性 值
    hash_data = dict(errno=RET.OK, errmsg='OK',data={"total_page":total_page,"houses":house_data})
    # 转字符串
    hash_data_str = json.dumps(hash_data)
    # 当前页 小于等于总页数
    if page_num <= total_page:
        try:
            # 开启redis 事物 保证整个 redis 保存都执行
            # 创建 管道
            piple = redis_store.pipeline()
            # 开启管道
            piple.multi()
            # hash类型保存数据
            redis_store.hset(hash_key, str(page_num), hash_data_str)
            # 有效时间
            redis_store.expire(hash_key, constants.PAGE_REDIS_TIME)
            # 执行管道
            piple.execute()
        except Exception as e:
            logging.error(e)

    return hash_data_str, 200, {"Content-Type" : "application/json",}







