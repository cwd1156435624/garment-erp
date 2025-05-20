# 前端API接口清单-第1部分

本文档详细描述了首页模块和系统管理模块的API接口。

## 一、首页模块 (Home)

### 1. 系统公告子模块

#### 1.1 获取系统公告列表

**请求**：
```http
GET /notices/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `is_active`: 是否激活，可选值：true/false

**响应**：
```json
{
  "count": 15,
  "next": "https://yagtpotihswf.sealosbja.site/api/notices/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "系统升级通知",
      "content": "系统将于2025年4月10日进行升级维护，请提前做好准备。",
      "is_active": true,
      "priority": "high",
      "created_at": "2025-04-01T08:00:00Z",
      "updated_at": "2025-04-01T08:00:00Z"
    },
    // 更多公告...
  ]
}
```

#### 1.2 获取单个系统公告

**请求**：
```http
GET /notices/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "id": 1,
  "title": "系统升级通知",
  "content": "系统将于2025年4月10日进行升级维护，请提前做好准备。",
  "is_active": true,
  "priority": "high",
  "created_at": "2025-04-01T08:00:00Z",
  "updated_at": "2025-04-01T08:00:00Z"
}
```

### 2. 数据概览子模块

#### 2.1 获取订单统计数据

**请求**：
```http
GET /orders/stats/
Authorization: Bearer <your_token>
```

**参数**：
- `period`: 统计周期，可选值：day/week/month/year，默认为day

**响应**：
```json
{
  "total_orders": 256,
  "completed_orders": 198,
  "pending_orders": 45,
  "delayed_orders": 13,
  "total_amount": 1256800.50,
  "period_data": [
    {
      "date": "2025-04-01",
      "orders_count": 12,
      "orders_amount": 45600.00
    },
    // 更多日期数据...
  ]
}
```

#### 2.2 获取物料统计数据

**请求**：
```http
GET /materials/stats/
Authorization: Bearer <your_token>
```

**参数**：
- `period`: 统计周期，可选值：day/week/month/year，默认为day

**响应**：
```json
{
  "total_materials": 1256,
  "low_stock_materials": 45,
  "out_of_stock_materials": 13,
  "total_value": 856800.50,
  "period_data": [
    {
      "date": "2025-04-01",
      "materials_count": 1256,
      "materials_value": 856800.50
    },
    // 更多日期数据...
  ]
}
```

### 3. 待发货订单子模块

#### 3.1 获取待发货订单列表

**请求**：
```http
GET /orders/pending-delivery/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `sort_by`: 排序字段，可选值：created_at/delivery_date/priority
- `sort_order`: 排序方向，可选值：asc/desc

**响应**：
```json
{
  "count": 45,
  "next": "https://yagtpotihswf.sealosbja.site/api/orders/pending-delivery/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "order_number": "ORD20250401001",
      "customer_name": "客户名称",
      "product_name": "产品名称",
      "quantity": 100,
      "delivery_date": "2025-04-15",
      "priority": "high",
      "status": "ready_for_delivery",
      "created_at": "2025-04-01T08:00:00Z"
    },
    // 更多订单...
  ]
}
```

### 4. 预警信息子模块

#### 4.1 获取预警信息列表

