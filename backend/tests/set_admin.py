# -*- coding: utf-8 -*-
"""测试准备：把指定手机号的客户标记为管理员。

用法（在任意目录）：
    D:/软件工程作业/backend/.venv/Scripts/python.exe D:/软件工程作业/backend/tests/set_admin.py 13900000001

从命令行参数读取手机号，避免 shell 引号嵌套问题。
"""
import sys
import pymysql

if len(sys.argv) != 2:
    print("用法: python set_admin.py <手机号>")
    sys.exit(1)

phone = sys.argv[1]
c = pymysql.connect(
    host="127.0.0.1", user="aduser", password="AdPlatform_2026",
    database="ad_platform", charset="utf8mb4",
)
with c.cursor() as cur:
    cur.execute("UPDATE client SET is_admin=1 WHERE phone=%s", (phone,))
    affected = cur.rowcount
c.commit()
c.close()
print(f"已标记管理员: phone={phone}, 影响行数={affected}")
