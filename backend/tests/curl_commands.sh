#!/bin/bash
# 广告平台 API curl 测试命令集（Git Bash 可直接执行）
# 服务地址：http://127.0.0.1:8000
# 中文用 \uXXXX 转义，避免 Windows 终端 GB2312 编码问题

BASE=http://127.0.0.1:8000
KEY=test-api-key-2026
PY="D:/软件工程作业/backend/.venv/Scripts/python.exe"
ADMIN_SCRIPT="D:/软件工程作业/backend/tests/set_admin.py"

PHONE_C=13800000001
PHONE_A=13900000001

echo "==================== 1. 注册 ===================="
curl -s -w " [%{http_code}]\n" -X POST "$BASE/api/register" \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800000001","password":"test123456","nickname":"\u5ba2\u6237"}'

curl -s -w " [%{http_code}]\n" -X POST "$BASE/api/register" \
  -H "Content-Type: application/json" \
  -d '{"phone":"13900000001","password":"admin123456","nickname":"\u7ba1\u7406\u5458"}'

echo "==================== 2. 标记管理员 ===================="
"$PY" "$ADMIN_SCRIPT" "$PHONE_A"

echo "==================== 3. 登录取 token ===================="
LOGIN_C=$(curl -s -X POST "$BASE/api/login" -H "Content-Type: application/json" \
  -d '{"phone":"13800000001","password":"test123456"}')
LOGIN_A=$(curl -s -X POST "$BASE/api/login" -H "Content-Type: application/json" \
  -d '{"phone":"13900000001","password":"admin123456"}')
TC=$(echo "$LOGIN_C" | "$PY" -c "import sys,json;print(json.load(sys.stdin)['token'])")
TA=$(echo "$LOGIN_A" | "$PY" -c "import sys,json;print(json.load(sys.stdin)['token'])")
echo "客户 token: ${TC:0:12}...   管理员 token: ${TA:0:12}..."

echo "==================== 4. 鉴权边界 ===================="
echo "-- 无 Token 访问 client/ads（期望 401）"
curl -s -w " [%{http_code}]\n" "$BASE/api/client/ads"
echo "-- 错误 Token（期望 401）"
curl -s -w " [%{http_code}]\n" "$BASE/api/client/ads" -H "Authorization: Token wrong"

echo "==================== 5. 广告与审核 ===================="
echo "-- 客户创建广告（期望 201，记录 ad_id）"
curl -s -w " [%{http_code}]\n" -X POST "$BASE/api/ads" \
  -H "Content-Type: application/json" -H "Authorization: Token $TC" \
  -d '{"title":"\u6d4b\u8bd5\u5e7f\u544a","content":"\u6587\u6848","image_url":"http://x/i.png","landing_url":"http://x","daily_budget":"100.00"}'
echo "-- 客户广告列表"
curl -s -w " [%{http_code}]\n" "$BASE/api/client/ads" -H "Authorization: Token $TC"
echo "-- 管理员待审核列表"
curl -s -w " [%{http_code}]\n" "$BASE/api/audit/pending" -H "Authorization: Token $TA"
echo "-- 对外拉广告（审核前应为空池 []）"
curl -s -w " [%{http_code}]\n" "$BASE/api/ads" -H "Api-Key: $KEY"

AD_ID=$("$PY" -c "
import pymysql
c=pymysql.connect(host='127.0.0.1',user='aduser',password='AdPlatform_2026',database='ad_platform')
with c.cursor() as cur:
    cur.execute(\"SELECT ad_id FROM ad WHERE title='测试广告' ORDER BY ad_id DESC LIMIT 1\")
    row=cur.fetchone()
    print(row[0] if row else 0)
c.close()
")
echo "本次广告 ID = $AD_ID"

echo "-- 审核通过"
curl -s -w " [%{http_code}]\n" -X POST "$BASE/api/audit/$AD_ID/pass" -H "Authorization: Token $TA"
echo "-- 对外拉广告（通过后应可见）"
curl -s -w " [%{http_code}]\n" "$BASE/api/ads" -H "Api-Key: $KEY"

echo "==================== 6. 回传与计费 ===================="
echo "-- 曝光回传"
curl -s -w " [%{http_code}]\n" -X POST "$BASE/api/track" \
  -H "Content-Type: application/json" -H "Api-Key: $KEY" \
  -d "{\"ad_id\":$AD_ID,\"event_type\":\"impression\",\"source\":\"curl\"}"
echo "-- 点击回传"
curl -s -w " [%{http_code}]\n" -X POST "$BASE/api/track" \
  -H "Content-Type: application/json" -H "Api-Key: $KEY" \
  -d "{\"ad_id\":$AD_ID,\"event_type\":\"click\",\"source\":\"curl\"}"
echo "-- 错误 Key（期望 401）"
curl -s -w " [%{http_code}]\n" "$BASE/api/ads" -H "Api-Key: wrong"

echo "==================== 7. 充值与流水 ===================="
curl -s -w " [%{http_code}]\n" -X POST "$BASE/api/recharge" \
  -H "Content-Type: application/json" -H "Authorization: Token $TC" \
  -d '{"amount":"200.00","order_no":"CURL001"}'
curl -s -w " [%{http_code}]\n" "$BASE/api/recharges" -H "Authorization: Token $TC"

echo "==================== 8. 站内信与报表 ===================="
curl -s -w " [%{http_code}]\n" "$BASE/api/notifications" -H "Authorization: Token $TC"
curl -s -w " [%{http_code}]\n" "$BASE/api/report" -H "Authorization: Token $TC"

echo "==================== 9. 消耗核对（期望 0.01）===================="
"$PY" -c "
import pymysql
c=pymysql.connect(host='127.0.0.1',user='aduser',password='AdPlatform_2026',database='ad_platform')
with c.cursor() as cur:
    cur.execute('SELECT spent FROM ad WHERE ad_id=$AD_ID')
    print('spent =', cur.fetchone()[0])
c.close()
"