**请求**：
```http
GET /alerts/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `type`: 预警类型，可选值：material/order/production/quality
- `severity`: 严重程度，可选值：low/medium/high/critical

**响应**：
```json
{
  "count": 13,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "type": "material",
      "title": "物料库存不足",
      "content": "布料A12345库存低于安全库存，请及时补充。",
      "severity": "high",
      "is_resolved": false,
      "created_at": "2025-04-05T10:30:00Z",
      "updated_at": "2025-04-05T10:30:00Z"
    },
    // 更多预警...
  ]
}
```

#### 4.2 获取单个预警信息

**请求**：
```http
GET /alerts/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "id": 1,
  "type": "material",
  "title": "物料库存不足",
  "content": "布料A12345库存低于安全库存，请及时补充。",
  "severity": "high",
  "is_resolved": false,
  "related_item": {
    "id": 123,
    "type": "material",
    "name": "布料A12345",
    "current_stock": 50,
    "safety_stock": 100
  },
  "created_at": "2025-04-05T10:30:00Z",
  "updated_at": "2025-04-05T10:30:00Z"
}
```

#### 4.3 标记预警为已解决

**请求**：
```http
PATCH /alerts/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "is_resolved": true,
  "resolution_note": "已补充物料库存"
}
```

**响应**：
```json
{
  "id": 1,
  "type": "material",
  "title": "物料库存不足",
  "content": "布料A12345库存低于安全库存，请及时补充。",
  "severity": "high",
  "is_resolved": true,
  "resolution_note": "已补充物料库存",
  "resolved_at": "2025-04-07T14:30:00Z",
  "created_at": "2025-04-05T10:30:00Z",
  "updated_at": "2025-04-07T14:30:00Z"
}
```

## 二、系统管理模块 (System)

### 1. 配置管理子模块

#### 1.1 获取系统配置

**请求**：
```http
GET /system/config/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "company_name": "样衣工序流程管理系统",
  "logo_url": "https://yagtpotihswf.sealosbja.site/api/media/system/logo.png",
  "theme": "dark",
  "default_language": "zh-CN",
  "notification_settings": {
    "email_notifications": true,
    "sms_notifications": false,
    "system_notifications": true
  },
  "modules": [
    {
      "id": "home",
      "name": "首页",
      "is_enabled": true
    },
    {
      "id": "production",
      "name": "生产管理",
      "is_enabled": true
    },
    // 更多模块...
  ]
}
```

#### 1.2 更新系统配置

**请求**：
```http
PATCH /system/config/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "theme": "light",
  "notification_settings": {
    "email_notifications": false
  }
}
```

**响应**：
```json
{
  "company_name": "样衣工序流程管理系统",
  "logo_url": "https://yagtpotihswf.sealosbja.site/api/media/system/logo.png",
  "theme": "light",
  "default_language": "zh-CN",
  "notification_settings": {
    "email_notifications": false,
    "sms_notifications": false,
    "system_notifications": true
  },
  "modules": [
    {
      "id": "home",
      "name": "首页",
      "is_enabled": true
    },
    {
      "id": "production",
      "name": "生产管理",
      "is_enabled": true
    },
    // 更多模块...
  ]
}
```

### 2. 用户管理子模块

#### 2.1 获取用户列表

**请求**：
```http
GET /users/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `search`: 搜索关键词，支持用户名、姓名、邮箱
- `role`: 角色ID
- `is_active`: 是否激活，可选值：true/false

**响应**：
```json
{
  "count": 56,
  "next": "https://yagtpotihswf.sealosbja.site/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "first_name": "管理员",
      "last_name": "",
      "role": {
        "id": 1,
        "name": "系统管理员"
      },
      "is_active": true,
      "last_login": "2025-04-07T08:30:00Z",
      "date_joined": "2025-01-01T00:00:00Z"
    },
    // 更多用户...
  ]
}
```

#### 2.2 获取单个用户信息

**请求**：
```http
GET /users/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "管理员",
  "last_name": "",
  "role": {
    "id": 1,
    "name": "系统管理员",
    "permissions": [
      "view_all",
      "edit_all",
      "delete_all",
      "manage_users",
      "manage_roles"
    ]
  },
  "department": {
    "id": 1,
    "name": "管理部"
  },
  "phone": "13800138000",
  "is_active": true,
  "last_login": "2025-04-07T08:30:00Z",
  "date_joined": "2025-01-01T00:00:00Z"
}
```

#### 2.3 创建用户

**请求**：
```http
POST /users/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepassword",
  "first_name": "新",
  "last_name": "用户",
  "role_id": 2,
  "department_id": 3,
  "phone": "13900139000",
  "is_active": true
}
```

**响应**：
```json
{
  "id": 57,
  "username": "newuser",
  "email": "newuser@example.com",
  "first_name": "新",
  "last_name": "用户",
  "role": {
    "id": 2,
    "name": "生产管理员"
  },
  "department": {
    "id": 3,
    "name": "生产部"
  },
  "phone": "13900139000",
  "is_active": true,
  "date_joined": "2025-04-07T14:35:00Z"
}
```

#### 2.4 更新用户信息

**请求**：
```http
PUT /users/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "email": "updated@example.com",
  "first_name": "已更新",
  "role_id": 3
}
```

**响应**：
```json
{
  "id": 57,
  "username": "newuser",
  "email": "updated@example.com",
  "first_name": "已更新",
  "last_name": "用户",
  "role": {
    "id": 3,
    "name": "物料管理员"
  },
  "department": {
    "id": 3,
    "name": "生产部"
  },
  "phone": "13900139000",
  "is_active": true,
  "last_login": null,
  "date_joined": "2025-04-07T14:35:00Z"
}
```

#### 2.5 删除用户

