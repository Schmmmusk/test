"""展示记录模型：对应关系模式 Impression 表。"""
from django.db import models


class Impression(models.Model):
    EVENT_IMPRESSION = "impression"
    EVENT_CLICK = "click"
    EVENT_CHOICES = [
        (EVENT_IMPRESSION, "展示"),
        (EVENT_CLICK, "点击"),
    ]

    imp_id = models.AutoField(primary_key=True, db_column="imp_id")
    ad = models.ForeignKey(
        "ads.Ad", on_delete=models.CASCADE, db_column="ad_id",
        related_name="impressions",
    )
    client = models.ForeignKey(
        "users.Client", on_delete=models.CASCADE, db_column="client_id",
        related_name="impressions",
    )
    event_type = models.CharField(max_length=16, choices=EVENT_CHOICES, db_column="event_type")
    event_time = models.DateTimeField(auto_now_add=True, db_column="event_time")
    source = models.CharField(max_length=100, blank=True, db_column="source")

    class Meta:
        db_table = "impression"

    def __str__(self):
        return f"{self.ad_id}-{self.event_type}"
