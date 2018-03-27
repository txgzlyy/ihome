# coding=utf-8
from . import api
from flask import make_response,request,jsonify
from app.utils.captcha.captcha import captcha
from app import redis_store,constants
import logging
from app.utils.response_code import RET
import random



@api.route('/imagecode/')
def img_code():
    """图片验证码"""
    # 前一次的img_code_id
    pre_code_id = request.args.get('pre')
    # 当前的img_code_id
    current_code_id = request.args.get('cur')
    # 生成图片验证码
    # name-图片验证码的名字， text-图片验证码的文本， image-图片的二进制数据
    name, txt, img = captcha.generate_captcha()

    try:
        # 把 txt 存入redis 把上一次存入的该用户 验证码删除
        redis_store.delete("ImageCode_"+pre_code_id)
        redis_store.setex(name="ImageCode_"+current_code_id,time=constants.ImgCodeTime,value=txt)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")
    else:
        # 给前端返回img
        #print(img)
        response = make_response(img)
        # 设置传回给前端的内容数据是图片格式
        response.headers["Content-Type"] = "image/jpg"
        return response


@api.rout('/smscode/<mobile>')
def SmsCode(mobile):
    """短信验证码"""
    # 接收的数据格式  /sms_code/13281121596?id=xxxx&text=xxx    id:图片验证码编号  text:图片验证码文本
    img_code_id = request.args.get('id')
    img_code_text = request.args.get('text')

    # 检查数据正确性
    if not all([mobile,img_code_id,img_code_text]):
        # 返回json格式
        return jsonify({"errcode":RET.DATAERR,"errmsg":"数据错误"})

    # 检验图片验证码正确性  获取数据可能失败
    try:
        redis_img_code = redis_store.get('ImageCode_'+img_code_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据异常")

    # 如果验证码已经过期
    if redis_img_code == '':
        return jsonify(errno=RET.DBERR, errmsg="验证码已经失效")

    # 删除redis中的验证码
    try:
        redis_store.delete("ImageCode_"+img_code_id)
    except Exception as e:
        logging.error(e)

    if img_code_text == redis_img_code:
        # 发送短信验证码至手机
        # 0,1000000 的随机数  如果没有 6位 就在前面用 0 代替
        sms_code = "%06d"%random.randint(0,1000000)















