# coding=utf-8
import time,logging
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
    else:
        return jsonify(errno=RET.DATAERR, errmsg="选择起止日期")

    # 存入数据库
    order = Order(
        user_id=user_id,
        house_id=house_id,
        begin_date=start_date,
        end_date=end_date
    )
    try:
        order.house_price = HouseInfo.query.get(house_id).price/100
        order.days = 1  # (time.mktime(end_date) - time.mktime(start_date))/(1000*3600*24)   # 转成时间戳 （毫秒）
        order.amount = order.house_price * order.days  # 总价
        db.session.add(order)
    except Exception as e:
        logging.error(e)
        db.rollback()
        return jsonify(errno=RET.DBERR,errmsg="数据库错误")

    db.session.commit()

    return  jsonify(errno=RET.OK, errmsg="生产订单成功")