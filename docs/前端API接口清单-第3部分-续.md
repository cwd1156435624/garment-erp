# 前端API接口清单-第3部分(续)

本文档继续详细描述物料管理模块的API接口。

## 五、物料模块 (Material)

### 1. 物料管理子模块

#### 1.1 获取物料列表

**请求**：
```http
GET /materials/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `search`: 搜索关键词，支持物料名称、编码
- `type`: 物料类型，可选值：fabric/accessory/package/other
- `status`: 状态，可选值：active/inactive
- `sort_by`: 排序字段，可选值：name/code/created_at/stock
- `sort_order`: 排序方向，可选值：asc/desc

**响应**：
```json
{
  "count": 256,
  "next": "https://yagtpotihswf.sealosbja.site/api/materials/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "高级面料B12345",
      "code": "MAT20250315005",
      "type": "fabric",
      "unit": "米",
      "stock": {
        "available": 500,
        "reserved": 300,
        "total": 800
      },
      "price": 50.00,
      "status": "active",
      "created_at": "2025-03-15T10:30:00Z",
      "updated_at": "2025-04-05T16:30:00Z"
    },
    // 更多物料...
  ]
}
```

#### 1.2 获取单个物料详情

**请求**：
```http
GET /materials/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "id": 1,
  "name": "高级面料B12345",
  "code": "MAT20250315005",
  "type": "fabric",
  "category": "棉麻混纺",
  "description": "高品质棉麻混纺面料，适合春季服装",
  "specifications": {
    "width": "1.5米",
    "weight": "200g/m²",
    "color": "蓝色",
    "pattern": "纯色",
    "composition": "60%棉, 40%麻"
  },
  "unit": "米",
  "stock": {
    "available": 500,
    "reserved": 300,
    "total": 800,
    "safety_stock": 100,
    "reorder_point": 200
  },
  "price": {
    "purchase_price": 50.00,
    "currency": "CNY",
    "last_purchase_date": "2025-03-15T10:30:00Z"
  },
  "supplier": {
    "id": 1,
    "name": "优质面料供应商",
    "contact_person": "张三",
    "contact_phone": "13800138001"
  },
  "status": "active",
  "images": [
    {
      "id": 1,
      "url": "https://yagtpotihswf.sealosbja.site/api/media/materials/2025/03/15/fabric1.jpg",
      "is_primary": true
    }
  ],
  "attachments": [
    {
      "id": 1,
      "name": "面料规格说明.pdf",
      "url": "https://yagtpotihswf.sealosbja.site/api/media/materials/2025/03/15/spec.pdf",
      "size": 512000,
      "uploaded_at": "2025-03-15T10:35:00Z"
    }
  ],
  "created_at": "2025-03-15T10:30:00Z",
  "updated_at": "2025-04-05T16:30:00Z"
}
```

#### 1.3 创建物料

**请求**：
```http
POST /materials/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "name": "轻薄棉",
  "code": "MAT20250407001",
  "type": "fabric",
  "category": "纯棉",
  "description": "轻薄纯棉面料，适合夏季服装",
  "specifications": {
    "width": "1.5米",
    "weight": "150g/m²",
    "color": "白色",
    "pattern": "纯色",
    "composition": "100%棉"
  },
  "unit": "米",
  "stock": {
    "available": 1000,
    "safety_stock": 200,
    "reorder_point": 300
  },
  "price": {
    "purchase_price": 30.00,
    "currency": "CNY"
  },
  "supplier_id": 1,
  "status": "active"
}
```

**响应**：
```json
{
  "id": 257,
  "name": "轻薄棉",
  "code": "MAT20250407001",
  "type": "fabric",
  "category": "纯棉",
  "description": "轻薄纯棉面料，适合夏季服装",
  "specifications": {
    "width": "1.5米",
    "weight": "150g/m²",
    "color": "白色",
    "pattern": "纯色",
    "composition": "100%棉"
  },
  "unit": "米",
  "stock": {
    "available": 1000,
    "reserved": 0,
    "total": 1000,
    "safety_stock": 200,
    "reorder_point": 300
  },
  "price": {
    "purchase_price": 30.00,
    "currency": "CNY",
    "last_purchase_date": "2025-04-07T14:47:00Z"
  },
  "supplier": {
    "id": 1,
    "name": "优质面料供应商"
  },
  "status": "active",
  "images": [],
  "attachments": [],
  "created_at": "2025-04-07T14:47:00Z",
  "updated_at": "2025-04-07T14:47:00Z"
}
```

#### 1.4 更新物料

**请求**：
```http
PUT /materials/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "price": {
    "purchase_price": 32.00
  },
  "stock": {
    "safety_stock": 250
  },
  "description": "优质轻薄纯棉面料，适合夏季服装"
}
```

**响应**：
```json
{
  "id": 257,
  "name": "轻薄棉",
  "code": "MAT20250407001",
  "type": "fabric",
  "category": "纯棉",
  "description": "优质轻薄纯棉面料，适合夏季服装",
  "specifications": {
    "width": "1.5米",
    "weight": "150g/m²",
    "color": "白色",
    "pattern": "纯色",
    "composition": "100%棉"
  },
  "unit": "米",
  "stock": {
    "available": 1000,
    "reserved": 0,
    "total": 1000,
    "safety_stock": 250,
    "reorder_point": 300
  },
  "price": {
    "purchase_price": 32.00,
    "currency": "CNY",
    "last_purchase_date": "2025-04-07T14:47:00Z"
  },
  "supplier": {
    "id": 1,
    "name": "优质面料供应商"
  },
  "status": "active",
  "images": [],
  "attachments": [],
  "created_at": "2025-04-07T14:47:00Z",
  "updated_at": "2025-04-07T14:48:00Z"
}
```

#### 1.5 删除物料

**请求**：
```http
DELETE /materials/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```
204 No Content
```

