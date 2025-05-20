# API文档

本文档提供了系统中所有API端点的详细说明，包括其用途、请求方法、参数和响应格式。

## 基础信息

**基础URL**: `https://yagtpotihswf.sealosbja.site/api`

**认证方式**: JWT (JSON Web Token)

所有API请求（除了认证相关的端点）都需要在请求头中包含有效的JWT令牌：

```
Authorization: Bearer {token}
```

## 认证API

### 获取令牌

```
POST /api/token/
```

**请求体**:
```json
{
  "username": "用户名",
  "password": "密码"
}
```

**响应**:
```json
{
  "access": "访问令牌",
  "refresh": "刷新令牌"
}
```

### 刷新令牌

```
POST /api/token/refresh/
```

**请求体**:
```json
{
  "refresh": "刷新令牌"
}
```

**响应**:
```json
{
  "access": "新的访问令牌"
}
```

## 用户API

### 获取用户列表

```
GET /api/users/
```

**查询参数**:
- `page`: 页码
- `page_size`: 每页记录数
- `search`: 搜索关键词

**响应**:
```json
{
  "count": 总记录数,
  "next": "下一页URL",
  "previous": "上一页URL",
  "results": [
    {
      "id": "用户ID",
      "username": "用户名",
      "email": "邮箱",
      "is_active": 是否激活,
      "date_joined": "注册日期"
    }
  ]
}
```

### 获取当前用户信息

```
GET /api/users/me/
```

**响应**:
```json
{
  "id": "用户ID",
  "username": "用户名",
  "email": "邮箱",
  "is_active": 是否激活,
  "date_joined": "注册日期",
  "permissions": ["权限列表"]
}
```

## 通知API

### 获取通知列表

```
GET /api/notifications/
```

**查询参数**:
- `page`: 页码
- `page_size`: 每页记录数
- `is_read`: 筛选已读/未读通知 (true/false)

**响应**:
```json
{
  "count": 总记录数,
  "results": [
    {
      "id": "通知ID",
      "title": "通知标题",
      "content": "通知内容",
      "type": "通知类型",
      "is_read": 是否已读,
      "created_at": "创建时间"
    }
  ]
}
```

### 获取未读通知数量

```
GET /api/notifications/unread-count/
```

**响应**:
```json
{
  "count": 未读通知数量
}
```

### 标记通知为已读

```
POST /api/notifications/{id}/read/
```

**响应**:
```json
{
  "status": "success"
}
```

### 标记所有通知为已读

```
POST /api/notifications/read-all/
```

**响应**:
```json
{
  "status": "success"
}
```

## 首页API

### 获取订单统计

```
GET /api/orders/stats/
```

**响应**:
```json
{
  "total": 订单总数,
  "inProduction": 生产中订单数,
  "completed": 已完成订单数,
  "abnormal": 异常订单数,
  "newAdded": 新增订单数
}
```

### 获取物料统计

```
GET /api/materials/stats/
```

**响应**:
```json
{
  "total": 物料总数,
  "inStock": 库存充足物料数,
  "lowStock": 库存不足物料数
}
```

### 获取最近订单

```
GET /api/orders/
```

**查询参数**:
- `page_size`: 每页记录数（默认10）
- `ordering`: 排序字段（默认-created_at）

**响应**:
```json
{
  "count": 总记录数,
  "results": [
    {
      "id": "订单ID",
      "orderNo": "订单编号",
      "customer": "客户名称",
      "status": "订单状态",
      "totalAmount": 订单金额,
      "createdAt": "创建时间",
      "deliveryDate": "交付日期"
    }
  ]
}
```

### 获取系统公告

```
GET /api/notices/
```

**查询参数**:
- `page_size`: 每页记录数（默认5）

**响应**:
```json
{
  "count": 总记录数,
  "results": [
    {
      "id": "公告ID",
      "title": "公告标题",
      "content": "公告内容",
      "createdAt": "创建时间",
      "isImportant": 是否重要
    }
  ]
}
```

### 获取系统告警

```
GET /api/alerts/
```

**查询参数**:
- `page_size`: 每页记录数（默认10）
- `ordering`: 排序字段（默认-created_at）

