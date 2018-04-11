# coding=utf-8
import logging
from datetime import datetime
from flask import request, jsonify, g
from . import api
from app import db
from app.utils.comments import logout_req
from app.utils.response_code import RET
from app.models import Order, HouseInfo

@api.route('/orders',methods=['POST'])
@logout_req
def set_order():
    '''
    创建订单
    '''
    user_id = g.user_id
    data = request.get_json()
    house_id = data.get('house_id')
    start_date = data.get('start_date')
    end_date = data.get("end_date")
    if not all([house_id,start_date,end_date]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        assert end_date >= start_date
    else:
        return jsonify(errno=RET.DATAERR, errmsg="选择起止日期")

    # 检验该房屋是不是存在
    try:
        house = HouseInfo.query.get(house_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="房屋信息为查到")

    # 检验是不是房东
    if user_id == house.user_id:
        return jsonify(errno=RET.DATAERR, errmsg="不能预定自己发布的房源")

    try:
        # 检查该房屋是否已经被预定 多人同事预定冲突 根据入住时间和结束时间条件查询order表
        count = Order.query.filter(Order.house_id==house_id,Order.begin_date<=end_date,Order.end_date>=start_date).count()
    except Exception as e:
        logging.error(e)
        count = 0

    if count > 0:
        return jsonify(errno=RET.DATAERR, errmsg="该房屋已经被预定")


    # 存入数据库
    order = Order(
        user_id=user_id,
        house_id=house_id,
        begin_date=start_date,
        end_date=end_date
    )
    try:
        order.house_price = house.price/100
        # <type 'datetime.timedelta'>  类型 可以转成 天，时，分...
        order.days = (end_date - start_date).days + 1
        order.amount = order.house_price * order.days  # 总价
        db.session.add(order)
    except Exception as e:
        logging.error(e)
        db.rollback()
        return jsonify(errno=RET.DBERR,errmsg="数据库错误")

    db.session.commit()

    return jsonify(errno=RET.OK, errmsg="生产订单成功")