#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from app.libs.ronglian_yun.CCPRestSDK import REST
import ConfigParser
print(REST)
#���ʺ�
accountSid= '8a216da862467c3a01626594d1a70b89';

#���ʺ�Token
accountToken= '6a67bd9209334b0d98c807dd929d4e90';

#Ӧ��Id
appId='8a216da862467c3a01626594d1fd0b8f';

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com';

#����˿� 
serverPort='8883';

#REST�汾��
softVersion='2013-12-26';

  # ����ģ�����
  # @param to �ֻ�����
  # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
  # @param $tempId ģ��Id

# def sendTemplateSMS(to,datas,tempId):
#
#
#     #��ʼ��REST SDK
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

#  �� sendTemplateSMS �ĳɵ���ģʽ


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
            # ����0 ��ʾ���Ͷ��ųɹ�
            return 0
        else:
            # ����-1 ��ʾ����ʧ��
            return -1


# class RongLian():
#     @staticmethod
#     def instance(to,datas,tempId):
#         if not hasattr(REST, '_instance'):
#             REST._indtace = REST(serverIP, serverPort, softVersion)
#             # ��ʼ��REST SDK
#             rest = REST._indtace
#             rest.setAccount(accountSid, accountToken)
#             rest.setAppId(appId)
#         else:
#             rest = REST._indtace
#
#         result = rest.sendTemplateSMS(to, datas, tempId)
#         if result.get('statusCode')=='000000':
#             # ����0 ��ʾ���Ͷ��ųɹ�
#             return 0
#         else:
#             # ����-1 ��ʾ����ʧ��
#             return -1
#
#
#
#
# sendTemplateSMS = RongLian.instance
   
#sendTemplateSMS(�ֻ�����,��������,ģ��Id)

if __name__=="__main__":
    ccp = CCP.instance()
    ccp.send_template_sms('13281121596',['1234', 5], 1)