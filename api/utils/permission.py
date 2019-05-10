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