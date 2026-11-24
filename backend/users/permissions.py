"""权限类：管理员权限 与 对外接口 API Key 鉴权。"""
from django.conf import settings
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """仅管理员可访问（审核管理等）。"""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class HasPartnerAPIKey(BasePermission):
    """对外接口鉴权：请求头 api_key 必须匹配服务端配置，否则 401。"""

    def has_permission(self, request, view):
        key = request.headers.get("api_key")
        return bool(key and key == settings.PARTNER_API_KEY)
