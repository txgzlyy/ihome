# coding=utf-8
import logging, os
from . import api
from app.utils.comments import logout_req
from alipay import AliPay
from flask import g, jsonify
from app.models import Order
from app import db
from app.utils.response_code import RET
from app import constants


@api.route('/orders/<int:order_id>/payment',methods=["POST"])
@logout_req
def alipay_pay(order_id):
    '''对接支付宝支付功能'''
    user_id = g.user_id
    # 检验订单存在，并且处于代支付状态
    try:
        order = Order.query.filter(Order.user_id == user_id, Order.id == order_id, Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库错误")
    if order is None:
        return jsonify(errno=RET.DATAERR, errmsg="订单不存在")

    alipay_ihome = AliPay(
        appid="2016091500518471",  # 支付宝appid
        app_notify_url=None,  # 默认回调url
        # 路径拼接  os.path.dirname(__file__)  当前文件的路径
        app_private_key_path=os.path.join(os.path.dirname(__file__),"pay_kes/app_private_key.pem"),
        alipay_public_key_path=os.path.join(os.path.dirname(__file__),"pay_kes/ailpay_publick_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False  开发环境开启
    )

    # 手机网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string    沙箱环境  https://openapi.alipaydev.com/gateway.do
    order_string = alipay_ihome.api_alipay_trade_wap_pay(
        out_trade_no=order.id,  # 订单id
        total_amount=order.amount,       # 订单金额
        subject="爱家租房_%s"%str(order.id),          # 订单标题
        return_url="127.0.0.1:5000/orders.html",   # 引导用户跳转链接
        notify_url=None  # 可选, 不填则使用默认notify url
    )
    # 用户支付链接
    pay_url = constants.ALIPAY_TEST_URL + order_string


    return jsonify(errno=RET.OK, errmsg="ok", data={"pay_url":pay_url})