"""审核接口（管理员）：待审核列表 / 通过 / 驳回。

驳回后自动写站内信（观察者模式落地点）。
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ads.models import Ad
from ads.serializers import AdSerializer
from users.models import Notification
from users.permissions import IsAdmin


class PendingAdListView(generics.ListAPIView):
    """GET /api/audit/pending —— 管理员查看待审核广告。"""

    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Ad.objects.filter(status=Ad.STATUS_PENDING).order_by("submit_time")


class AuditActionView(APIView):
    """审核通过 / 驳回的基类。"""

    permission_classes = [IsAuthenticated, IsAdmin]

    def _get_ad(self, pk):
        try:
            return Ad.objects.get(pk=pk, status=Ad.STATUS_PENDING)
        except Ad.DoesNotExist:
            return None


class AdPassView(AuditActionView):
    """POST /api/audit/<id>/pass —— 审核通过。"""

    def post(self, request, pk):
        ad = self._get_ad(pk)
        if ad is None:
            return Response({"detail": "广告不存在或不在待审核状态"}, status=404)
        ad.status = Ad.STATUS_APPROVED
        ad.save(update_fields=["status"])
        Notification.objects.create(
            client=ad.client,
            title="广告审核结果",
            content=f"您的广告《{ad.title}》已审核通过，进入投放池。",
        )
        return Response(AdSerializer(ad).data, status=status.HTTP_200_OK)


class AdRejectView(AuditActionView):
    """POST /api/audit/<id>/reject —— 驳回，必须填写原因。"""

    def post(self, request, pk):
        ad = self._get_ad(pk)
        if ad is None:
            return Response({"detail": "广告不存在或不在待审核状态"}, status=404)
        reason = (request.data.get("reason") or "").strip()
        if not reason:
            return Response({"detail": "驳回必须填写原因"}, status=status.HTTP_400_BAD_REQUEST)
        ad.status = Ad.STATUS_REJECTED
        ad.reject_reason = reason
        ad.save(update_fields=["status", "reject_reason"])
        Notification.objects.create(
            client=ad.client,
            title="广告审核结果",
            content=f"您的广告《{ad.title}》被驳回，原因：{reason}",
        )
        return Response(AdSerializer(ad).data, status=status.HTTP_200_OK)
