# 前端API接口清单-第3部分

本文档详细描述了生产管理模块的后续API接口和物料管理模块的API接口。

## 四、生产模块 (Production) - 续

### 3. 生产进度子模块

#### 3.1 获取生产进度列表

**请求**：
```http
GET /production/progress/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `order_id`: 订单ID
- `start_date`: 开始日期
- `end_date`: 结束日期
- `status`: 状态，可选值：pending/in_progress/completed/delayed

**响应**：
```json
{
  "count": 256,
  "next": "https://yagtpotihswf.sealosbja.site/api/production/progress/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "order": {
        "id": 1,
        "order_number": "ORD20250401001",
        "product_name": "春季新款样衣"
      },
      "overall_progress": 60,
      "status": "in_progress",
      "steps": [
        {
          "id": 1,
          "name": "打板",
          "status": "completed",
          "progress": 100
        },
        {
          "id": 2,
          "name": "裁剪",
          "status": "in_progress",
          "progress": 80
        },
        {
          "id": 3,
          "name": "缝制",
          "status": "pending",
          "progress": 0
        }
      ],
      "start_date": "2025-04-02T09:00:00Z",
      "estimated_completion_date": "2025-04-10T17:00:00Z",
      "updated_at": "2025-04-05T10:30:00Z"
    },
    // 更多进度...
  ]
}
```

#### 3.2 获取单个订单的生产进度详情

**请求**：
```http
GET /production/progress/{order_id}/
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
    },
    "delivery_date": "2025-04-15"
  },
  "overall_progress": 60,
  "status": "in_progress",
  "steps": [
    {
      "id": 1,
      "name": "打板",
      "description": "根据设计图纸制作样板",
      "status": "completed",
      "progress": 100,
      "responsible_person": {
        "id": 5,
        "name": "李四"
      },
      "start_date": "2025-04-02T09:00:00Z",
      "end_date": "2025-04-03T17:00:00Z",
      "notes": "按计划完成"
    },
    {
      "id": 2,
      "name": "裁剪",
      "description": "根据样板裁剪面料",
      "status": "in_progress",
      "progress": 80,
      "responsible_person": {
        "id": 8,
        "name": "王五"
      },
      "start_date": "2025-04-04T09:00:00Z",
      "end_date": null,
      "notes": "进展顺利，预计明天完成"
    },
    {
      "id": 3,
      "name": "缝制",
      "description": "将裁剪好的面料进行缝制",
      "status": "pending",
      "progress": 0,
      "responsible_person": {
        "id": 12,
        "name": "赵六"
      },
      "start_date": null,
      "end_date": null,
      "notes": "等待裁剪完成"
    }
  ],
  "timeline": [
    {
      "date": "2025-04-01T08:00:00Z",
      "event": "订单创建",
      "user": {
        "id": 1,
        "name": "管理员"
      }
    },
    {
      "date": "2025-04-02T09:00:00Z",
      "event": "开始打板",
      "user": {
        "id": 5,
        "name": "李四"
      }
    },
    {
      "date": "2025-04-03T17:00:00Z",
      "event": "打板完成",
      "user": {
        "id": 5,
        "name": "李四"
      }
    },
    {
      "date": "2025-04-04T09:00:00Z",
      "event": "开始裁剪",
      "user": {
        "id": 8,
        "name": "王五"
      }
    }
  ],
  "start_date": "2025-04-02T09:00:00Z",
  "estimated_completion_date": "2025-04-10T17:00:00Z",
  "is_delayed": false,
  "delay_reason": null,
  "created_at": "2025-04-01T08:00:00Z",
  "updated_at": "2025-04-05T10:30:00Z"
}
```

#### 3.3 更新生产进度

**请求**：
```http
PUT /production/progress/{order_id}/steps/{step_id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "status": "completed",
  "progress": 100,
  "end_date": "2025-04-05T16:30:00Z",
  "notes": "裁剪工作已完成，质量良好"
}
```

**响应**：
```json
{
  "id": 2,
  "name": "裁剪",
  "description": "根据样板裁剪面料",
  "status": "completed",
  "progress": 100,
  "responsible_person": {
    "id": 8,
    "name": "王五"
  },
  "start_date": "2025-04-04T09:00:00Z",
  "end_date": "2025-04-05T16:30:00Z",
  "notes": "裁剪工作已完成，质量良好",
  "updated_at": "2025-04-05T16:30:00Z"
}
```

### 4. 裁剪管理子模块

#### 4.1 获取裁剪任务列表

**请求**：
```http
GET /production/cutting-tasks/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `order_id`: 订单ID
- `status`: 状态，可选值：pending/in_progress/completed
- `responsible_person_id`: 负责人ID

