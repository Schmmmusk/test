"""对外回传接口：曝光/点击上报。"""
from decimal import Decimal

from django.conf import settings
from django.db.models import F
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ads.models import Ad

from .models import Impression

# 单次点击消耗（元）：按用户裁定为 0.01 元
COST_PER_CLICK = Decimal("0.01")


class TrackView(APIView):
    """POST /api/track —— 合作网站上报展示/点击事件，API Key 鉴权。

    body: { ad_id, event_type: impression|click, source? }
    Key 错误返回 401，不写任何数据。
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # Django runserver 会剥离带下划线的 header，故用 Api-Key（连字符）传输
        api_key = request.headers.get("Api-Key") or request.headers.get("api_key")
        if api_key != settings.PARTNER_API_KEY:
            return Response(
                {"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        ad_id = request.data.get("ad_id")
        event_type = request.data.get("event_type")
        source = request.data.get("source", "")

        if event_type not in (Impression.EVENT_IMPRESSION, Impression.EVENT_CLICK):
            return Response({"detail": "event_type 无效"}, status=400)
        try:
            ad = Ad.objects.get(pk=ad_id)
        except (Ad.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "广告不存在"}, status=400)

        Impression.objects.create(
            ad=ad,
            client=ad.client,
            event_type=event_type,
            source=source,
        )

        # 若为点击事件，累加广告消耗（单次点击 0.01 元）
        if event_type == Impression.EVENT_CLICK:
            Ad.objects.filter(pk=ad.pk).update(
                spent=F("spent") + COST_PER_CLICK
            )

        return Response({"detail": "ok"}, status=status.HTTP_201_CREATED)
