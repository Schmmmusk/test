"""用户模块路由：注册 / 登录 / 站内信。"""
from django.urls import path

from .views import LoginView, NotificationListView, RegisterView

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("notifications", NotificationListView.as_view(), name="notifications"),
]
