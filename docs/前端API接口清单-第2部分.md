# 前端API接口清单-第2部分

本文档详细描述了搜索模块和生产模块的API接口。

## 三、搜索模块 (Search)

### 1. 全局搜索子模块

#### 1.1 全局搜索

**请求**：
```http
GET /search/global/
Authorization: Bearer <your_token>
```

**参数**：
- `q`: 搜索关键词
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `type`: 搜索类型，可选值：all/order/material/customer/supplier

**响应**：
```json
{
  "count": 35,
  "next": "https://yagtpotihswf.sealosbja.site/api/search/global/?q=样衣&page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "type": "order",
      "title": "订单: ORD20250401001",
      "description": "客户: 客户A, 产品: 样衣设计稿",
      "url": "/orders/1/",
      "created_at": "2025-04-01T08:00:00Z",
      "updated_at": "2025-04-01T08:00:00Z"
    },
    {
      "id": 5,
      "type": "material",
      "title": "物料: 高级面料B12345",
      "description": "类型: 面料, 库存: 500米",
      "url": "/materials/5/",
      "created_at": "2025-03-15T10:30:00Z",
      "updated_at": "2025-04-02T14:20:00Z"
    },
    // 更多搜索结果...
  ]
}
```

### 2. 搜索建议子模块

#### 2.1 获取搜索建议

**请求**：
```http
GET /search/suggestions/
Authorization: Bearer <your_token>
```

**参数**：
- `q`: 搜索关键词前缀
- `limit`: 返回建议数量，默认为5
- `type`: 搜索类型，可选值：all/order/material/customer/supplier

**响应**：
```json
{
  "suggestions": [
    {
      "text": "样衣设计",
      "type": "keyword",
      "count": 15
    },
    {
      "text": "样衣工艺单",
      "type": "keyword",
      "count": 8
    },
    {
      "text": "ORD20250315008",
      "type": "order",
      "id": 45
    },
    {
      "text": "客户A",
      "type": "customer",
      "id": 12
    },
    {
      "text": "高级面料B12345",
      "type": "material",
      "id": 5
    }
  ]
}
```

### 3. 高级搜索子模块

#### 3.1 高级搜索

**请求**：
```http
POST /search/advanced/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "type": "order",
  "filters": [
    {
      "field": "customer_name",
      "operator": "contains",
      "value": "客户A"
    },
    {
      "field": "status",
      "operator": "in",
      "value": ["pending", "in_progress"]
    },
    {
      "field": "created_at",
      "operator": "between",
      "value": ["2025-03-01", "2025-04-01"]
    }
  ],
  "sort": [
    {
      "field": "created_at",
      "direction": "desc"
    }
  ],
  "page": 1,
  "page_size": 10
}
```

**响应**：
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 45,
      "order_number": "ORD20250315008",
      "customer_name": "客户A",
      "product_name": "春季新款样衣",
      "status": "in_progress",
      "created_at": "2025-03-15T09:30:00Z",
      "updated_at": "2025-03-20T14:15:00Z"
    },
    // 更多搜索结果...
  ]
}
```

## 四、生产模块 (Production)

### 1. 订单管理子模块

#### 1.1 获取订单列表

**请求**：
```http
GET /orders/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `status`: 订单状态，可选值：draft/pending/in_progress/completed/cancelled
- `customer_id`: 客户ID
- `start_date`: 开始日期
- `end_date`: 结束日期
- `sort_by`: 排序字段，可选值：created_at/delivery_date/priority
- `sort_order`: 排序方向，可选值：asc/desc

**响应**：
```json
{
  "count": 256,
  "next": "https://yagtpotihswf.sealosbja.site/api/orders/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "order_number": "ORD20250401001",
      "customer": {
        "id": 1,
        "name": "客户A"
      },
      "product_name": "春季新款样衣",
      "quantity": 100,
      "status": "in_progress",
      "priority": "high",
      "delivery_date": "2025-04-15",
      "created_at": "2025-04-01T08:00:00Z",
      "updated_at": "2025-04-05T10:30:00Z"
    },
    // 更多订单...
  ]
}
```

#### 1.2 获取单个订单详情