### 2. 库存管理子模块

#### 2.1 获取库存记录列表

**请求**：
```http
GET /inventory/records/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `material_id`: 物料ID
- `type`: 记录类型，可选值：in/out/adjust
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应**：
```json
{
  "count": 156,
  "next": "https://yagtpotihswf.sealosbja.site/api/inventory/records/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "material": {
        "id": 1,
        "name": "高级面料B12345",
        "code": "MAT20250315005"
      },
      "type": "in",
      "quantity": 800,
      "unit": "米",
      "reference": {
        "type": "purchase",
        "id": 1,
        "number": "PO20250315001"
      },
      "operator": {
        "id": 1,
        "name": "管理员"
      },
      "notes": "初始入库",
      "created_at": "2025-03-15T10:30:00Z"
    },
    {
      "id": 2,
      "material": {
        "id": 1,
        "name": "高级面料B12345",
        "code": "MAT20250315005"
      },
      "type": "out",
      "quantity": 300,
      "unit": "米",
      "reference": {
        "type": "order",
        "id": 1,
        "number": "ORD20250401001"
      },
      "operator": {
        "id": 8,
        "name": "王五"
      },
      "notes": "用于订单ORD20250401001的裁剪",
      "created_at": "2025-04-04T09:00:00Z"
    },
    // 更多库存记录...
  ]
}
```

#### 2.2 获取单个库存记录详情

**请求**：
```http
GET /inventory/records/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "id": 1,
  "material": {
    "id": 1,
    "name": "高级面料B12345",
    "code": "MAT20250315005",
    "type": "fabric",
    "unit": "米"
  },
  "type": "in",
  "quantity": 800,
  "unit": "米",
  "reference": {
    "type": "purchase",
    "id": 1,
    "number": "PO20250315001",
    "details": {
      "supplier": {
        "id": 1,
        "name": "优质面料供应商"
      },
      "date": "2025-03-15T10:00:00Z"
    }
  },
  "before_quantity": 0,
  "after_quantity": 800,
  "location": {
    "id": 1,
    "name": "主仓库",
    "code": "WH001"
  },
  "operator": {
    "id": 1,
    "name": "管理员",
    "department": {
      "id": 1,
      "name": "管理部"
    }
  },
  "notes": "初始入库",
  "attachments": [
    {
      "id": 1,
      "name": "入库单.pdf",
      "url": "https://yagtpotihswf.sealosbja.site/api/media/inventory/2025/03/15/receipt.pdf",
      "size": 256000,
      "uploaded_at": "2025-03-15T10:35:00Z"
    }
  ],
  "created_at": "2025-03-15T10:30:00Z"
}
```

#### 2.3 创建库存记录

**请求**：
```http
POST /inventory/records/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "material_id": 257,
  "type": "in",
  "quantity": 500,
  "reference": {
    "type": "purchase",
    "id": 5,
    "number": "PO20250407001"
  },
  "location_id": 1,
  "notes": "补充库存"
}
```

**响应**：
```json
{
  "id": 157,
  "material": {
    "id": 257,
    "name": "轻薄棉",
    "code": "MAT20250407001",
    "type": "fabric",
    "unit": "米"
  },
  "type": "in",
  "quantity": 500,
  "unit": "米",
  "reference": {
    "type": "purchase",
    "id": 5,
    "number": "PO20250407001"
  },
  "before_quantity": 1000,
  "after_quantity": 1500,
  "location": {
    "id": 1,
    "name": "主仓库",
    "code": "WH001"
  },
  "operator": {
    "id": 1,
    "name": "管理员"
  },
  "notes": "补充库存",
  "created_at": "2025-04-07T14:49:00Z"
}
```

#### 2.4 库存调整

**请求**：
```http
POST /inventory/adjust/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "material_id": 257,
  "adjustment_quantity": -50,
  "reason": "inventory_count",
  "notes": "盘点发现实际库存比系统少50米"
}
```

**响应**：
```json
{
  "id": 158,
  "material": {
    "id": 257,
    "name": "轻薄棉",
    "code": "MAT20250407001"
  },
  "type": "adjust",
  "quantity": -50,
  "unit": "米",
  "reference": {
    "type": "adjustment",
    "reason": "inventory_count"
  },
  "before_quantity": 1500,
  "after_quantity": 1450,
  "operator": {
    "id": 1,
    "name": "管理员"
  },
  "notes": "盘点发现实际库存比系统少50米",
  "created_at": "2025-04-07T14:50:00Z"
}
```

#### 2.5 获取库存预警列表

**请求**：
```http
GET /inventory/alerts/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `type`: 预警类型，可选值：low_stock/out_of_stock/over_stock
- `severity`: 严重程度，可选值：low/medium/high

