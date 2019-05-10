from rest_framework.throttling import BaseThrottle,SimpleRateThrottle
import time

# VISTI_RECORD = {
#
# }
#
#
# class VisitThrottle(BaseThrottle):
#     """
#     60s内只能访问3次
#     """
#     def __init__(self):
#         self.history = []
#
#     def allow_request(self,request,view):
#         #1.获取用户ip
#         # remote_addr = request._request.META.get('REMOTE_ADDR')
#         remote_addr = self.get_ident(request)
#         current_time = time.time()
#         if remote_addr not in VISTI_RECORD:
#             VISTI_RECORD[remote_addr] = [current_time]
#             return True
#         history = VISTI_RECORD.get(remote_addr)
#         self.history = history
#         while history and history[-1] < current_time-60:
#             history.pop()
#         if len(history)<3:
#             history.insert(0,current_time)
#             return True
#         return False
#         # print(remote_addr)
#         # return True #:表示可以继续访问
#         #return False:表示访问频率太高，被限制
#
#     def wait(self):
#         """
#         还需要等多少秒才能访问
#         :return:
#         """
#         current_time = time.time()
#         return 60-(current_time-self.history[-1])


class VisitThrottle(SimpleRateThrottle):
    scope = "Luffy"

    def get_cache_key(self, request, view):
        return self.get_ident(request)

class UserThrottle(SimpleRateThrottle):
    scope = "LuffyUser"

    def get_cache_key(self, request, view):
        return request.user.username