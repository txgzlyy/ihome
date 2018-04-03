# coding=utf-8
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from app import constants

class Basec(object):
    create_time = db.Column(db.DateTime,default=datetime.now())
    update_time = db.Column(db.DateTime,default=datetime.now(),onupdate=datetime.now()) # 记录的更新时间  onupdate 党数据改变时


class UserInfo(Basec, db.Model):
    __tablename__ = 'ih_userinfos'
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(64),unique=True,nullable=False)
    user_mobile = db.Column(db.String(32),unique=True,nullable=False)
    password_hash = db.Column(db.String(428),unique=True)
    author_url = db.Column(db.String(512),default='')   # 头像
    real_name = db.Column(db.String(64),default='')     # 真实姓名
    id_card = db.Column(db.String(20),unique=True,default='')

    house = db.relationship('HouseInfo',backref='ih_userinfos')  # house 是用户信息的一个属性  用户是房屋的一个外键
    order = db.relationship("Order",backref="ih_userinfos")      # order 是用户信息的一个属性

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

    def get_dict(self):
        data = {
            "name":self.user_name,
            "mobile": self.user_mobile,
            "avatar": constants.QINIUIMGURL + self.author_url if self.author_url else ""
        }
        return data


# 房屋设施表，建立房屋与设施的多对多关系
house_facility = db.Table(
    "ih_house_facility",
    db.Column("house_id", db.Integer, db.ForeignKey("ih_houseinfos.id"), primary_key=True),  # 房屋编号
    db.Column("facility_id", db.Integer, db.ForeignKey("ih_facilitys.id"), primary_key=True)  # 设施编号
    # ,db.Column("create_time", db.DateTime, default=datetime.now),
    # db.Column("update_time", db.DateTime, default=datetime.now, onupdate=datetime.now)
)


class HouseInfo(Basec, db.Model):
    __tablename__ = 'ih_houseinfos'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('ih_userinfos.id'))
    area_id = db.Column(db.Integer, db.ForeignKey("ih_areas.id"), nullable=False)  # 归属地的区域编号

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

    facilities = db.relationship("Facility", secondary=house_facility)  # 房屋的设施
    house_pic = db.relationship('HousePic')
    order = db.relationship("Order", backref="ih_houseinfos")  # order 是房屋信息的一个属性


class HousePic(Basec, db.Model):
    """房屋图片"""
    __tablename__ = "ih_housepics"
    id = db.Column(db.Integer,primary_key=True)

    house_id = db.Column(db.Integer, db.ForeignKey('ih_houseinfos.id'), nullable=False)

    img_url = db.Column(db.String(256),nullable=False)


class Facility(Basec,db.Model):
    '''设施信息'''
    __tablename__ = 'ih_facilitys'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),nullable=False)


class Area(Basec,db.Model):
    """城区"""
    __tablename__ = 'ih_areas'
    id = db.Column(db.Integer,primary_key=True)

    house = db.relationship('HouseInfo',backref="ih_areas")

    name = db.Column(db.String(32), nullable=False)  # 区域名字


class Order(Basec,db.Model):
    '''订单'''
    __tablename__ = 'ih_orders'
    id = db.Column(db.Integer,primary_key=True)

    user_id = db.Column(db.Integer,db.ForeignKey('ih_userinfos.id'),nullable=False)
    house_id = db.Column(db.Integer,db.ForeignKey('ih_houseinfos.id'),nullable=False)

    begin_date = db.Column(db.DateTime, nullable=False)  # 预订的起始时间
    end_date = db.Column(db.DateTime, nullable=False)  # 预订的结束时间
    days = db.Column(db.Integer, nullable=False)  # 预订的总天数
    house_price = db.Column(db.Integer, nullable=False)  # 房屋的单价
    amount = db.Column(db.Integer, nullable=False)  # 订单的总金额
    status = db.Column(  # 订单的状态
        db.Enum(
            "WAIT_ACCEPT",  # 待接单,
            "WAIT_PAYMENT",  # 待支付
            "PAID",  # 已支付
            "WAIT_COMMENT",  # 待评价
            "COMPLETE",  # 已完成
            "CANCELED",  # 已取消
            "REJECTED"  # 已拒单
        ),
        default="WAIT_ACCEPT", index=True)
    comment = db.Column(db.Text)  # 订单的评论信息或者拒单原因
























