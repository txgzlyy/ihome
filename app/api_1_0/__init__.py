# coding=utf-8

from flask import Blueprint

api = Blueprint('api',__name__)

# 要导入视图才会生效
from . import verifycode, user, profile, house


