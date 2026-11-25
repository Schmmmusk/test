# 基于 Web 的互联网广告平台系统

软件工程课程第四组贯穿项目。系统采用前后端分离架构，覆盖广告客户从注册充值、创建广告、平台审核、投放计费到数据报表的完整闭环，并对外提供广告拉取与曝光/点击回传接口。

## 一、技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3.5 + Vue Router 4 + Pinia 2 + Axios 1 + Element Plus 2 + ECharts 5 + Vite 5 |
| 后端 | Django 5.2 + Django REST Framework + django-cors-headers |
| 数据库 | MySQL 8.0（PyMySQL 驱动） |
| 鉴权 | 用户接口 Token 鉴权；对外接口 Api-Key 鉴权 |

## 二、目录结构

```
.
├── backend/                     Django 后端
│   ├── adplatform/              项目配置（settings / urls / wsgi）
│   ├── users/                   用户、注册登录、站内信、权限
│   ├── ads/                     广告模型、列表与创建、对外拉广告
│   ├── audit/                   待审核列表、通过、驳回
│   ├── recharge/                充值与流水
│   ├── api/                     对外事件回传（曝光/点击）
│   ├── report/                  数据报表汇总
│   ├── tests/                   端到端测试脚本
│   └── requirements.txt
├── frontend/ad-platform-frontend/  Vue 3 前端
│   └── src/
│       ├── api/                 axios 封装与接口定义
│       ├── router/              路由与权限守卫
│       ├── stores/              Pinia 用户状态
│       ├── layouts/             主布局
│       ├── views/               8 个业务页面
│       └── utils/               格式化工具
├── docs/                        课程实验文档（SRS、设计说明书、接口文档等）
├── output/api-doc-20261124/     后端 API 对接文档（md / html / docx）
├── 联调记录.md                   前后端联调记录
└── LICENSE
```

## 三、环境准备

| 软件 | 版本要求 |
|------|----------|
| Python | 3.11 / 3.12 |
| Node.js | 20.x LTS 及以上（实测 22.22.2 可用） |
| MySQL | 8.0 |

后端 Python 依赖：

```powershell
cd ".\backend"
.\.venv\Scripts\pip.exe install -r requirements.txt
```

前端依赖（若 node_modules 缺失）：

```powershell
cd ".\frontend\ad-platform-frontend"
npm install
```

数据库配置通过环境变量注入，未设置时使用 settings.py 中的开发默认值：

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `DB_NAME` | 数据库名 | `ad_platform` |
| `DB_USER` | 用户名 | `aduser` |
| `DB_PASSWORD` | 密码 | 见 settings.py（开发环境） |
| `DB_HOST` | 主机 | `127.0.0.1` |
| `DB_PORT` | 端口 | `3306` |

> 生产部署务必设置 `DJANGO_SECRET_KEY`、`PARTNER_API_KEY` 与数据库环境变量，不要沿用开发默认值。

## 四、启动方式

**1. 后端**（在 `backend` 目录执行）

```powershell
cd ".\backend"
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

**2. 前端**（在 `D:\软件工程作业\frontend\ad-platform-frontend` 目录执行）

```powershell
cd ".\frontend\ad-platform-frontend"
npm run dev
```

浏览器打开 `http://localhost:5173`。后端生产构建用 `npm run build`，产物在 `dist/`。

## 五、账号与鉴权

| 角色 | 获取方式 |
|------|----------|
| 普通客户 | 通过 `/register` 页面自助注册 |
| 管理员 | 客户注册后由后端将 `client.is_admin` 置为 1；可用 `backend/tests/set_admin.py <手机号>` 快速设置 |

鉴权约定：

- 用户接口：请求头 `Authorization: Token <登录返回的 token>`，前端自动注入并持久化到 localStorage。
- 对外接口：请求头 `Api-Key: <PARTNER_API_KEY>`，注意用连字符形式，勿写成 `api_key`。
- `GET /api/ads`（对外拉广告）与 `POST /api/ads`（新建广告）为同一路径不同语义，前端查本人广告用 `GET /api/client/ads`。

## 六、接口概览

共 13 个接口，完整规格见 `output/api-doc-20261124/stage1/final_draft.md`。

| 类别 | 接口 |
|------|------|
| 用户 | 注册、登录、我的广告、新建广告、充值、充值流水、站内信、数据报表 |
| 管理员 | 待审核列表、审核通过、审核驳回 |
| 对外 | 拉取可投放广告（Api-Key）、曝光/点击回传（Api-Key） |

响应约定：统一 JSON / UTF-8；时间为 ISO 8601；金额为字符串（如 `"200.00"`），前端展示时转 Number；广告状态为英文枚举 `pending` / `approved` / `rejected` / `paused`。

## 七、测试

后端端到端脚本（覆盖全部 13 个接口与鉴权边界）：

```bash
bash "./backend/tests/curl_test_final.sh"
```

详细联调过程、CORS 问题排查与事件回传实测见 `联调记录.md`。

## 八、补充说明

- 前端未实现素材上传、受众标签、密码找回（后端无对应接口，按 MVP 裁剪）。
- 站内信标记已读由前端 localStorage 本地维护，后端无该接口。
- 数据报表为累计汇总，无时间筛选参数。
- 课程实验一、实验二的 SRS、架构设计、接口设计等文档在 `docs/` 目录。
