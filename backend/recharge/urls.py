"""充值模块路由。"""
from django.urls import path

from .views import RechargeListView, RechargeView

urlpatterns = [
    path("recharge", RechargeView.as_view(), name="recharge"),
    path("recharges", RechargeListView.as_view(), name="recharges"),
]