**响应**:
```json
{
  "count": 总记录数,
  "results": [
    {
      "id": "告警ID",
      "title": "告警标题",
      "content": "告警内容",
      "severity": "严重程度",
      "status": "告警状态",
      "created_at": "创建时间"
    }
  ]
}
```

## 设计文件API

### 获取设计文件列表

```
GET /api/design-files/
```

**查询参数**:
- `page`: 页码
- `page_size`: 每页记录数
- `search`: 搜索关键词
- `status`: 文件状态
- `type`: 文件类型

**响应**:
```json
{
  "count": 总记录数,
  "results": [
    {
      "id": "文件ID",
      "name": "文件名称",
      "type": "文件类型",
      "status": "文件状态",
      "version": "版本号",
      "created_by": "创建者",
      "created_at": "创建时间",
      "file_url": "文件URL"
    }
  ]
}
```

### 上传设计文件

```
POST /api/design-files/
```

**请求体** (multipart/form-data):
- `name`: 文件名称
- `type`: 文件类型
- `description`: 文件描述
- `file`: 文件内容

**响应**:
```json
{
  "id": "文件ID",
  "name": "文件名称",
  "type": "文件类型",
  "status": "文件状态",
  "version": "版本号",
  "created_by": "创建者",
  "created_at": "创建时间",
  "file_url": "文件URL"
}
```

## 物料API

### 获取物料列表

```
GET /api/materials/
```

**查询参数**:
- `page`: 页码
- `page_size`: 每页记录数
- `search`: 搜索关键词
- `category`: 物料类别
- `in_stock`: 是否有库存

**响应**:
```json
{
  "count": 总记录数,
  "results": [
    {
      "id": "物料ID",
      "code": "物料编码",
      "name": "物料名称",
      "category": "物料类别",
      "specification": "规格",
      "unit": "单位",
      "stock_quantity": 库存数量,
      "min_stock": 最小库存,
      "price": 单价
    }
  ]
}
```

## WebSocket服务

WebSocket服务用于提供实时更新功能，包括通知推送、系统告警等。

### 连接WebSocket

```
WebSocket: wss://yagtpotihswf.sealosbja.site/ws/
```

**连接参数**:
- `token`: JWT访问令牌

### 消息格式

**服务器发送的消息**:
```json
{
  "type": "消息类型",
  "data": {
    // 消息内容，根据type不同而不同
  }
}
```

**消息类型**:
- `notification`: 新通知
- `alert`: 系统告警
- `order_update`: 订单状态更新
- `material_update`: 物料库存更新

## API关系说明

### 特殊路径与常规路径的关系

1. **订单API**:
   - `/api/orders/`: 订单资源的别名路径
   - `/api/production/orders/`: 订单资源的原始路径
   
   这两个路径指向相同的资源，但`/api/orders/`提供了更简洁的访问方式，特别适合前端使用。

2. **告警API**:
   - `/api/alerts/`: 系统告警的别名路径
   - `/api/system/alerts/`: 系统告警的原始路径
   
   同样，`/api/alerts/`是一个更简洁的别名，指向系统模块中的告警资源。

3. **设计文件API**:
   - `/api/design-files/`: 设计文件的别名路径
   - `/api/design/files/`: 设计文件的原始路径
   
   这种映射使得API路径更符合直觉，同时保持了后端模块的组织结构。

### 模块间的关系

1. **用户与通知**:
   - 通知(`/api/notifications/`)与用户(`/api/users/`)相关联，每个通知都属于特定用户。

2. **订单与物料**:
   - 订单(`/api/orders/`)使用物料(`/api/materials/`)，订单状态变更可能影响物料库存。

3. **设计与生产**:
   - 设计文件(`/api/design-files/`)用于生产过程，与订单(`/api/orders/`)相关联。

## 开发者API

开发者API提供了用于系统监控、调试和管理的端点，仅供开发人员使用。

```
GET /api/developer/system-monitor/
GET /api/developer/api-metrics/
GET /api/developer/system-logs/
GET /api/developer/health/
POST /api/developer/test-endpoint/
```

这些API需要特殊的开发者权限才能访问。
