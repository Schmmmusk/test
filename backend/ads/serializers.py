"""广告序列化器。"""
from rest_framework import serializers

from .models import Ad


class AdSerializer(serializers.ModelSerializer):
    client_id = serializers.IntegerField(source="client.client_id", read_only=True)

    class Meta:
        model = Ad
        fields = [
            "ad_id", "client_id", "title", "content", "image_url", "landing_url",
            "daily_budget", "spent", "status", "submit_time", "reject_reason",
        ]
        read_only_fields = ["ad_id", "spent", "status", "submit_time", "reject_reason"]
