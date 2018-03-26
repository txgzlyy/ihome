# coding=utf-8
from . import api
from flask import make_response,request
from app.utils.captcha.captcha import captcha
from app import redis_store,constants
import logging


@api.route('/imagecode/')
def img_code():
    """图片验证码"""
    print(123)
    # 前一次的img_code_id
    pre_code_id = request.args.get('pre')
    # 当前的img_code_id
    current_code_id = request.args.get('cur')
    # 生成图片验证码
    # name-图片验证码的名字， text-图片验证码的文本， image-图片的二进制数据
    name, txt, img = captcha.generate_captcha()

    print(img)
    try:
        # 把 txt 存入redis 把上一次存入的该用户 验证码删除
        redis_store.delete("ImageCode_"+pre_code_id)
        redis_store.setex(name="ImageCode_"+current_code_id,time=constants.ImgCodeTime,value=txt)
    except Exception as e:
        logging.error(e)
    else:
        # 给前端返回img
        #print(img)
        response = make_response(img)
        # 设置传回给前端的内容数据是图片格式
        response.headers["Content-Type"] = "image/jpg"
        return response