**请求**：
```http
GET /orders/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "id": 1,
  "order_number": "ORD20250401001",
  "customer": {
    "id": 1,
    "name": "客户A",
    "contact_person": "张三",
    "contact_phone": "13800138001"
  },
  "product": {
    "name": "春季新款样衣",
    "code": "PRD20250401001",
    "description": "春季新款女装样衣，面料为高级棉麻混纺",
    "category": "女装",
    "images": [
      {
        "id": 1,
        "url": "https://yagtpotihswf.sealosbja.site/api/media/products/2025/04/01/image1.jpg",
        "is_primary": true
      }
    ]
  },
  "quantity": 100,
  "unit_price": 299.99,
  "total_price": 29999.00,
  "status": "in_progress",
  "priority": "high",
  "delivery_date": "2025-04-15",
  "production_steps": [
    {
      "id": 1,
      "name": "打板",
      "status": "completed",
      "start_date": "2025-04-02T09:00:00Z",
      "end_date": "2025-04-03T17:00:00Z",
      "responsible_person": {
        "id": 5,
        "name": "李四"
      }
    },
    {
      "id": 2,
      "name": "裁剪",
      "status": "in_progress",
      "start_date": "2025-04-04T09:00:00Z",
      "end_date": null,
      "responsible_person": {
        "id": 8,
        "name": "王五"
      }
    },
    // 更多生产步骤...
  ],
  "materials": [
    {
      "id": 1,
      "material": {
        "id": 5,
        "name": "高级面料B12345",
        "code": "MAT20250315005",
        "unit": "米"
      },
      "quantity": 300,
      "unit_price": 50.00,
      "total_price": 15000.00
    },
    // 更多物料...
  ],
  "notes": "客户要求在4月15日前完成样衣，以便进行季度展示",
  "attachments": [
    {
      "id": 1,
      "name": "设计稿.pdf",
      "url": "https://yagtpotihswf.sealosbja.site/api/media/orders/2025/04/01/design.pdf",
      "size": 2048000,
      "uploaded_at": "2025-04-01T08:10:00Z"
    }
  ],
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "created_at": "2025-04-01T08:00:00Z",
  "updated_at": "2025-04-05T10:30:00Z"
}
```

#### 1.3 创建订单

**请求**：
```http
POST /orders/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "customer_id": 1,
  "product_name": "夏季新款样衣",
  "product_code": "PRD20250407001",
  "product_description": "夏季新款女装样衣，面料为轻薄棉",
  "product_category": "女装",
  "quantity": 50,
  "unit_price": 199.99,
  "status": "draft",
  "priority": "medium",
  "delivery_date": "2025-05-15",
  "materials": [
    {
      "material_id": 8,
      "quantity": 150,
      "unit_price": 30.00
    }
  ],
  "notes": "客户要求在5月15日前完成样衣",
  "production_steps": [
    {
      "name": "打板",
      "responsible_person_id": 5,
      "planned_start_date": "2025-04-10T09:00:00Z",
      "planned_end_date": "2025-04-12T17:00:00Z"
    },
    {
      "name": "裁剪",
      "responsible_person_id": 8,
      "planned_start_date": "2025-04-13T09:00:00Z",
      "planned_end_date": "2025-04-15T17:00:00Z"
    }
  ]
}
```

**响应**：
```json
{
  "id": 257,
  "order_number": "ORD20250407001",
  "customer": {
    "id": 1,
    "name": "客户A"
  },
  "product": {
    "name": "夏季新款样衣",
    "code": "PRD20250407001",
    "description": "夏季新款女装样衣，面料为轻薄棉",
    "category": "女装",
    "images": []
  },
  "quantity": 50,
  "unit_price": 199.99,
  "total_price": 9999.50,
  "status": "draft",
  "priority": "medium",
  "delivery_date": "2025-05-15",
  "production_steps": [
    {
      "id": 501,
      "name": "打板",
      "status": "pending",
      "planned_start_date": "2025-04-10T09:00:00Z",
      "planned_end_date": "2025-04-12T17:00:00Z",
      "responsible_person": {
        "id": 5,
        "name": "李四"
      }
    },
    {
      "id": 502,
      "name": "裁剪",
      "status": "pending",
      "planned_start_date": "2025-04-13T09:00:00Z",
      "planned_end_date": "2025-04-15T17:00:00Z",
      "responsible_person": {
        "id": 8,
        "name": "王五"
      }
    }
  ],
  "materials": [
    {
      "id": 301,
      "material": {
        "id": 8,
        "name": "轻薄棉",
        "code": "MAT20250320008",
        "unit": "米"
      },
      "quantity": 150,
      "unit_price": 30.00,
      "total_price": 4500.00
    }
  ],
  "notes": "客户要求在5月15日前完成样衣",
  "attachments": [],
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "created_at": "2025-04-07T14:40:00Z",
  "updated_at": "2025-04-07T14:40:00Z"
}
```

#### 1.4 更新订单

**请求**：
```http
PUT /orders/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "status": "in_progress",
  "priority": "high",
  "notes": "客户要求提前完成，已调整优先级"
}
```

**响应**：
```json
{
  "id": 257,
  "order_number": "ORD20250407001",
  "customer": {
    "id": 1,
    "name": "客户A"
  },
  "product": {
    "name": "夏季新款样衣",
    "code": "PRD20250407001",
    "description": "夏季新款女装样衣，面料为轻薄棉",
    "category": "女装",
    "images": []
  },
  "quantity": 50,
  "unit_price": 199.99,
  "total_price": 9999.50,
  "status": "in_progress",
  "priority": "high",
  "delivery_date": "2025-05-15",
  "production_steps": [
    // 生产步骤...
  ],
  "materials": [
    // 物料...
  ],
  "notes": "客户要求提前完成，已调整优先级",
  "attachments": [],
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "created_at": "2025-04-07T14:40:00Z",
  "updated_at": "2025-04-07T14:41:00Z"
}
```

