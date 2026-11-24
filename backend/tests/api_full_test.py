# -*- coding: utf-8 -*-
"""广告平台后端 API 全面测试（37 项）。

运行（在 backend 目录下）：
    .venv\\Scripts\\python.exe tests\\api_full_test.py

覆盖：13 个接口 + 鉴权边界 + 业务规则 + 点击消耗 0.01 元口径。

数据隔离策略：
    测试开始时快照现有 client_id，结束时（含异常）仅删除本次新增的账号
    及其级联数据（ad / impression / notification / recharge / token），
    绝不触碰测试前已存在的数据。

注意：本脚本直连真实 MySQL（ad_platform），不需要创建 test_ 数据库，
因此不依赖数据库账户的 CREATE DATABASE 权限。
"""
import os
import sys
import json
import random
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adplatform.settings")

import django
django.setup()

from django.conf import settings
from django.test import Client
from users.models import Client as ClientModel
from ads.models import Ad
from api.models import Impression

# test client 使用 testserver 主机名，临时放行（不改生产配置）
settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ["testserver"]

results = []


def check(name, cond, detail=""):
    ok = bool(cond)
    results.append((name, ok, detail))
    print(("PASS" if ok else "FAIL"), name, "|", str(detail)[:120])


c = Client()
KEY = settings.PARTNER_API_KEY


def jpost(path, payload, key=None, token=None):
    h = {}
    if key is not None:
        h["HTTP_api_key"] = key
    if token is not None:
        h["HTTP_AUTHORIZATION"] = f"Token {token}"
    return c.post(path, data=json.dumps(payload, ensure_ascii=False),
                  content_type="application/json", **h)


# 快照：测试前已存在的账号
baseline_ids = set(ClientModel.objects.values_list("client_id", flat=True))