**请求**：
```http
DELETE /users/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```
204 No Content
```

#### 2.6 获取待审核用户列表

**请求**：
```http
GET /users/pending/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 58,
      "username": "pendinguser1",
      "email": "pending1@example.com",
      "first_name": "待审核",
      "last_name": "用户1",
      "registration_date": "2025-04-06T10:20:00Z"
    },
    // 更多待审核用户...
  ]
}
```

#### 2.7 审核用户

**请求**：
```http
POST /users/{id}/approve/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "approved": true,
  "role_id": 4,
  "department_id": 2
}
```

**响应**：
```json
{
  "id": 58,
  "username": "pendinguser1",
  "email": "pending1@example.com",
  "first_name": "待审核",
  "last_name": "用户1",
  "role": {
    "id": 4,
    "name": "普通用户"
  },
  "department": {
    "id": 2,
    "name": "设计部"
  },
  "is_active": true,
  "approved_by": {
    "id": 1,
    "username": "admin"
  },
  "approved_at": "2025-04-07T14:36:00Z"
}
```

### 3. 角色权限子模块

#### 3.1 获取角色列表

**请求**：
```http
GET /roles/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "系统管理员",
      "description": "拥有系统所有权限",
      "user_count": 2,
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "生产管理员",
      "description": "管理生产相关功能",
      "user_count": 5,
      "created_at": "2025-01-01T00:00:00Z"
    },
    // 更多角色...
  ]
}
```

#### 3.2 获取单个角色详情

**请求**：
```http
GET /roles/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "id": 1,
  "name": "系统管理员",
  "description": "拥有系统所有权限",
  "permissions": [
    {
      "id": 1,
      "code": "view_all",
      "name": "查看所有",
      "description": "可以查看系统中的所有内容"
    },
    {
      "id": 2,
      "code": "edit_all",
      "name": "编辑所有",
      "description": "可以编辑系统中的所有内容"
    },
    // 更多权限...
  ],
  "user_count": 2,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

#### 3.3 创建角色

**请求**：
```http
POST /roles/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "name": "质检员",
  "description": "负责产品质量检查",
  "permission_ids": [1, 5, 8, 12]
}
```

**响应**：
```json
{
  "id": 6,
  "name": "质检员",
  "description": "负责产品质量检查",
  "permissions": [
    {
      "id": 1,
      "code": "view_all",
      "name": "查看所有",
      "description": "可以查看系统中的所有内容"
    },
    // 更多权限...
  ],
  "user_count": 0,
  "created_at": "2025-04-07T14:37:00Z",
  "updated_at": "2025-04-07T14:37:00Z"
}
```

#### 3.4 更新角色

**请求**：
```http
PUT /roles/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "name": "高级质检员",
  "permission_ids": [1, 5, 8, 12, 15]
}
```

**响应**：
```json
{
  "id": 6,
  "name": "高级质检员",
  "description": "负责产品质量检查",
  "permissions": [
    {
      "id": 1,
      "code": "view_all",
      "name": "查看所有",
      "description": "可以查看系统中的所有内容"
    },
    // 更多权限...
  ],
  "user_count": 0,
  "created_at": "2025-04-07T14:37:00Z",
  "updated_at": "2025-04-07T14:38:00Z"
}
```

#### 3.5 删除角色

**请求**：
```http
DELETE /roles/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```
204 No Content
```

### 4. 操作日志子模块

#### 4.1 获取操作日志列表

**请求**：
```http
GET /logs/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `user_id`: 用户ID
- `action`: 操作类型，可选值：create/update/delete/login/logout
- `module`: 模块名称
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应**：
```json
{
  "count": 1256,
  "next": "https://yagtpotihswf.sealosbja.site/api/logs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1256,
      "user": {
        "id": 1,
        "username": "admin"
      },
      "action": "create",
      "module": "users",
      "resource_id": 57,
      "resource_type": "User",
      "description": "创建了新用户 'newuser'",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "created_at": "2025-04-07T14:35:00Z"
    },
    // 更多日志...
  ]
}
```

#### 4.2 获取单个操作日志详情

**请求**：
```http
GET /logs/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "id": 1256,
  "user": {
    "id": 1,
    "username": "admin"
  },
  "action": "create",
  "module": "users",
  "resource_id": 57,
  "resource_type": "User",
  "description": "创建了新用户 'newuser'",
  "details": {
    "before": null,
    "after": {
      "username": "newuser",
      "email": "newuser@example.com",
      "first_name": "新",
      "last_name": "用户",
      "role_id": 2,
      "department_id": 3,
      "is_active": true
    }
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "created_at": "2025-04-07T14:35:00Z"
}
```
