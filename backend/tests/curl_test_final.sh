#!/bin/bash
# ============================================================
# 广告平台后端 API —— 最终测试命令集（可直接执行）
# ------------------------------------------------------------
# 执行方式（在任意目录）：
#   bash "D:/软件工程作业/backend/tests/curl_test_final.sh"
#
# 编码说明：
#   请求体中文一律用 \uXXXX 转义（纯 ASCII），彻底避免 Windows 终端
#   GB2312/GBK 编码问题。脚本内显式设置 UTF-8 locale 作双保险
#   （bash script.sh 是非交互式 shell，不读取 ~/.bashrc）。
#
# 鉴权说明：
#   对外接口用 Api-Key 头（连字符）。Django runserver 会剥离带下划线的
#   header，api_key 写法不可用。
# ============================================================

export LANG=C.UTF-8
export LC_ALL=C.UTF-8

BASE=http://127.0.0.1:8000
KEY=test-api-key-2026
PY="D:/软件工程作业/backend/.venv/Scripts/python.exe"
ADMIN_SCRIPT="D:/软件工程作业/backend/tests/set_admin.py"

PHONE_C=13800000001
PHONE_A=13900000001
ORDER_NO="CURL$(date +%s)"

req() {
  local name="$1"; shift
  echo "----- $name"
  curl -s -w "       [HTTP %{http_code}]\n" "$@"
}

die() {
  echo ""
  echo "!!!!! 测试中止：$1"
  echo "!!!!! 常见原因：后端服务未监听 127.0.0.1:8000、MySQL 未运行。"
  exit 1
}

