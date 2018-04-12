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
        count = Order.query.filter(Order.house_id==house_id, Order.begin_date<=end_date,Order.end_date>=start_date).count()
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


@api.route('/user/orders/',methods=['GET'])
@logout_req
def get_orders():
    '''
    获取订单信息  房客得到自己下单的房屋信息   房东获取自己有订单的房屋信息
    '''
    user_id = g.user_id
    role = request.args.get("role", 'custom')   # 默认的角色是租客
    if role not in("custom", "landlord"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        # 该登陆用户的所有房屋
        house = HouseInfo.query.filter(HouseInfo.user_id == user_id)
        house_ids = [house.id for house in house]
        if role == 'custom':
            # 该登录用户的所有订单   租客的订单信息  订单表中的user_id 等于自己的id
            orders = Order.query.filter(Order.user_id == user_id).order_by(Order.create_time.desc())
        else:
            # 自己房屋中有被下订单的房屋  房东身份   订单表中的house_id 等于自己房屋的id
            orders = Order.query.filter(Order.house_id.in_(house_ids)).order_by(Order.create_time.desc())

        if orders:
            orders_data = [order.get_dict() for order in orders]
        else:
            orders_data = []
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据库错误")

    return jsonify(errno=RET.OK, errmsg="OK", data={"orders":orders_data})


@api.route('/orders/<int:order_id>/status',methods=['PUT'])
@logout_req
def change_order_status(order_id):
    '''接单，拒单 处理'''
    user_id = g.user_id
    data = request.get_json()
    if not data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    action = data.get("action")

    if action not in("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不正确")

    # 查询该订单是否存在 并且处于带接单状态
    try:
        order = Order.query.filter(Order.id==order_id, Order.status=="WAIT_ACCEPT").first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR , errmsg="订单不存在")

    # 一个订单对应一个房屋  #house = HouseInfo.query.filter_by(id=order.house_id).first()
    house = order.ih_houseinfos   # 通过关联直接获取对应房屋

    # 检验是不是该订单房屋的房东
    if order.house_id != house.id:
        return jsonify(errno=RET.DATAERR, errmsg="你不是房东无权修改")

    if action == "accept":
        '''接单 改变订单状态'''
        order.status = "WAIT_PAYMENT"  # 待支付   从带接单状态改为待支付
    else:
        ''' 拒单'''
        order.status = "REJECTED" # 已经拒单
        # 拒单原因
        reason = data.get("reason", '')
        if not reason:
            return jsonify(errno=RET.DATAERR, errmsg="填写原因")
        order.comment = reason

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据存储失败")

    return jsonify(errno=RET.OK, errmsg="OK")















