"""广告模块路由。"""
from django.urls import path

from .views import AdCollectionView, ClientAdListView

urlpatterns = [
    # 前端：查看自己的广告列表（拆分后的独立路径）
    path("client/ads", ClientAdListView.as_view(), name="client-ads"),
    # 同一个 /api/ads：GET 对外拉广告（API Key），POST 前端新建送审（Token）
    path("ads", AdCollectionView.as_view(), name="ads"),
]
