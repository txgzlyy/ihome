# coding=utf-8
from . import db

class UserInfo(db.Model):
    __tablename__ = 'userinfos'
    user_id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(64))
    user_mobile = db.Column(db.String(32),unique=True)
    password = db.Column(db.String(64),unique=True)
    author_url = db.Column(db.String(64))
    real_name = db.Column(db.String(64))


class HouseInfo(db.Model):
    __tablename__ = 'houseinfos'
    house_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userinfos.user_id'))
    price = db.Column(db.Float,unique=True) # 地区
    capacity = db.String(db.String(64)) # 户型
    beds = db.Column(db.String(32))
    min_days = db.Column(db.Integer)
