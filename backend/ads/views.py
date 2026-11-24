"""广告接口：前端列表/创建 + 对外拉广告。

GET  /api/ads        对外-合作网站拉广告（API Key），仅 approved 且未超额，无广告返回 []
POST /api/ads        前端-新建广告并送审（Token）
GET  /api/client/ads 前端-查看当前客户自己的广告列表（Token）
"""
from django.conf import settings
from django.db.models import F
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Ad
from .serializers import AdSerializer


class ClientAdListView(generics.ListAPIView):
    """GET /api/client/ads —— 前端查看自己广告列表（需 Token）。"""

    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(client=self.request.user).order_by("-submit_time")


class AdCollectionView(APIView):
    """/api/ads —— GET 对外拉广告（API Key）；POST 前端新建送审（Token）。

    GET 的文档约定：Key 错误返回 401 且不返回任何业务数据；无广告返回 []。
    """

    def get_permissions(self):
        # GET 走 API Key 手动校验（需精确控制 401），POST 走 Token 认证
        if self.request.method == "GET":
            return []
        return [IsAuthenticated()]

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()

    def get(self, request):
        # Django runserver 会剥离带下划线的 header，故用 Api-Key（连字符）传输
        api_key = request.headers.get("Api-Key") or request.headers.get("api_key")
        if api_key != settings.PARTNER_API_KEY:
            return Response(
                {"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        qs = (
            Ad.objects.filter(status=Ad.STATUS_APPROVED)
            .filter(spent__lt=F("daily_budget"))
            .order_by("-submit_time")
        )
        return Response(AdSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(client=request.user, status=Ad.STATUS_PENDING)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
