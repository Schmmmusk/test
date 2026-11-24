"""审核模块路由。"""
from django.urls import path

from .views import AdPassView, AdRejectView, PendingAdListView

urlpatterns = [
    path("audit/pending", PendingAdListView.as_view(), name="audit-pending"),
    path("audit/<int:pk>/pass", AdPassView.as_view(), name="audit-pass"),
    path("audit/<int:pk>/reject", AdRejectView.as_view(), name="audit-reject"),
]
