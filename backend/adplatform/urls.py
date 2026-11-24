"""后端 API 根路由。

路径与《07_接口文档》《01_软件设计说明书》保持一致：
  POST /api/register               注册
  POST /api/login                  登录
  GET  /api/client/ads             前端-广告列表（拆分后的独立路径）
  GET  /api/ads                    对外-合作网站拉广告（API Key）
  POST /api/ads                    前端-新建广告并送审（Token）
  POST /api/track                  对外-曝光点击回传（API Key）
  POST /api/recharge               充值
  GET  /api/recharges              充值流水
  GET  /api/audit/pending          管理员-待审核列表
  POST /api/audit/<id>/pass        审核通过
  POST /api/audit/<id>/reject      审核驳回
  GET  /api/notifications          站内信
  GET  /api/report                 数据报表
"""
from django.urls import include, path

urlpatterns = [
    path("api/", include("users.urls")),
    path("api/", include("ads.urls")),
    path("api/", include("audit.urls")),
    path("api/", include("recharge.urls")),
    path("api/", include("api.urls")),
    path("api/", include("report.urls")),
]
