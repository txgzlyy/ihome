# coding=utf-8
# 文件取名为task celery 自动识别
from app.celery_task.main import celery_app
from app.utils.sms import CCP



@celery_app.task
def send_sms(to, datas, temp_id):
    ccp = CCP.instance()
    #  sendTemplateSMS(手机号码,内容数据,模板Id)
    ccp.send_template_sms(to,datas,temp_id)


#  开启 celery 服务

# celery -A celer对象（celery_app）所在的模块文件 worker -l 日志信息级别       celery -A app.celery_task.celery_sms worker -l info