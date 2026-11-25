"""用户与站内信序列化器。"""
from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import Client, Notification


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Client
        fields = ["client_id", "phone", "password", "nickname"]
        read_only_fields = ["client_id"]

    def create(self, validated_data):
        return Client.objects.create_user(
            phone=validated_data["phone"],
            password=validated_data["password"],
            nickname=validated_data.get("nickname", ""),
        )


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(phone=attrs["phone"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError("手机号或密码错误")
        if not user.is_active:
            raise serializers.ValidationError("账号已停用")
        attrs["user"] = user
        return attrs


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["client_id", "phone", "nickname", "balance", "reg_time", "is_admin"]
        read_only_fields = fields


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["notice_id", "title", "content", "is_read", "create_time"]
        read_only_fields = fields
