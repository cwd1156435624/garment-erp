# ERP系统

一个基于Django的企业资源规划(ERP)系统，集成了用户管理、生产管理、仓储物流、财务管理、供应商管理、客户管理、设备管理和员工管理等功能模块，以及报表、结算、扫码和搜索等增强功能。

## 技术栈

- 后端：Django 4.2 + Django REST Framework
- 数据库：PostgreSQL
- 缓存：Redis
- 任务队列：Celery
- 监控：Prometheus
- 前端：React (前端代码在frontend目录)
- API文档：drf-yasg (Swagger/ReDoc)
- 认证：JWT (djangorestframework-simplejwt)
- 历史记录：django-simple-history

## 功能模块

- 用户管理：用户认证、权限控制
- 生产管理：生产计划、生产进度跟踪、生产异常处理、裁剪任务管理
- 仓储物流：库存管理、物流跟踪
- 财务管理：财务报表、成本核算、支付管理
- 供应商管理：供应商信息、采购管理
- 客户管理：客户信息、订单管理
- 设备管理：设备信息、维护记录
- 员工管理：员工信息、考勤管理
- 系统设置：系统参数配置、日志查询
- 报表模块：生产报表、库存报表、成本报表、报表模板
- 结算模块：结算单据、对账管理
- 扫码模块：条码管理、扫码操作（入库、出库、生产过程、包装）
- 搜索模块：全局搜索、搜索建议、高级搜索
- 物料管理：物料信息、库存位置、采购需求、采购订单
- 系统公告：公告发布、阅读状态跟踪、公告范围控制
- 开发者控制台：系统监控、API指标、系统日志、配置管理、WebSocket会话管理

## 安装与运行

### 环境要求

- Python 3.11+
- PostgreSQL 14+
- Redis 5+

### 前后端通信配置

#### CORS配置

后端已经配置了CORS支持，允许前端应用访问后端 API。主要配置如下：

- 已启用 `corsheaders` 中间件
- 允许所有来源的请求（开发环境）
- 支持带凭证的请求
- 白名单包含开发服务器和生产服务器地址

#### API请求设置

前端应用使用 Axios 进行 API 请求，默认配置如下：

- API基础URL：`https://yagtpotihswf.sealosbja.site/api`
- 请求拦截器会自动添加JWT认证令牌
- 响应拦截器处理401未授权错误，自动重定向到登录页面
- 支持开发环境下使用模拟数据

### 安装依赖

```bash
pip install -r requirements.txt
```

### 数据库迁移

```bash
python manage.py migrate
```

### 创建超级用户

```bash
python manage.py createsuperuser
```

### 运行开发服务器

```bash
python manage.py runserver
```

## API文档

系统提供了Swagger和ReDoc两种API文档格式：

- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## API端点

系统提供以下主要API端点：

- `/api/users/` - 用户管理
- `/api/production/` - 生产管理
- `/api/warehouse/` - 仓储物流
- `/api/finance/` - 财务管理
- `/api/supplier/` - 供应商管理
- `/api/customer/` - 客户管理
- `/api/equipment/` - 设备管理
- `/api/employee/` - 员工管理
- `/api/system/` - 系统设置
- `/api/reports/` - 报表模块
- `/api/settlement/` - 结算模块
- `/api/scanning/` - 扫码模块
- `/api/search/` - 搜索模块
- `/api/materials/` - 物料管理
- `/api/system/notices/` - 系统公告
- `/api/developer/` - 开发者控制台

## 监控

系统集成了Prometheus监控，可以通过以下方式访问监控指标：

- 监控指标接口: `/api/system/metrics/`

### 监控指标

系统提供以下监控指标：

- HTTP请求计数：按方法、路径和状态码统计
- HTTP请求延迟：按方法和路径统计
- 活跃请求数：按方法统计
- 系统内存使用情况：总内存、可用内存、已用内存
- 系统CPU使用率
- 系统磁盘使用情况：按挂载点统计总空间、已用空间、可用空间

## 开发者控制台

系统提供了开发者控制台功能，用于系统监控、调试和配置管理：

- 系统监控：`/api/developer/system-monitor/` - 实时监控系统资源使用情况
- API指标：`/api/developer/api-metrics/` - 跟踪API调用频率、响应时间等指标
- 系统日志：`/api/developer/system-logs/` - 查看系统日志记录
- 配置管理：`/api/developer/config/` - 管理系统配置项
- WebSocket会话：`/api/developer/websocket-sessions/` - 管理WebSocket会话
- WebSocket消息：`/api/developer/websocket-messages/` - 查看WebSocket消息记录

## 系统公告

系统提供了公告管理功能，用于发布和管理系统公告：

- 公告列表：`/api/system/notices/` - 获取所有公告
- 未读公告：`/api/system/notices/unread/` - 获取未读公告
- 有效公告：`/api/system/notices/active/` - 获取当前有效的公告
- 标记已读：`/api/system/notices/{id}/mark_as_read/` - 标记公告为已读

## 部署

### 使用Gunicorn

```bash
gunicorn project.wsgi_prometheus:application --workers 4 --bind 0.0.0.0:8000
```

### 使用Docker

```bash
docker build -t erp-system .
docker run -p 8000:8000 erp-system
```

## 许可证

本项目采用MIT许可证。详见LICENSE文件。