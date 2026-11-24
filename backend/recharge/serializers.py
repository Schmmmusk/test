"""充值序列化器。"""
from rest_framework import serializers

from .models import Recharge


class RechargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recharge
        fields = ["recharge_id", "amount", "order_no", "recharge_time"]
        read_only_fields = ["recharge_id", "recharge_time"]
