"""广告模型：对应关系模式 Ad 表。"""
from django.db import models


class Ad(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_PAUSED = "paused"
    STATUS_CHOICES = [
        (STATUS_PENDING, "待审核"),
        (STATUS_APPROVED, "通过"),
        (STATUS_REJECTED, "驳回"),
        (STATUS_PAUSED, "暂停"),
    ]

    ad_id = models.AutoField(primary_key=True, db_column="ad_id")
    client = models.ForeignKey(
        "users.Client", on_delete=models.CASCADE, db_column="client_id",
        related_name="ads",
    )
    title = models.CharField(max_length=100, db_column="title")
    content = models.TextField(blank=True, db_column="content")
    image_url = models.CharField(max_length=300, blank=True, db_column="image_url")
    landing_url = models.CharField(max_length=300, blank=True, db_column="landing_url")
    daily_budget = models.DecimalField(max_digits=12, decimal_places=2, db_column="daily_budget")
    spent = models.DecimalField(max_digits=12, decimal_places=2, default=0, db_column="spent")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING, db_column="status")
    submit_time = models.DateTimeField(auto_now_add=True, db_column="submit_time")
    reject_reason = models.TextField(blank=True, null=True, db_column="reject_reason")

    class Meta:
        db_table = "ad"

    def __str__(self):
        return self.title
