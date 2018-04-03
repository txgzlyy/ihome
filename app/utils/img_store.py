# coding=utf-8
# 使用七牛云存储

from qiniu import Auth, put_data

# 需要填写你的 Access Key 和 Secret Key

access_key = 'faZIkGvlnPqqHPLHeHcq6B537bLv4vmbh8xG0rlX'
secret_key = '7TUX_S0VBvnC9lskQpgSKuedMmNzUaYOUvS0YDsE'

# 要上传的空间
bucket_name = 'ihome'
import logging


def img_store(data):
    '''七牛云存储上传'''
    if not data:
        return None
    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)
        # 生成上传 Token，可以指定过期时间等  和确定上传的空间
        token = q.upload_token(bucket_name)
        # 上传文件
        ret,info = put_data(token,None,data)
    except Exception as e:
        logging.error(e)
        raise e
    if not ret:
        raise Exception('文件上传失败')

    return ret['key']   # 返回图片名


if __name__ == "__main__":
    file_name = raw_input('文件名')
    with open(file_name,'rb') as f:
        print(img_store(f.read()))
