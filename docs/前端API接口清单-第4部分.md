# 前端API接口清单-第4部分

本文档详细描述了工厂结算模块和扫码模块的API接口。

## 一、工厂结算模块 (Settlement)

### 1. 结算单管理子模块

#### 1.1 获取结算单列表

**请求**：

```http
GET /settlements/
Authorization: Bearer <your_token>
```

**参数**：

- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `factory_id`: 工厂ID
- `status`: 状态，可选值：draft/pending/approved/rejected/paid
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应**：

```json
{
  "count": 45,
  "next": "https://yagtpotihswf.sealosbja.site/api/settlements/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "settlement_number": "ST20250401001",
      "factory": {
        "id": 5,
        "name": "优质制衣厂"
      },
      "period": "2025-03",
      "total_amount": 125680.50,
      "status": "pending",
      "created_by": {
        "id": 1,
        "username": "admin"
      },
      "created_at": "2025-04-01T10:00:00Z",
      "updated_at": "2025-04-01T10:00:00Z"
    },
    // 更多结算单...
  ]
}
```

#### 1.2 获取单个结算单详情

**请求**：

```http
GET /settlements/{id}/
Authorization: Bearer <your_token>
```

**响应**：

```json
{
  "id": 1,
  "settlement_number": "ST20250401001",
  "factory": {
    "id": 5,
    "name": "优质制衣厂",
    "contact_person": "张经理",
    "contact_phone": "13800138000",
    "address": "广东省广州市番禺区"
  },
  "period": "2025-03",
  "total_amount": 125680.50,
  "paid_amount": 0,
  "status": "pending",
  "payment_due_date": "2025-04-15",
  "payment_method": null,
  "payment_date": null,
  "payment_reference": null,
  "notes": "3月份样衣制作结算单",
  "items": [
    {
      "id": 1,
      "order": {
        "id": 101,
        "order_number": "ORD20250310001",
        "product_name": "春季新款连衣裙"
      },
      "quantity": 5,
      "unit_price": 120.50,
      "amount": 602.50,
      "description": "样衣制作费用"
    },
    {
      "id": 2,
      "order": {
        "id": 102,
        "order_number": "ORD20250315002",
        "product_name": "夏季轻薄T恤"
      },
      "quantity": 10,
      "unit_price": 85.80,
      "amount": 858.00,
      "description": "样衣制作费用"
    },
    // 更多结算项...
  ],
  "approvals": [
    {
      "id": 1,
      "user": {
        "id": 2,
        "username": "manager"
      },
      "status": "pending",
      "comments": null,
      "created_at": null
    }
  ],
  "attachments": [
    {
      "id": 1,
      "file_name": "结算明细表.xlsx",
      "file_url": "https://yagtpotihswf.sealosbja.site/api/media/settlements/1/结算明细表.xlsx",
      "file_size": 25600,
      "uploaded_at": "2025-04-01T10:05:00Z",
      "uploaded_by": {
        "id": 1,
        "username": "admin"
      }
    }
  ],
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "created_at": "2025-04-01T10:00:00Z",
  "updated_at": "2025-04-01T10:05:00Z"
}
```

#### 1.3 创建结算单

**请求**：

```http
POST /settlements/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "factory_id": 5,
  "period": "2025-03",
  "payment_due_date": "2025-04-15",
  "notes": "3月份样衣制作结算单",
  "items": [
    {
      "order_id": 101,
      "quantity": 5,
      "unit_price": 120.50,
      "description": "样衣制作费用"
    },
    {
      "order_id": 102,
      "quantity": 10,
      "unit_price": 85.80,
      "description": "样衣制作费用"
    }
  ]
}
```

**响应**：

```json
{
  "id": 1,
  "settlement_number": "ST20250401001",
  "factory": {
    "id": 5,
    "name": "优质制衣厂"
  },
  "period": "2025-03",
  "total_amount": 1460.50,
  "status": "draft",
  "payment_due_date": "2025-04-15",
  "notes": "3月份样衣制作结算单",
  "items": [
    {
      "id": 1,
      "order": {
        "id": 101,
        "order_number": "ORD20250310001",
        "product_name": "春季新款连衣裙"
      },
      "quantity": 5,
      "unit_price": 120.50,
      "amount": 602.50,
      "description": "样衣制作费用"
    },
    {
      "id": 2,
      "order": {
        "id": 102,
        "order_number": "ORD20250315002",
        "product_name": "夏季轻薄T恤"
      },
      "quantity": 10,
      "unit_price": 85.80,
      "amount": 858.00,
      "description": "样衣制作费用"
    }
  ],
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "created_at": "2025-04-07T15:00:00Z",
  "updated_at": "2025-04-07T15:00:00Z"
}
```

#### 1.4 更新结算单

