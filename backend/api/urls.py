"""对外接口路由。"""
from django.urls import path

from .views import TrackView

urlpatterns = [
    path("track", TrackView.as_view(), name="track"),
]
