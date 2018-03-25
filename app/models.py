# coding=utf-8
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

class Basec(object):
    create_time = db.Column(db.DateTime,default=datetime.now())
    update_time = db.Column(db.DateTime,default=datetime.now(),onupdate=datetime.now()) # 记录的更新时间  onupdate 党数据改变时


class UserInfo(Basec, db.Model):
    __tablename__ = 'ih_userinfos'
    user_id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(64),unique=True,nullable=False)
    user_mobile = db.Column(db.String(32),unique=True,nullable=False)
    password_hash = db.Column(db.String(428),unique=True)
    author_url = db.Column(db.String(512),default='')
    real_name = db.Column(db.String(64),default='')
    id_card = db.Column(db.String(20),unique=True,default='')

    @property
    def password(self):
        """获取password属性时被调用"""
        raise AttributeError("不可读")

    @password.setter
    def password(self,passwords):
        """设置password属性时被调用，设置密码加密"""
        self.password_hash = generate_password_hash(passwords)

    def check_password(self,passwords):
        """检查密码的正确性"""
        return check_password_hash(self.password_hash,passwords)


class HouseInfo(Basec, db.Model):
    __tablename__ = 'ih_houseinfos'
    house_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ih_userinfos.user_id'))
    title = db.Column(db.String(64), nullable=False)  # 标题
    price = db.Column(db.Integer,default=0)         #单价
    address = db.Column(db.String(512), default="")  # 地址
    room_count = db.Column(db.Integer, default=1)  # 房间数目
    acreage = db.Column(db.Integer, default=0)  # 房屋面积
    unit = db.Column(db.String(32), default="")  # 房屋单元， 如几室几厅
    capacity = db.Column(db.Integer, default=1)  # 房屋容纳的人数
    beds = db.Column(db.String(64),default='')   # 房屋床铺的配置
    deposit = db.Column(db.Integer, default=0)  # 房屋押金
    min_days = db.Column(db.Integer,default=1)  # 最少入住天数
    max_days = db.Column(db.Integer, default=0)  # 最多入住天数，0表示不限制
    order_count = db.Column(db.Integer, default=0)  # 预订完成的该房屋的订单数
    index_image_url = db.Column(db.String(256), default="")  # 房屋主图片的路径


# 房屋图片
class HousePic(Basec, db.Model):
    __tablename__ = "ih_housepics"
    img_id = db.Column(db.Integer,primary_key=True)
    img_url = db.Column(db.String(64))
    house_id = db.Column(db.Integer,db.ForeignKey('ih_houseinfos.house_id'))

