**请求**：

```http
PUT /settlements/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "payment_due_date": "2025-04-20",
  "notes": "3月份样衣制作结算单（已更新）",
  "items": [
    {
      "id": 1,
      "quantity": 6,
      "unit_price": 120.50,
      "description": "样衣制作费用（含修改）"
    },
    {
      "id": 2,
      "quantity": 10,
      "unit_price": 85.80,
      "description": "样衣制作费用"
    }
  ]
}
```

**响应**：

```json
{
  "id": 1,
  "settlement_number": "ST20250401001",
  "factory": {
    "id": 5,
    "name": "优质制衣厂"
  },
  "period": "2025-03",
  "total_amount": 1581.00,
  "status": "draft",
  "payment_due_date": "2025-04-20",
  "notes": "3月份样衣制作结算单（已更新）",
  "items": [
    {
      "id": 1,
      "order": {
        "id": 101,
        "order_number": "ORD20250310001",
        "product_name": "春季新款连衣裙"
      },
      "quantity": 6,
      "unit_price": 120.50,
      "amount": 723.00,
      "description": "样衣制作费用（含修改）"
    },
    {
      "id": 2,
      "order": {
        "id": 102,
        "order_number": "ORD20250315002",
        "product_name": "夏季轻薄T恤"
      },
      "quantity": 10,
      "unit_price": 85.80,
      "amount": 858.00,
      "description": "样衣制作费用"
    }
  ],
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "created_at": "2025-04-07T15:00:00Z",
  "updated_at": "2025-04-07T15:01:00Z"
}
```

#### 1.5 删除结算单

**请求**：

```http
DELETE /settlements/{id}/
Authorization: Bearer <your_token>
```

**响应**：

```http
204 No Content
```

#### 1.6 提交结算单审批

**请求**：

```http
POST /settlements/{id}/submit/
Authorization: Bearer <your_token>
```

**响应**：

```json
{
  "id": 1,
  "settlement_number": "ST20250401001",
  "status": "pending",
  "submitted_by": {
    "id": 1,
    "username": "admin"
  },
  "submitted_at": "2025-04-07T15:02:00Z"
}
```

#### 1.7 审批结算单

**请求**：

```http
POST /settlements/{id}/approve/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "approved": true,
  "comments": "结算单金额核对无误，同意支付"
}
```

**响应**：

```json
{
  "id": 1,
  "settlement_number": "ST20250401001",
  "status": "approved",
  "approved_by": {
    "id": 2,
    "username": "manager"
  },
  "approved_at": "2025-04-07T15:03:00Z",
  "comments": "结算单金额核对无误，同意支付"
}
```

#### 1.8 记录结算单付款

**请求**：

```http
POST /settlements/{id}/payment/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "payment_method": "bank_transfer",
  "payment_date": "2025-04-08",
  "payment_amount": 1581.00,
  "payment_reference": "TRF20250408001",
  "notes": "已完成银行转账"
}
```

**响应**：

```json
{
  "id": 1,
  "settlement_number": "ST20250401001",
  "status": "paid",
  "payment_method": "bank_transfer",
  "payment_date": "2025-04-08T00:00:00Z",
  "payment_amount": 1581.00,
  "payment_reference": "TRF20250408001",
  "paid_by": {
    "id": 3,
    "username": "finance"
  },
  "paid_at": "2025-04-07T15:04:00Z"
}
```

### 2. 工厂管理子模块

#### 2.1 获取工厂列表

**请求**：

```http
GET /factories/
Authorization: Bearer <your_token>
```

**参数**：

- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `search`: 搜索关键词，支持工厂名称、联系人
- `status`: 状态，可选值：active/inactive

**响应**：

```json
{
  "count": 25,
  "next": "https://yagtpotihswf.sealosbja.site/api/factories/?page=2",
  "previous": null,
  "results": [
    {
      "id": 5,
      "name": "优质制衣厂",
      "contact_person": "张经理",
      "contact_phone": "13800138000",
      "address": "广东省广州市番禺区",
      "status": "active",
      "created_at": "2025-01-15T10:00:00Z"
    },
    // 更多工厂...
  ]
}
```

#### 2.2 获取单个工厂详情

**请求**：

```http
GET /factories/{id}/
Authorization: Bearer <your_token>
```

**响应**：

```json
{
  "id": 5,
  "name": "优质制衣厂",
  "code": "YZZ-001",
  "contact_person": "张经理",
  "contact_phone": "13800138000",
  "contact_email": "zhang@example.com",
  "address": "广东省广州市番禺区",
  "business_license": "91440101XXXXXXXXXX",
  "tax_id": "91440101XXXXXXXXXX",
  "bank_name": "中国工商银行广州分行",
  "bank_account": "6222021234567890123",
  "bank_account_name": "广州优质制衣厂有限公司",
  "production_capacity": "每月5000件",
  "specialties": ["连衣裙", "T恤", "外套"],
  "rating": 4.8,
  "status": "active",
  "notes": "长期合作伙伴，质量稳定",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-03-20T14:30:00Z"
}
```

