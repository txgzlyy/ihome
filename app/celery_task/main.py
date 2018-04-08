# coding=utf-8
# celery 启动文件
from celery import Celery
from app.celery_task import config

# 创建celery 对象
celery_app = Celery("ihome")


# 引入配置信息
celery_app.config_from_object(config)



# 开启自动搜索任务
celery_app.autodiscover_tasks(['app.celery_task.sms'])