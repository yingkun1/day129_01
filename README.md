# day129_01
这是django的rest framework框架的demo,包含了授权Permission和节流Throttle
s7day129
内容回顾：
	1.中间件
	2.csrf原理（process view）
	3.rest 10规范
	4.面向对象
	5.django请求生命周期
	6.django请求生命周期(包含rest framework框架)

今日内容：
	1.认证
		a.问题1：有些API需要用户登录成功之后才能访问，有些无需登录就能访问
		b.基本使用认证组件：
			解决：
				a.创建两张表
				b.用户登录(返回token并保存到数据库)
		c.流程：当请求进来，第一步：找dispatch(APIView中)，在dispatch中又做了什么呢？对request进行了封装initialize_request，封装了一些函数
		return Request(
            request,
            parsers=self.get_parsers(),
            authenticators=self.get_authenticators(),
            negotiator=self.get_content_negotiator(),
            parser_context=parser_context
        )
        对于其中的get_authenticators()的函数，通过列表生成式return [auth() for auth in self.authentication_classes]，返回了一个个对象，注意authentication_classes
        authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES，对于这条语句，注意我们是设置了的
        authentication_classes = [Authtication,]
        可以参看restframework认证流程.png
        d.再看一遍源码
        	1.认证可以局部实现，也可以全局实现
        	2.匿名(未授权)的用户，request.user=None
        e.内置认证类
        	1.认证类，必须继承：from rest_framework.authentication import BaseAuthentication
        	2.其他认证类：BasicaAuthentication,
        梳理：
        	1.使用
        		-创建类：继承from rest_framework.authentication import BasicAuthentication,BaseAuthentication,实现：
        		    def authenticate(self,request):
				        pass

				    def authenticate_header(self,request):
				        pass
				-返回值
					-None:让下一个认证来执行
					-抛出异常：raise exceptions.AuthenticationFailed("用户认证失败")，这个异常需要先引用：from rest_framework import exceptions
					-（元素1，元素2）#元素1赋值给request.user,元素2赋值给request.auth
				-当前类使用：
					from rest_framework.authentication import BasicAuthentication
					class UserCenterView(APIView):
					    """
					    用户中心相关页面
					    """
					    authentication_classes = [BasicAuthentication,]
					    def get(self,request,*args,**kwargs):
					        print(request.user)
					        return HttpResponse("用户信息")
				-全局使用：
					REST_FRAMEWORK = {
					    #全局使用的认证类
					    "DEFAULT_AUTHENTICATION_CLASSES":['api.utils.auth.FirstAuthtication','api.utils.auth.Authtication'],
					    # "DEFAULT_AUTHENTICATION_CLASSES":['api.utils.auth.FirstAuthtication'],
					    # "UNAUTHENTICATED_USER":lambda :"匿名用户"
					    # "UNAUTHENTICATED_USER":"匿名用户",
					    "UNAUTHENTICATED_USER":None,        #推荐使用None,对于未授权或者未登陆的用户，request.user=None
					    "UNAUTHENTICATED_TOKEN":None,       #推荐使用None
					}
			2.源码流程
				-dispatch
					-封装request
						-获取定义的认证类(全局/单个视图),通过列表生成式创建对象
					-initial
						-perform_authentication
							request.user(内部循环)

	2.权限
		问题：不同视图不同的权限才可以访问
		基本使用：
			class MyPermission(object):
			    def has_permission(self,request,view):
			        if request.user.user_type != 3:
			            return False
			        return True

			class UserCenterView(APIView):
				"""
				用户中心相关页面(普通用户和VIP)
				"""
				permission_classes = [MyPermission1]            //在这里使用
				def get(self,request,*args,**kwargs):
				    print(request.user)
				    return HttpResponse("用户信息")
		源码流程：

		梳理：
			1.使用
				-类：必须继承BasePermission，必须实现：has_permission方法
					from rest_framework.permissions import BasePermission

					class SvipPermission(BasePermission):
					    message = "必须是SVIP才能访问"
					    def has_permission(self,request,view):
					        if request.user.user_type != 3:
					            return False
					        return True

					class MyPermission1(BasePermission):
					    def has_permission(self,request,view):
					        if request.user.user_type == 3:
					            return False
					        return True

				返回值：
					-True:有权访问
					-False:无权访问

				全局：
					REST_FRAMEWORK = {
					    #全局使用的认证类
					    "UNAUTHENTICATED_TOKEN":None,       #推荐使用None

					    #全局使用的权限类
					    "DEFAULT_PERMISSION_CLASSES":['api.utils.permission.SvipPermission']
					}

				单个类视图使用：
					class UserCenterView(APIView):
					    """
					    用户中心相关页面(普通用户和VIP)
					    """
					    permission_classes = [MyPermission1]        //在这里使用
					    def get(self,request,*args,**kwargs):
					        print(request.user)
					        return HttpResponse("用户信息")
			2.源码流程
	3.节流（访问频率控制）
		问题：控制访问频率
			class VisitThrottle(object):
			    """
			    60s内只能访问3次
			    """
			    def __init__(self):
			        self.history = []

			    def allow_request(self,request,view):
			        #1.获取用户ip
			        remote_addr = request._request.META.get('REMOTE_ADDR')
			        current_time = time.time()
			        if remote_addr not in VISTI_RECORD:
			            VISTI_RECORD[remote_addr] = [current_time]
			            return True
			        history = VISTI_RECORD.get(remote_addr)
			        self.history = history
			        while history and history[-1] < current_time-60:
			            history.pop()
			        if len(history)<3:
			            history.insert(0,current_time)
			            return True
			        return False
			        # print(remote_addr)
			        # return True #:表示可以继续访问
			        #return False:表示访问频率太高，被限制

			    def wait(self):
			        """
			        还需要等多少秒才能访问
			        :return:
			        """
			        current_time = time.time()
			        return 60-(current_time-self.history[-1])
			源码流程：
				...
			
			内置控制频率类(节流)
			class VisitThrottle(SimpleRateThrottle):
			    scope = "Luffy"

			    def get_cache_key(self, request, view):
			        return self.get_ident(request)

			class UserThrottle(SimpleRateThrottle):
			    scope = "LuffyUser"

			    def get_cache_key(self, request, view):
			        return request.user.username
			"DEFAULT_THROTTLE_RATES":{
		        "Luffy":'3/m',          #每分钟三次
		        "LuffyUser":'10/m',
		    },
		    梳理：
		    	a.基本使用
		    		-类，继承：BaseThrottle,实现：allow_request,wait
		    		-类，继承：SimpleRateThrottle，实现：get_cache_key，scope = "Luffy"
		    			 "DEFAULT_THROTTLE_RATES":{
						        "Luffy":'3/m',          #每分钟三次
						        "LuffyUser":'10/m',
						    },

				b.单个类实现：
					class UserCenterView(APIView):
					    """
					    用户中心相关页面(普通用户和VIP)
					    """
					    permission_classes = [MyPermission1]
					    throttle_classes = [VisitThrottle, ]          #引入VisitThrottle
					    def get(self,request,*args,**kwargs):
					        print(request.user)
					        return HttpResponse("用户信息")

				c.全局：
					全局配置：
						REST_FRAMEWORK = {
						    #全局使用的认证类
						    "UNAUTHENTICATED_TOKEN":None,       #推荐使用None

						    #全局使用的权限类
						    "DEFAULT_PERMISSION_CLASSES":['api.utils.permission.SvipPermission'],

						    #全局使用的节流类
						    "DEFAULT_THROTTLE_CLASSES":['api.utils.throttle.VisitThrottle']
						}
		今日作业
