from django.shortcuts import render
from django.views import View
from django.http import JsonResponse,HttpResponse
from rest_framework.views import APIView
from .models import UserInfo,UserToken
from . import models
import hashlib,time
from rest_framework.request import Request
from rest_framework import exceptions
from rest_framework.authentication import BasicAuthentication
from api.utils.permission import MyPermission1,SvipPermission
from api.utils.throttle import UserThrottle,VisitThrottle
from rest_framework.viewsets import ModelViewSet
# Create your views here.

#一个订单字典
ORDER_DICT = {
    1:{
        'name':'媳妇',
        'age':18,
        'gender':'女',
        'content':'这是一个可爱的女生'
    },
    2:{
        'name':'dog',
        'age':3,
        'gender':'男',
        'content':'这是一条哈士奇',
    }
}


#生成一个随机字符串
def md5(user):
    current_time = str(time.time())
    m = hashlib.md5(bytes(user,encoding="utf-8"))
    m.update(bytes(current_time,encoding="utf-8"))
    return m.hexdigest()



class AuthView(APIView):
    """
    用于用户登录认证
    """
    authentication_classes = []
    permission_classes = []
    throttle_classes = [VisitThrottle,]

    def post(self,request,*args,**kwargs):
        print("1")
        ret = {'code':1000,'message':None}
        try:
            username = request._request.POST.get('username')
            password = request._request.POST.get('password')
            exists = UserInfo.objects.filter(username=username,password=password).first()
            print(exists)
            if exists:
                # 为登录的用户创建随机字符串token
                print("="*30)
                token = md5(username)
                print(token)
                print("="*30)
                # 若该用户存在就更新，不存在就创建
                UserToken.objects.update_or_create(user=exists,defaults={'token':token})
                ret['token'] = token
            else:
                ret['code'] = 1001
                ret['message'] = "用户名或者密码错误"

        except Exception as e:
            ret['code'] = 1002
            ret['message'] = "请求异常"
        return JsonResponse(ret)



class OrderView(APIView):
    """
    订单相关页面(只有SVIP用户有权限)
    """
    # authentication_classes = [FirstAuthtication,Authtication]
    # permission_classes = [SvipPermission,]
    def get(self,request,*args,**kwargs):
        # self.dispatch()              #源码流程的入口，需要时打开，不需要时记得关闭
        # token = request._request.GET.get('token')
        # if not token:
        #     return HttpResponse("用户未登录!")


        #request.user:就相当于第一个字段：token_obj.user,
        #request.auth:就相当于第二个字段：token_obj

        # if request.user.user_type != 3:
        #     return HttpResponse("无权访问")
        result = {
            'code':1000,
            'message': None,
            'data':None,
        }
        try:
            result['data'] = ORDER_DICT

        except Exception as e:
            pass
        return JsonResponse(result)


class UserCenterView(APIView):
    """
    用户中心相关页面(普通用户和VIP)
    """
    permission_classes = [MyPermission1]
    throttle_classes = [VisitThrottle, ]
    def get(self,request,*args,**kwargs):
        print(request.user)
        return HttpResponse("用户信息")
