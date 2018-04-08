# coding=utf-8
# celery 的配置文件

REDIS_BROKER_URL = "redis://127.0.0.1:6379/1"  # 使用1号库

# celery 处理好的数据保存位置
REDIS_BACKEND = "redis://127.0.0.1:6379/2"
