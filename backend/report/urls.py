"""报表模块路由。"""
from django.urls import path

from .views import ReportView

urlpatterns = [
    path("report", ReportView.as_view(), name="report"),
]