**响应**：
```json
{
  "count": 45,
  "next": "https://yagtpotihswf.sealosbja.site/api/production/cutting-tasks/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "order": {
        "id": 1,
        "order_number": "ORD20250401001",
        "product_name": "春季新款样衣"
      },
      "material": {
        "id": 5,
        "name": "高级面料B12345"
      },
      "quantity": 300,
      "unit": "米",
      "status": "completed",
      "responsible_person": {
        "id": 8,
        "name": "王五"
      },
      "start_date": "2025-04-04T09:00:00Z",
      "end_date": "2025-04-05T16:30:00Z",
      "created_at": "2025-04-03T17:00:00Z",
      "updated_at": "2025-04-05T16:30:00Z"
    },
    // 更多裁剪任务...
  ]
}
```

#### 4.2 获取单个裁剪任务详情

**请求**：
```http
GET /production/cutting-tasks/{id}/
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
  "material": {
    "id": 5,
    "name": "高级面料B12345",
    "code": "MAT20250315005",
    "type": "面料",
    "color": "蓝色",
    "specifications": "宽度: 1.5米",
    "inventory": {
      "available": 500,
      "reserved": 300,
      "unit": "米"
    }
  },
  "pattern": {
    "id": 1,
    "name": "春季新款样衣-样板",
    "file_url": "https://yagtpotihswf.sealosbja.site/api/media/patterns/2025/04/03/pattern.pdf"
  },
  "quantity": 300,
  "unit": "米",
  "waste_estimate": 15,
  "waste_actual": 12,
  "status": "completed",
  "responsible_person": {
    "id": 8,
    "name": "王五",
    "department": {
      "id": 3,
      "name": "生产部"
    },
    "phone": "13800138003"
  },
  "start_date": "2025-04-04T09:00:00Z",
  "end_date": "2025-04-05T16:30:00Z",
  "notes": "裁剪工作已完成，质量良好",
  "issues": [],
  "created_at": "2025-04-03T17:00:00Z",
  "updated_at": "2025-04-05T16:30:00Z"
}
```

#### 4.3 创建裁剪任务

**请求**：
```http
POST /production/cutting-tasks/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "order_id": 257,
  "material_id": 8,
  "pattern_id": 5,
  "quantity": 150,
  "unit": "米",
  "waste_estimate": 10,
  "responsible_person_id": 8,
  "status": "pending",
  "notes": "请按照样板精确裁剪"
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
  "material": {
    "id": 8,
    "name": "轻薄棉"
  },
  "pattern": {
    "id": 5,
    "name": "夏季新款样衣-样板"
  },
  "quantity": 150,
  "unit": "米",
  "waste_estimate": 10,
  "waste_actual": null,
  "status": "pending",
  "responsible_person": {
    "id": 8,
    "name": "王五"
  },
  "start_date": null,
  "end_date": null,
  "notes": "请按照样板精确裁剪",
  "created_at": "2025-04-07T14:45:00Z",
  "updated_at": "2025-04-07T14:45:00Z"
}
```

#### 4.4 更新裁剪任务

**请求**：
```http
PUT /production/cutting-tasks/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "status": "in_progress",
  "start_date": "2025-04-13T09:00:00Z",
  "notes": "已开始裁剪，预计明天完成"
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
  "material": {
    "id": 8,
    "name": "轻薄棉"
  },
  "pattern": {
    "id": 5,
    "name": "夏季新款样衣-样板"
  },
  "quantity": 150,
  "unit": "米",
  "waste_estimate": 10,
  "waste_actual": null,
  "status": "in_progress",
  "responsible_person": {
    "id": 8,
    "name": "王五"
  },
  "start_date": "2025-04-13T09:00:00Z",
  "end_date": null,
  "notes": "已开始裁剪，预计明天完成",
  "created_at": "2025-04-07T14:45:00Z",
  "updated_at": "2025-04-13T09:00:00Z"
}
```

#### 4.5 删除裁剪任务

**请求**：
```http
DELETE /production/cutting-tasks/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```
204 No Content
```

### 5. 异常管理子模块

#### 5.1 获取异常列表

**请求**：
```http
GET /production/issues/
Authorization: Bearer <your_token>
```

**参数**：
- `page`: 页码，默认为1
- `page_size`: 每页条数，默认为10
- `order_id`: 订单ID
- `status`: 状态，可选值：open/in_progress/resolved/closed
- `severity`: 严重程度，可选值：low/medium/high/critical
- `type`: 类型，可选值：material/quality/process/equipment

**响应**：
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "order": {
        "id": 1,
        "order_number": "ORD20250401001",
        "product_name": "春季新款样衣"
      },
      "title": "面料质量问题",
      "type": "material",
      "severity": "high",
      "status": "resolved",
      "reported_by": {
        "id": 8,
        "name": "王五"
      },
      "assigned_to": {
        "id": 5,
        "name": "李四"
      },
      "reported_at": "2025-04-04T10:30:00Z",
      "resolved_at": "2025-04-04T16:00:00Z",
      "updated_at": "2025-04-04T16:00:00Z"
    },
    // 更多异常...
  ]
}
```