# 清理上次运行的测试账号，保证可重复执行
"$PY" -c "
import pymysql
c=pymysql.connect(host='127.0.0.1',user='aduser',password='AdPlatform_2026',database='ad_platform',charset='utf8mb4')
with c.cursor() as cur:
    cur.execute(\"SELECT client_id FROM client WHERE phone IN ('$PHONE_C','$PHONE_A')\")
    ids=[r[0] for r in cur.fetchall()]
    if ids:
        ph=','.join(['%s']*len(ids))
        for t,col in [('impression','client_id'),('notification','client_id'),('recharge','client_id'),('ad','client_id'),('authtoken_token','user_id')]:
            cur.execute(f'DELETE FROM {t} WHERE {col} IN ({ph})', ids)
        cur.execute(f'DELETE FROM client WHERE client_id IN ({ph})', ids)
    c.commit()
c.close()
" || die "清理历史账号失败（检查 MySQL 连接）"
echo "[准备] 已清理历史测试账号"
echo ""

echo "==================== 1. 注册 ===================="
R1=$(curl -s -w "|%{http_code}" -X POST "$BASE/api/register" \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800000001","password":"test123456","nickname":"\u5ba2\u6237"}')
echo "注册客户: $R1"
echo "$R1" | grep -q '|201$' || die "客户注册失败"

R2=$(curl -s -w "|%{http_code}" -X POST "$BASE/api/register" \
  -H "Content-Type: application/json" \
  -d '{"phone":"13900000001","password":"admin123456","nickname":"\u7ba1\u7406\u5458"}')
echo "注册管理员: $R2"
echo "$R2" | grep -q '|201$' || die "管理员注册失败"

echo "==================== 2. 标记管理员 ===================="
"$PY" "$ADMIN_SCRIPT" "$PHONE_A" || die "标记管理员失败"

echo "==================== 3. 登录取 token ===================="
LOGIN_C=$(curl -s -X POST "$BASE/api/login" -H "Content-Type: application/json" \
  -d '{"phone":"13800000001","password":"test123456"}')
LOGIN_A=$(curl -s -X POST "$BASE/api/login" -H "Content-Type: application/json" \
  -d '{"phone":"13900000001","password":"admin123456"}')
TC=$(echo "$LOGIN_C" | "$PY" -c "import sys,json;print(json.load(sys.stdin)['token'])" 2>/dev/null) || die "客户登录失败：$LOGIN_C"
TA=$(echo "$LOGIN_A" | "$PY" -c "import sys,json;print(json.load(sys.stdin)['token'])" 2>/dev/null) || die "管理员登录失败：$LOGIN_A"
echo "客户 token:    ${TC:0:12}..."
echo "管理员 token:  ${TA:0:12}..."

echo "==================== 4. 鉴权边界 ===================="
req "无 Token 访问（期望 401）" "$BASE/api/client/ads"
req "错误 Token（期望 401）" "$BASE/api/client/ads" -H "Authorization: Token wrong"
req "对外拉广告无 Key（期望 401）" "$BASE/api/ads"
req "对外拉广告错 Key（期望 401）" "$BASE/api/ads" -H "Api-Key: wrong"

echo "==================== 5. 广告与审核 ===================="
REQ_AD=$(curl -s -w "|%{http_code}" -X POST "$BASE/api/ads" \
  -H "Content-Type: application/json" -H "Authorization: Token $TC" \
  -d '{"title":"\u6d4b\u8bd5\u5e7f\u544a","content":"\u6587\u6848","image_url":"http://x/i.png","landing_url":"http://x","daily_budget":"100.00"}')
echo "新建广告: $REQ_AD"
echo "$REQ_AD" | grep -q '|201$' || die "新建广告失败"

req "客户广告列表（期望 200）" "$BASE/api/client/ads" -H "Authorization: Token $TC"
req "管理员待审核列表（期望 200）" "$BASE/api/audit/pending" -H "Authorization: Token $TA"
req "非管理员访问审核（期望 403）" "$BASE/api/audit/pending" -H "Authorization: Token $TC"
req "对外拉广告-空池（期望 200 []）" "$BASE/api/ads" -H "Api-Key: $KEY"

AD_ID=$("$PY" -c "
import pymysql
c=pymysql.connect(host='127.0.0.1',user='aduser',password='AdPlatform_2026',database='ad_platform')
with c.cursor() as cur:
    cur.execute(\"SELECT ad_id FROM ad WHERE title='测试广告' ORDER BY ad_id DESC LIMIT 1\")
    row=cur.fetchone(); print(row[0] if row else 0)
c.close()
")
[ "$AD_ID" != "0" ] || die "未找到本次广告"
echo "本次广告 ID = $AD_ID"

req "审核通过（期望 200）" -X POST "$BASE/api/audit/$AD_ID/pass" -H "Authorization: Token $TA"
req "对外拉广告-已进池（期望 200 可见）" "$BASE/api/ads" -H "Api-Key: $KEY"

echo "==================== 6. 回传与计费 ===================="
req "曝光回传（期望 201）" -X POST "$BASE/api/track" \
  -H "Content-Type: application/json" -H "Api-Key: $KEY" \
  -d "{\"ad_id\":$AD_ID,\"event_type\":\"impression\",\"source\":\"curl\"}"
req "点击回传（期望 201）" -X POST "$BASE/api/track" \
  -H "Content-Type: application/json" -H "Api-Key: $KEY" \
  -d "{\"ad_id\":$AD_ID,\"event_type\":\"click\",\"source\":\"curl\"}"
req "回传错 Key（期望 401）" -X POST "$BASE/api/track" \
  -H "Content-Type: application/json" -H "Api-Key: wrong" \
  -d "{\"ad_id\":$AD_ID,\"event_type\":\"click\"}"

echo "==================== 7. 充值与流水 ===================="
req "充值 200 元（期望 200）" -X POST "$BASE/api/recharge" \
  -H "Content-Type: application/json" -H "Authorization: Token $TC" \
  -d "{\"amount\":\"200.00\",\"order_no\":\"$ORDER_NO\"}"
req "充值流水（期望 200）" "$BASE/api/recharges" -H "Authorization: Token $TC"

echo "==================== 8. 站内信与报表 ===================="
req "站内信（期望 200）" "$BASE/api/notifications" -H "Authorization: Token $TC"
req "数据报表（期望 200）" "$BASE/api/report" -H "Authorization: Token $TC"

echo "==================== 9. 消耗核对（期望 spent = 0.01）===================="
"$PY" -c "
import pymysql
c=pymysql.connect(host='127.0.0.1',user='aduser',password='AdPlatform_2026',database='ad_platform')
with c.cursor() as cur:
    cur.execute('SELECT spent FROM ad WHERE ad_id=$AD_ID')
    row=cur.fetchone()
    print('spent =', row[0] if row else 'NULL')
c.close()
"

echo ""
echo "==================== 测试完成 ===================="
