"""数据报表接口：展示量 / 点击量 / 消耗汇总。"""
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ads.models import Ad
from api.models import Impression


class ReportView(APIView):
    """GET /api/report —— 当前客户广告的汇总统计（前端 ECharts 取数）。"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        ads = Ad.objects.filter(client=user)
        imp_qs = Impression.objects.filter(client=user)

        impression_count = imp_qs.filter(
            event_type=Impression.EVENT_IMPRESSION
        ).count()
        click_count = imp_qs.filter(event_type=Impression.EVENT_CLICK).count()
        total_spent = ads.aggregate(total=Sum("spent"))["total"] or 0

        return Response(
            {
                "ad_count": ads.count(),
                "impression_count": impression_count,
                "click_count": click_count,
                "total_spent": str(total_spent),
            },
            status=200,
        )