**响应**：
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "material": {
        "id": 5,
        "name": "纽扣A001",
        "code": "MAT20250320001",
        "type": "accessory"
      },
      "type": "low_stock",
      "severity": "medium",
      "current_stock": 50,
      "threshold": 100,
      "created_at": "2025-04-05T10:30:00Z",
      "updated_at": "2025-04-05T10:30:00Z"
    },
    // 更多预警...
  ]
}
```

### 3. 供应商管理子模块

#### 3.1 获取供应商列表

**请求**：
```http
GET /suppliers/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `search`: 搜索关键词，支持供应商名称、联系人
- `category`: 供应商类别，可选值：fabric/accessory/package/service
- `status`: 状态，可选值：active/inactive

**响应**：
```json
{
  "count": 25,
  "next": "https://yagtpotihswf.sealosbja.site/api/suppliers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "优质面料供应商",
      "code": "SUP001",
      "category": "fabric",
      "contact_person": "张三",
      "contact_phone": "13800138001",
      "email": "supplier1@example.com",
      "status": "active",
      "rating": 4.8,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-03-15T10:30:00Z"
    },
    // 更多供应商...
  ]
}
```

#### 3.2 获取单个供应商详情

**请求**：
```http
GET /suppliers/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "id": 1,
  "name": "优质面料供应商",
  "code": "SUP001",
  "category": "fabric",
  "description": "专业提供高品质面料的供应商",
  "contact": {
    "person": "张三",
    "phone": "13800138001",
    "email": "supplier1@example.com",
    "address": "广东省广州市天河区某某路123号",
    "postcode": "510000"
  },
  "business": {
    "license_number": "91440101XXXXXXXXXX",
    "tax_number": "91440101XXXXXXXXXX",
    "bank_name": "中国工商银行",
    "bank_account": "6212XXXXXXXXXXXX",
    "bank_account_name": "广州优质面料有限公司"
  },
  "cooperation": {
    "start_date": "2025-01-01",
    "payment_terms": "30天",
    "delivery_terms": "供应商负责运输",
    "minimum_order": "100米"
  },
  "materials": [
    {
      "id": 1,
      "name": "高级面料B12345",
      "code": "MAT20250315005",
      "type": "fabric",
      "price": 50.00
    },
    {
      "id": 8,
      "name": "轻薄棉",
      "code": "MAT20250320008",
      "type": "fabric",
      "price": 30.00
    }
    // 更多物料...
  ],
  "status": "active",
  "rating": 4.8,
  "performance": {
    "on_time_delivery": 95,
    "quality_pass_rate": 98,
    "response_time": "24小时内"
  },
  "attachments": [
    {
      "id": 1,
      "name": "合作协议.pdf",
      "url": "https://yagtpotihswf.sealosbja.site/api/media/suppliers/2025/01/01/agreement.pdf",
      "size": 1024000,
      "uploaded_at": "2025-01-01T00:10:00Z"
    }
  ],
  "notes": "长期合作伙伴，产品质量稳定",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-03-15T10:30:00Z"
}
```

