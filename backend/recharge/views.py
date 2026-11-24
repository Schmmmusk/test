"""充值接口：充值下单（更新余额）/ 充值流水 / 低额预警。"""
from decimal import Decimal

from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Notification

from .models import Recharge
from .serializers import RechargeSerializer

LOW_BALANCE_THRESHOLD = Decimal("50")


class RechargeView(APIView):
    """POST /api/recharge —— 充值，更新余额并记流水；低于阈值发站内信。"""

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        amount_str = request.data.get("amount")
        order_no = (request.data.get("order_no") or "").strip()
        try:
            amount = Decimal(str(amount_str))
        except (TypeError, ValueError):
            return Response({"detail": "充值金额格式错误"}, status=400)
        if amount <= 0:
            return Response({"detail": "充值金额必须大于 0"}, status=400)
        if not order_no:
            return Response({"detail": "订单号不能为空"}, status=400)
        if Recharge.objects.filter(order_no=order_no).exists():
            return Response({"detail": "订单号已存在"}, status=400)

        Recharge.objects.create(client=request.user, amount=amount, order_no=order_no)

        # 余额更新：用 F 表达式避免并发覆盖
        from django.db.models import F

        request.user.__class__.objects.filter(pk=request.user.pk).update(
            balance=F("balance") + amount
        )
        request.user.refresh_from_db()

        # 低额预警：充值后余额仍低于阈值也提醒（按设计文档"余额低于 50 元自动发提醒"）
        if request.user.balance < LOW_BALANCE_THRESHOLD:
            Notification.objects.create(
                client=request.user,
                title="余额提醒",
                content=f"您的账户余额为 {request.user.balance} 元，低于 {LOW_BALANCE_THRESHOLD} 元。",
            )

        return Response(
            {
                "message": "充值成功",
                "balance": str(request.user.balance),
            },
            status=status.HTTP_200_OK,
        )


class RechargeListView(generics.ListAPIView):
    """GET /api/recharges —— 查看当前客户充值流水。"""

    serializer_class = RechargeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recharge.objects.filter(client=self.request.user).order_by("-recharge_time")