#### 2.3 创建工厂

**请求**：

```http
POST /factories/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "name": "新锐制衣厂",
  "code": "XRZ-001",
  "contact_person": "李经理",
  "contact_phone": "13900139000",
  "contact_email": "li@example.com",
  "address": "广东省东莞市长安镇",
  "business_license": "91441900XXXXXXXXXX",
  "tax_id": "91441900XXXXXXXXXX",
  "bank_name": "中国建设银行东莞分行",
  "bank_account": "6227001234567890123",
  "bank_account_name": "东莞新锐制衣厂有限公司",
  "production_capacity": "每月3000件",
  "specialties": ["衬衫", "西装", "休闲裤"],
  "status": "active",
  "notes": "新合作伙伴，专注高端定制"
}
```

**响应**：

```json
{
  "id": 26,
  "name": "新锐制衣厂",
  "code": "XRZ-001",
  "contact_person": "李经理",
  "contact_phone": "13900139000",
  "contact_email": "li@example.com",
  "address": "广东省东莞市长安镇",
  "business_license": "91441900XXXXXXXXXX",
  "tax_id": "91441900XXXXXXXXXX",
  "bank_name": "中国建设银行东莞分行",
  "bank_account": "6227001234567890123",
  "bank_account_name": "东莞新锐制衣厂有限公司",
  "production_capacity": "每月3000件",
  "specialties": ["衬衫", "西装", "休闲裤"],
  "rating": null,
  "status": "active",
  "notes": "新合作伙伴，专注高端定制",
  "created_at": "2025-04-07T15:05:00Z",
  "updated_at": "2025-04-07T15:05:00Z"
}
```

#### 2.4 更新工厂信息

**请求**：

```http
PUT /factories/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "contact_person": "王经理",
  "contact_phone": "13900139001",
  "production_capacity": "每月3500件",
  "notes": "新合作伙伴，专注高端定制，质量良好"
}
```

**响应**：

```json
{
  "id": 26,
  "name": "新锐制衣厂",
  "code": "XRZ-001",
  "contact_person": "王经理",
  "contact_phone": "13900139001",
  "contact_email": "li@example.com",
  "address": "广东省东莞市长安镇",
  "business_license": "91441900XXXXXXXXXX",
  "tax_id": "91441900XXXXXXXXXX",
  "bank_name": "中国建设银行东莞分行",
  "bank_account": "6227001234567890123",
  "bank_account_name": "东莞新锐制衣厂有限公司",
  "production_capacity": "每月3500件",
  "specialties": ["衬衫", "西装", "休闲裤"],
  "rating": null,
  "status": "active",
  "notes": "新合作伙伴，专注高端定制，质量良好",
  "created_at": "2025-04-07T15:05:00Z",
  "updated_at": "2025-04-07T15:06:00Z"
}
```

#### 2.5 删除工厂

**请求**：

```http
DELETE /factories/{id}/
Authorization: Bearer <your_token>
```

**响应**：

```http
204 No Content
```

## 二、扫码模块 (Scanning)

### 1. 条码管理子模块

#### 1.1 获取条码列表

**请求**：