#### 1.5 删除订单

**请求**：
```http
DELETE /orders/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```
204 No Content
```

### 2. 生产调度子模块

#### 2.1 获取生产调度列表

**请求**：
```http
GET /production/schedules/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `start_date`: 开始日期
- `end_date`: 结束日期
- `status`: 状态，可选值：pending/in_progress/completed/delayed
- `responsible_person_id`: 负责人ID

**响应**：
```json
{
  "count": 45,
  "next": "https://yagtpotihswf.sealosbja.site/api/production/schedules/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "order": {
        "id": 1,
        "order_number": "ORD20250401001",
        "product_name": "春季新款样衣"
      },
      "step": {
        "id": 1,
        "name": "打板"
      },
      "responsible_person": {
        "id": 5,
        "name": "李四"
      },
      "status": "completed",
      "planned_start_date": "2025-04-02T09:00:00Z",
      "planned_end_date": "2025-04-03T17:00:00Z",
      "actual_start_date": "2025-04-02T09:00:00Z",
      "actual_end_date": "2025-04-03T17:00:00Z",
      "progress": 100,
      "notes": "按计划完成"
    },
    // 更多调度...
  ]
}
```

#### 2.2 获取单个生产调度详情

**请求**：
```http
GET /production/schedules/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "id": 1,
  "order": {
    "id": 1,
    "order_number": "ORD20250401001",
    "product_name": "春季新款样衣",
    "customer": {
      "id": 1,
      "name": "客户A"
    }
  },
  "step": {
    "id": 1,
    "name": "打板",
    "description": "根据设计图纸制作样板"
  },
  "responsible_person": {
    "id": 5,
    "name": "李四",
    "department": {
      "id": 2,
      "name": "设计部"
    },
    "phone": "13800138002"
  },
  "status": "completed",
  "planned_start_date": "2025-04-02T09:00:00Z",
  "planned_end_date": "2025-04-03T17:00:00Z",
  "actual_start_date": "2025-04-02T09:00:00Z",
  "actual_end_date": "2025-04-03T17:00:00Z",
  "progress": 100,
  "notes": "按计划完成",
  "attachments": [
    {
      "id": 1,
      "name": "样板图.pdf",
      "url": "https://yagtpotihswf.sealosbja.site/api/media/production/2025/04/03/pattern.pdf",
      "size": 1024000,
      "uploaded_at": "2025-04-03T16:50:00Z"
    }
  ],
  "created_at": "2025-04-01T08:30:00Z",
  "updated_at": "2025-04-03T17:00:00Z"
}
```

#### 2.3 创建生产调度

**请求**：
```http
POST /production/schedules/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "order_id": 257,
  "step_name": "打板",
  "responsible_person_id": 5,
  "planned_start_date": "2025-04-10T09:00:00Z",
  "planned_end_date": "2025-04-12T17:00:00Z",
  "status": "pending",
  "notes": "优先处理"
}
```

**响应**：
```json
{
  "id": 46,
  "order": {
    "id": 257,
    "order_number": "ORD20250407001",
    "product_name": "夏季新款样衣"
  },
  "step": {
    "id": 501,
    "name": "打板"
  },
  "responsible_person": {
    "id": 5,
    "name": "李四"
  },
  "status": "pending",
  "planned_start_date": "2025-04-10T09:00:00Z",
  "planned_end_date": "2025-04-12T17:00:00Z",
  "actual_start_date": null,
  "actual_end_date": null,
  "progress": 0,
  "notes": "优先处理",
  "created_at": "2025-04-07T14:42:00Z",
  "updated_at": "2025-04-07T14:42:00Z"
}
```

#### 2.4 更新生产调度

**请求**：
```http
PUT /production/schedules/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "status": "in_progress",
  "actual_start_date": "2025-04-10T09:30:00Z",
  "progress": 20,
  "notes": "已开始打板，预计按时完成"
}
```

**响应**：
```json
{
  "id": 46,
  "order": {
    "id": 257,
    "order_number": "ORD20250407001",
    "product_name": "夏季新款样衣"
  },
  "step": {
    "id": 501,
    "name": "打板"
  },
  "responsible_person": {
    "id": 5,
    "name": "李四"
  },
  "status": "in_progress",
  "planned_start_date": "2025-04-10T09:00:00Z",
  "planned_end_date": "2025-04-12T17:00:00Z",
  "actual_start_date": "2025-04-10T09:30:00Z",
  "actual_end_date": null,
  "progress": 20,
  "notes": "已开始打板，预计按时完成",
  "created_at": "2025-04-07T14:42:00Z",
  "updated_at": "2025-04-10T10:00:00Z"
}
```

#### 2.5 删除生产调度

**请求**：
```http
DELETE /production/schedules/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```
204 No Content
```
