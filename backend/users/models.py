"""用户模型：对应关系模式 Client 表。"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class ClientManager(BaseUserManager):
    def create_user(self, phone, password=None, nickname="", is_admin=False, **extra):
        if not phone:
            raise ValueError("手机号不能为空")
        user = self.model(phone=phone, nickname=nickname, is_admin=is_admin, **extra)
        user.set_password(password)  # PBKDF2 哈希，不存明文
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, nickname="", **extra):
        extra.setdefault("balance", 0)
        return self.create_user(
            phone=phone, password=password, nickname=nickname, is_admin=True, **extra
        )


class Client(AbstractBaseUser):
    """client 用户表：广告客户与管理员账号。"""

    client_id = models.AutoField(primary_key=True, db_column="client_id")
    phone = models.CharField(max_length=20, unique=True, db_column="phone")
    # 继承 AbstractBaseUser.password，底层存储 PBKDF2 哈希；文档字段名 pwd_hash
    password = models.CharField(max_length=128, db_column="pwd_hash")
    nickname = models.CharField(max_length=50, blank=True, db_column="nickname")
    balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, db_column="balance"
    )
    reg_time = models.DateTimeField(auto_now_add=True, db_column="reg_time")
    is_admin = models.BooleanField(default=False, db_column="is_admin")
    is_active = models.BooleanField(default=True, db_column="is_active")

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = ClientManager()

    class Meta:
        db_table = "client"

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return self.phone


class Notification(models.Model):
    """notification 站内信表：审核结果与余额提醒。"""

    notice_id = models.AutoField(primary_key=True, db_column="notice_id")
    client = models.ForeignKey(
        "users.Client", on_delete=models.CASCADE, db_column="client_id",
        related_name="notifications",
    )
    title = models.CharField(max_length=100, db_column="title")
    content = models.TextField(blank=True, db_column="content")
    is_read = models.BooleanField(default=False, db_column="is_read")
    create_time = models.DateTimeField(auto_now_add=True, db_column="create_time")

    class Meta:
        db_table = "notification"

    def __str__(self):
        return self.title