#### 3.3 创建供应商

**请求**：
```http
POST /suppliers/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "name": "新辅料供应商",
  "code": "SUP026",
  "category": "accessory",
  "description": "专业提供各类服装辅料的供应商",
  "contact": {
    "person": "李四",
    "phone": "13900139000",
    "email": "supplier26@example.com",
    "address": "浙江省杭州市余杭区某某路456号",
    "postcode": "310000"
  },
  "business": {
    "license_number": "91330110XXXXXXXXXX",
    "tax_number": "91330110XXXXXXXXXX"
  },
  "cooperation": {
    "payment_terms": "15天",
    "delivery_terms": "供应商负责运输"
  },
  "status": "active"
}
```

**响应**：
```json
{
  "id": 26,
  "name": "新辅料供应商",
  "code": "SUP026",
  "category": "accessory",
  "description": "专业提供各类服装辅料的供应商",
  "contact": {
    "person": "李四",
    "phone": "13900139000",
    "email": "supplier26@example.com",
    "address": "浙江省杭州市余杭区某某路456号",
    "postcode": "310000"
  },
  "business": {
    "license_number": "91330110XXXXXXXXXX",
    "tax_number": "91330110XXXXXXXXXX"
  },
  "cooperation": {
    "start_date": "2025-04-07",
    "payment_terms": "15天",
    "delivery_terms": "供应商负责运输"
  },
  "materials": [],
  "status": "active",
  "rating": null,
  "performance": {},
  "attachments": [],
  "notes": "",
  "created_at": "2025-04-07T14:51:00Z",
  "updated_at": "2025-04-07T14:51:00Z"
}
```

#### 3.4 更新供应商

**请求**：
```http
PUT /suppliers/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "contact": {
    "phone": "13900139001",
    "email": "newsupplier26@example.com"
  },
  "cooperation": {
    "payment_terms": "30天"
  },
  "notes": "新合作伙伴，质量有保障"
}
```

**响应**：
```json
{
  "id": 26,
  "name": "新辅料供应商",
  "code": "SUP026",
  "category": "accessory",
  "description": "专业提供各类服装辅料的供应商",
  "contact": {
    "person": "李四",
    "phone": "13900139001",
    "email": "newsupplier26@example.com",
    "address": "浙江省杭州市余杭区某某路456号",
    "postcode": "310000"
  },
  "business": {
    "license_number": "91330110XXXXXXXXXX",
    "tax_number": "91330110XXXXXXXXXX"
  },
  "cooperation": {
    "start_date": "2025-04-07",
    "payment_terms": "30天",
    "delivery_terms": "供应商负责运输"
  },
  "materials": [],
  "status": "active",
  "rating": null,
  "performance": {},
  "attachments": [],
  "notes": "新合作伙伴，质量有保障",
  "created_at": "2025-04-07T14:51:00Z",
  "updated_at": "2025-04-07T14:52:00Z"
}
```

#### 3.5 删除供应商

**请求**：
```http
DELETE /suppliers/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```
204 No Content
```
