#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from app.libs.ronglian_yun.CCPRestSDK import REST
import ConfigParser
print(REST)
#主帐号
accountSid= '8a216da862467c3a01626594d1a70b89';

#主帐号Token
accountToken= '6a67bd9209334b0d98c807dd929d4e90';

#应用Id
appId='8a216da862467c3a01626594d1fd0b8f';

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com';

#请求端口 
serverPort='8883';

#REST版本号
softVersion='2013-12-26';

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id

# def sendTemplateSMS(to,datas,tempId):
#
#
#     #初始化REST SDK
#     rest = REST(serverIP,serverPort,softVersion)
#     rest.setAccount(accountSid,accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to,datas,tempId)
#     for k,v in result.iteritems():
#
#         if k=='templateSMS' :
#                 for k,s in v.iteritems():
#                     print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)

#  把 sendTemplateSMS 改成单列模式


class CCP(object):
    def __init__(self):
        self.rest =  REST(serverIP, serverPort, softVersion)
        self.rest.setAccount(accountSid, accountToken)
        self.rest.setAppId(appId)

    @staticmethod
    def instance():
        if not hasattr(CCP,'_instance'):
            CCP._instance = CCP()
        return CCP._instance

    def send_template_sms(self,to, datas, tempId):
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        if result.get('statusCode')=='000000':
            # 返回0 表示发送短信成功
            return 0
        else:
            # 返回-1 表示发送失败
            return -1


# class RongLian():
#     @staticmethod
#     def instance(to,datas,tempId):
#         if not hasattr(REST, '_instance'):
#             REST._indtace = REST(serverIP, serverPort, softVersion)
#             # 初始化REST SDK
#             rest = REST._indtace
#             rest.setAccount(accountSid, accountToken)
#             rest.setAppId(appId)
#         else:
#             rest = REST._indtace
#
#         result = rest.sendTemplateSMS(to, datas, tempId)
#         if result.get('statusCode')=='000000':
#             # 返回0 表示发送短信成功
#             return 0
#         else:
#             # 返回-1 表示发送失败
#             return -1
#
#
#
#
# sendTemplateSMS = RongLian.instance
   
#sendTemplateSMS(手机号码,内容数据,模板Id)

if __name__=="__main__":
    ccp = CCP.instance()
    ccp.send_template_sms('13281121596',['1234', 5], 1)