```http
GET /barcodes/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `type`: 条码类型，可选值：product/material/order/package
- `status`: 状态，可选值：active/used/expired
- `search`: 搜索关键词，支持条码值、关联对象名称

**响应**：

```json
{
  "count": 156,
  "next": "https://yagtpotihswf.sealosbja.site/api/barcodes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "barcode": "P20250407001",
      "type": "product",
      "related_object": {
        "id": 123,
        "type": "product",
        "name": "春季新款连衣裙"
      },
      "status": "active",
      "created_at": "2025-04-07T10:00:00Z"
    },
    // 更多条码...
  ]
}
```

#### 1.2 获取单个条码详情

**请求**：

```http
GET /barcodes/{id}/
Authorization: Bearer <your_token>
```

**响应**：

```json
{
  "id": 1,
  "barcode": "P20250407001",
  "qr_code_url": "https://yagtpotihswf.sealosbja.site/api/media/barcodes/P20250407001.png",
  "type": "product",
  "related_object": {
    "id": 123,
    "type": "product",
    "name": "春季新款连衣裙",
    "code": "PRD-2025-001",
    "details_url": "https://yagtpotihswf.sealosbja.site/api/products/123/"
  },
  "status": "active",
  "scan_count": 5,
  "last_scanned_at": "2025-04-07T14:30:00Z",
  "last_scanned_by": {
    "id": 2,
    "username": "manager"
  },
  "expiry_date": "2026-04-07T00:00:00Z",
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "created_at": "2025-04-07T10:00:00Z",
  "updated_at": "2025-04-07T14:30:00Z"
}
```

#### 1.3 生成条码

**请求**：

```http
POST /barcodes/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "type": "product",
  "related_object_type": "product",
  "related_object_id": 124,
  "expiry_date": "2026-04-07"
}
```

**响应**：

```json
{
  "id": 157,
  "barcode": "P20250407002",
  "qr_code_url": "https://yagtpotihswf.sealosbja.site/api/media/barcodes/P20250407002.png",
  "type": "product",
  "related_object": {
    "id": 124,
    "type": "product",
    "name": "夏季轻薄T恤",
    "code": "PRD-2025-002"
  },
  "status": "active",
  "scan_count": 0,
  "expiry_date": "2026-04-07T00:00:00Z",
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "created_at": "2025-04-07T15:07:00Z",
  "updated_at": "2025-04-07T15:07:00Z"
}
```

#### 1.4 批量生成条码

**请求**：

```http
POST /barcodes/batch/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "type": "material",
  "related_object_type": "material",
  "related_object_ids": [101, 102, 103],
  "expiry_date": "2026-04-07"
}
```

**响应**：

```json
{
  "success": true,
  "count": 3,
  "barcodes": [
    {
      "id": 158,
      "barcode": "M20250407001",
      "related_object": {
        "id": 101,
        "type": "material",
        "name": "优质棉布"
      }
    },
    {
      "id": 159,
      "barcode": "M20250407002",
      "related_object": {
        "id": 102,
        "type": "material",
        "name": "弹力面料"
      }
    },
    {
      "id": 160,
      "barcode": "M20250407003",
      "related_object": {
        "id": 103,
        "type": "material",
        "name": "牛仔布料"
      }
    }
  ]
}
```

#### 1.5 作废条码

**请求**：

```http
POST /barcodes/{id}/invalidate/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "reason": "产品信息变更"
}
```

**响应**：

```json
{
  "id": 1,
  "barcode": "P20250407001",
  "status": "expired",
  "invalidated_by": {
    "id": 1,
    "username": "admin"
  },
  "invalidated_at": "2025-04-07T15:08:00Z",
  "invalidation_reason": "产品信息变更"
}
```

### 2. 扫码记录子模块

#### 2.1 获取扫码记录列表

**请求**：

```http
GET /scan-records/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `barcode`: 条码值
- `user_id`: 扫码用户ID
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应**：

```json
{
  "count": 256,
  "next": "https://yagtpotihswf.sealosbja.site/api/scan-records/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "barcode": {
        "id": 1,
        "barcode": "P20250407001",
        "type": "product"
      },
      "user": {
        "id": 2,
        "username": "manager"
      },
      "location": "广州仓库",
      "device_info": "iPhone 15 Pro",
      "ip_address": "192.168.1.100",
      "scanned_at": "2025-04-07T14:30:00Z"
    },
    // 更多扫码记录...
  ]
}
```

#### 2.2 记录扫码

**请求**：

```http
POST /scan-records/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "barcode_value": "P20250407001",
  "location": "广州仓库",
  "device_info": "iPhone 15 Pro"
}
```

**响应**：

```json
{
  "id": 257,
  "barcode": {
    "id": 1,
    "barcode": "P20250407001",
    "type": "product",
    "related_object": {
      "id": 123,
      "type": "product",
      "name": "春季新款连衣裙",
      "code": "PRD-2025-001",
      "details_url": "https://yagtpotihswf.sealosbja.site/api/products/123/"
    }
  },
  "user": {
    "id": 1,
    "username": "admin"
  },
  "location": "广州仓库",
  "device_info": "iPhone 15 Pro",
  "ip_address": "192.168.1.101",
  "scanned_at": "2025-04-07T15:09:00Z"
}
```

#### 2.3 获取条码扫描历史

**请求**：

```http
GET /barcodes/{id}/scan-history/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10

**响应**：

```json
{
  "count": 6,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 257,
      "user": {
        "id": 1,
        "username": "admin"
      },
      "location": "广州仓库",
      "device_info": "iPhone 15 Pro",
      "ip_address": "192.168.1.101",
      "scanned_at": "2025-04-07T15:09:00Z"
    },
    {
      "id": 1,
      "user": {
        "id": 2,
        "username": "manager"
      },
      "location": "广州仓库",
      "device_info": "iPhone 15 Pro",
      "ip_address": "192.168.1.100",
      "scanned_at": "2025-04-07T14:30:00Z"
    },
    // 更多扫码记录...
  ]
}
```
