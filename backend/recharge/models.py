"""充值记录模型：对应关系模式 Recharge 表。"""
from django.db import models


class Recharge(models.Model):
    recharge_id = models.AutoField(primary_key=True, db_column="recharge_id")
    client = models.ForeignKey(
        "users.Client", on_delete=models.CASCADE, db_column="client_id",
        related_name="recharges",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, db_column="amount")
    order_no = models.CharField(max_length=64, unique=True, db_column="order_no")
    recharge_time = models.DateTimeField(auto_now_add=True, db_column="recharge_time")

    class Meta:
        db_table = "recharge"

    def __str__(self):
        return self.order_no