#### 5.2 获取单个异常详情

**请求**：
```http
GET /production/issues/{id}/
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
  "title": "面料质量问题",
  "description": "发现部分面料有色差，可能影响成品质量",
  "type": "material",
  "severity": "high",
  "status": "resolved",
  "impact": "可能导致部分成品不合格，需要重新采购面料",
  "reported_by": {
    "id": 8,
    "name": "王五",
    "department": {
      "id": 3,
      "name": "生产部"
    },
    "phone": "13800138003"
  },
  "assigned_to": {
    "id": 5,
    "name": "李四",
    "department": {
      "id": 2,
      "name": "设计部"
    },
    "phone": "13800138002"
  },
  "resolution": "已联系供应商更换面料，新面料已到货并检查合格",
  "attachments": [
    {
      "id": 1,
      "name": "面料问题照片.jpg",
      "url": "https://yagtpotihswf.sealosbja.site/api/media/issues/2025/04/04/fabric_issue.jpg",
      "size": 512000,
      "uploaded_at": "2025-04-04T10:35:00Z"
    }
  ],
  "comments": [
    {
      "id": 1,
      "user": {
        "id": 8,
        "name": "王五"
      },
      "content": "发现部分面料有明显色差，已停止裁剪",
      "created_at": "2025-04-04T10:35:00Z"
    },
    {
      "id": 2,
      "user": {
        "id": 5,
        "name": "李四"
      },
      "content": "已联系供应商，他们将在今天下午送来新的面料",
      "created_at": "2025-04-04T11:20:00Z"
    },
    {
      "id": 3,
      "user": {
        "id": 5,
        "name": "李四"
      },
      "content": "新面料已到货并检查合格，可以继续生产",
      "created_at": "2025-04-04T15:50:00Z"
    }
  ],
  "reported_at": "2025-04-04T10:30:00Z",
  "resolved_at": "2025-04-04T16:00:00Z",
  "created_at": "2025-04-04T10:30:00Z",
  "updated_at": "2025-04-04T16:00:00Z"
}
```

#### 5.3 创建异常

**请求**：
```http
POST /production/issues/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "order_id": 257,
  "title": "缝制质量问题",
  "description": "部分缝线不平整，需要返工",
  "type": "quality",
  "severity": "medium",
  "impact": "可能延迟交付时间",
  "assigned_to_id": 12
}
```

**响应**：
```json
{
  "id": 16,
  "order": {
    "id": 257,
    "order_number": "ORD20250407001",
    "product_name": "夏季新款样衣"
  },
  "title": "缝制质量问题",
  "description": "部分缝线不平整，需要返工",
  "type": "quality",
  "severity": "medium",
  "status": "open",
  "impact": "可能延迟交付时间",
  "reported_by": {
    "id": 1,
    "name": "管理员"
  },
  "assigned_to": {
    "id": 12,
    "name": "赵六"
  },
  "resolution": null,
  "reported_at": "2025-04-07T14:46:00Z",
  "resolved_at": null,
  "created_at": "2025-04-07T14:46:00Z",
  "updated_at": "2025-04-07T14:46:00Z"
}
```

#### 5.4 更新异常

**请求**：
```http
PUT /production/issues/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "status": "resolved",
  "resolution": "已重新缝制，质量检查合格",
  "resolved_at": "2025-04-14T15:30:00Z"
}
```

**响应**：
```json
{
  "id": 16,
  "order": {
    "id": 257,
    "order_number": "ORD20250407001",
    "product_name": "夏季新款样衣"
  },
  "title": "缝制质量问题",
  "description": "部分缝线不平整，需要返工",
  "type": "quality",
  "severity": "medium",
  "status": "resolved",
  "impact": "可能延迟交付时间",
  "reported_by": {
    "id": 1,
    "name": "管理员"
  },
  "assigned_to": {
    "id": 12,
    "name": "赵六"
  },
  "resolution": "已重新缝制，质量检查合格",
  "reported_at": "2025-04-07T14:46:00Z",
  "resolved_at": "2025-04-14T15:30:00Z",
  "created_at": "2025-04-07T14:46:00Z",
  "updated_at": "2025-04-14T15:30:00Z"
}
```

#### 5.5 添加异常评论

**请求**：
```http
POST /production/issues/{id}/comments/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "content": "已开始修复缝制问题，预计今天完成"
}
```

**响应**：
```json
{
  "id": 4,
  "user": {
    "id": 12,
    "name": "赵六"
  },
  "content": "已开始修复缝制问题，预计今天完成",
  "created_at": "2025-04-14T10:20:00Z"
}
```

#### 5.6 删除异常

**请求**：
```http
DELETE /production/issues/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```
204 No Content
```