try:
    suffix = str(random.randint(100000, 999999))
    phone_c = "138" + suffix[-8:]
    phone_a = "139" + suffix[-8:]

    # ============ 一、注册 / 登录 / 鉴权 ============
    r = jpost("/api/register", {"phone": phone_c, "password": "test123456", "nickname": "客户"})
    check("01 注册客户 201", r.status_code == 201, r.status_code)

    r = jpost("/api/register", {"phone": phone_a, "password": "admin123456", "nickname": "管理员"})
    check("02 注册管理员 201", r.status_code == 201, r.status_code)
    ClientModel.objects.filter(phone=phone_a).update(is_admin=True)

    r = jpost("/api/register", {"phone": phone_c, "password": "test123456"})
    check("03 重复手机号注册被拒 400", r.status_code == 400, r.status_code)

    r = jpost("/api/login", {"phone": phone_c, "password": "test123456"})
    check("04 登录返回 token 200", r.status_code == 200 and "token" in r.json(), r.status_code)
    token_c = r.json()["token"]

    r = jpost("/api/login", {"phone": phone_a, "password": "admin123456"})
    token_a = r.json()["token"]
    check("05 管理员登录 200", r.status_code == 200 and "token" in r.json(), r.status_code)

    r = jpost("/api/login", {"phone": phone_c, "password": "wrongpass"})
    check("06 错误密码登录被拒 400", r.status_code == 400, r.status_code)

    r = jpost("/api/login", {"phone": "19900000000", "password": "test123456"})
    check("07 不存在账号登录被拒 400", r.status_code == 400, r.status_code)

    r = c.get("/api/client/ads")
    check("08 无 Token 访问受保护接口 401", r.status_code == 401, r.status_code)
    r = c.get("/api/client/ads", HTTP_AUTHORIZATION="Token bogus-token")
    check("09 错误 Token 401", r.status_code == 401, r.status_code)

    # ============ 二、广告创建 / 列表 / 审核 ============
    ad_payload = {"title": "测试广告", "content": "文案", "image_url": "http://x/i.png",
                  "landing_url": "http://x", "daily_budget": "100.00"}
    r = jpost("/api/ads", {**ad_payload, "title": "待审核广告"}, token=token_c)
    check("10 POST /api/ads 新建送审 201", r.status_code == 201 and r.json()["status"] == "pending", r.status_code)
    ad_id = r.json()["ad_id"]

    r = jpost("/api/ads", {**ad_payload, "title": "第二条广告"}, token=token_c)
    ad2 = r.json()["ad_id"]

    r = c.get("/api/client/ads", HTTP_AUTHORIZATION=f"Token {token_c}")
    check("11 GET /api/client/ads 返回本人广告", r.status_code == 200 and len(r.json()) == 2, r.status_code)

    r = c.get("/api/audit/pending", HTTP_AUTHORIZATION=f"Token {token_c}")
    check("12 非管理员访问审核列表被拒 403", r.status_code in (401, 403), r.status_code)
    r = c.get("/api/audit/pending", HTTP_AUTHORIZATION=f"Token {token_a}")
    check("13 管理员查看待审核列表 200", r.status_code == 200 and any(a["ad_id"] == ad_id for a in r.json()), r.status_code)

    r = c.get("/api/ads", HTTP_api_key=KEY)
    check("14 审核通过前不进投放池", r.status_code == 200 and all(a["ad_id"] != ad_id for a in r.json()), r.status_code)
    r = c.get("/api/ads")
    check("15 对外拉广告无 Key 401", r.status_code == 401, r.status_code)
    r = c.get("/api/ads", HTTP_api_key="wrong-key")
    check("16 对外拉广告错 Key 401", r.status_code == 401, r.status_code)

    r = c.post(f"/api/audit/{ad2}/reject", data=json.dumps({}), content_type="application/json",
               HTTP_AUTHORIZATION=f"Token {token_a}")
    check("17 驳回无原因被拒 400", r.status_code == 400, r.status_code)
    r = c.post(f"/api/audit/{ad2}/reject", data=json.dumps({"reason": "素材违规"}), content_type="application/json",
               HTTP_AUTHORIZATION=f"Token {token_a}")
    check("18 驳回带原因 200", r.status_code == 200 and r.json()["status"] == "rejected", r.status_code)
    r = c.post(f"/api/audit/{ad2}/pass", HTTP_AUTHORIZATION=f"Token {token_a}")
    check("19 已驳回广告不能再通过 404", r.status_code == 404, r.status_code)

    r = c.post(f"/api/audit/{ad_id}/pass", HTTP_AUTHORIZATION=f"Token {token_a}")
    check("20 审核通过 200", r.status_code == 200 and r.json()["status"] == "approved", r.status_code)
    r = c.get("/api/ads", HTTP_api_key=KEY)
    check("21 通过后进入投放池", r.status_code == 200 and any(a["ad_id"] == ad_id for a in r.json()), r.status_code)

    # ============ 三、回传 + 点击消耗 0.01 ============
    r = jpost("/api/track", {"ad_id": ad_id, "event_type": "impression", "source": "p1"}, key=KEY)
    check("22 曝光回传 201", r.status_code == 201, r.status_code)
    r = jpost("/api/track", {"ad_id": ad_id, "event_type": "click", "source": "p1"}, key=KEY)
    check("23 点击回传 201", r.status_code == 201, r.status_code)
    r = jpost("/api/track", {"ad_id": ad_id, "event_type": "click"}, key="wrong")
    check("24 回传错 Key 401", r.status_code == 401, r.status_code)
    r = jpost("/api/track", {"ad_id": ad_id, "event_type": "bogus"}, key=KEY)
    check("25 非法 event_type 400", r.status_code == 400, r.status_code)
    r = jpost("/api/track", {"ad_id": 999999, "event_type": "click"}, key=KEY)
    check("26 不存在广告回传 400", r.status_code == 400, r.status_code)

    ad_obj = Ad.objects.get(pk=ad_id)
    check("27 单次点击消耗=0.01元", ad_obj.spent == Decimal("0.01"), f"spent={ad_obj.spent}")
    imp_cnt = Impression.objects.filter(ad_id=ad_id, event_type="impression").count()
    clk_cnt = Impression.objects.filter(ad_id=ad_id, event_type="click").count()
    check("28 曝光/点击日志各1条", imp_cnt == 1 and clk_cnt == 1, f"imp={imp_cnt} clk={clk_cnt}")

    jpost("/api/track", {"ad_id": ad_id, "event_type": "click"}, key=KEY)
    ad_obj.refresh_from_db()
    check("29 两次点击累加=0.02元", ad_obj.spent == Decimal("0.02"), f"spent={ad_obj.spent}")

    # ============ 四、充值 / 流水 / 预警 ============
    r = jpost("/api/recharge", {"amount": "200.00", "order_no": "ORD" + suffix}, token=token_c)
    check("30 充值 200 元成功", r.status_code == 200 and r.json()["balance"] == "200.00", r.status_code)
    r = jpost("/api/recharge", {"amount": "50.00", "order_no": "ORD" + suffix}, token=token_c)
    check("31 重复订单号被拒 400", r.status_code == 400, r.status_code)
    r = jpost("/api/recharge", {"amount": "-10", "order_no": "NEG" + suffix}, token=token_c)
    check("32 负数充值被拒 400", r.status_code == 400, r.status_code)
    r = c.get("/api/recharges", HTTP_AUTHORIZATION=f"Token {token_c}")
    check("33 充值流水查询 200", r.status_code == 200 and len(r.json()) == 1, r.status_code)

    phone_low = "137" + suffix[-8:]
    jpost("/api/register", {"phone": phone_low, "password": "low123456", "nickname": "低额用户"})
    r = jpost("/api/login", {"phone": phone_low, "password": "low123456"})
    token_low = r.json()["token"]
    r = jpost("/api/recharge", {"amount": "10.00", "order_no": "LOW" + suffix}, token=token_low)
    check("34 低额充值成功", r.status_code == 200, r.status_code)
    r = c.get("/api/notifications", HTTP_AUTHORIZATION=f"Token {token_low}")
    check("35 余额低于50触发站内信", r.status_code == 200 and any("余额" in n["title"] for n in r.json()), r.status_code)

    # ============ 五、站内信 / 报表 ============
    r = c.get("/api/notifications", HTTP_AUTHORIZATION=f"Token {token_c}")
    check("36 审核结果写入站内信", r.status_code == 200 and any("审核" in n["title"] for n in r.json()), r.status_code)
    r = c.get("/api/report", HTTP_AUTHORIZATION=f"Token {token_c}")
    check("37 报表统计 200", r.status_code == 200 and r.json()["impression_count"] >= 1 and r.json()["click_count"] >= 2, r.json())

finally:
    # 仅删除本次新增的账号，级联清理其全部关联数据
    current_ids = set(ClientModel.objects.values_list("client_id", flat=True))
    new_ids = current_ids - baseline_ids
    if new_ids:
        ClientModel.objects.filter(client_id__in=new_ids).delete()
    print(f"\n[cleanup] 已清理本次新增账号 {len(new_ids)} 个")

print("\n" + "=" * 64)
passed = sum(1 for _, ok, _ in results if ok)
print(f"RESULT: {passed}/{len(results)} PASSED")
for name, ok, detail in results:
    if not ok:
        print("FAILED:", name, "|", detail)
sys.exit(0 if passed == len(results) else 1)
