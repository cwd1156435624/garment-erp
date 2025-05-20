# API命名规范

为确保API设计的一致性和可维护性，本文档定义了项目中API命名的标准规范。

## 基本原则

1. **遵循RESTful设计原则**：API应该围绕资源设计，使用HTTP方法表示操作。
2. **使用复数形式表示资源集合**：例如`/api/users/`而不是`/api/user/`。
3. **使用连字符（-）连接多个单词**：例如`/api/order-items/`而不是`/api/orderItems/`或`/api/order_items/`。
4. **使用小写字母**：所有URL路径应使用小写字母，避免使用大写字母。

## URL路径结构

### 基础路径

所有API请求应使用以下基础路径：
```
https://yagtpotihswf.sealosbja.site/api/
```

### 资源路径

资源路径应遵循以下格式：
```
/api/{resource}/
```

其中`{resource}`是资源的复数形式，例如：
- `/api/users/`
- `/api/orders/`
- `/api/products/`

### 子资源路径

子资源应使用嵌套路径表示：
```
/api/{resource}/{resourceId}/{subresource}/
```

例如：
- `/api/orders/123/items/`
- `/api/users/456/permissions/`

### 操作路径

对资源的特定操作应使用以下格式：
```
/api/{resource}/{resourceId}/{action}/
```

例如：
- `/api/orders/123/cancel/`
- `/api/users/456/activate/`

## HTTP方法

- **GET**：获取资源
- **POST**：创建资源
- **PUT**：完全更新资源
- **PATCH**：部分更新资源
- **DELETE**：删除资源

## 查询参数

查询参数应使用下划线命名法（snake_case）：
```
/api/orders/?status=pending&created_after=2023-01-01
```

常用查询参数：
- `page`：分页页码
- `page_size`：每页记录数
- `ordering`：排序字段
- `search`：搜索关键词
- `fields`：指定返回字段

## 版本控制

如需版本控制，应在URL路径中包含版本号：
```
/api/v1/users/
```

## 现有API路径规范化指南

对于现有的API路径，我们采取以下策略：

1. **保持向后兼容**：不修改已经在使用的API路径，避免破坏现有集成。
2. **新API遵循规范**：所有新开发的API应严格遵循本文档定义的命名规范。
3. **逐步迁移**：在未来的版本更新中，可以考虑逐步将旧API迁移到符合规范的新路径，同时保留旧路径一段时间以确保平滑过渡。

## 特殊路径说明

项目中的一些特殊路径及其用途说明：

- `/api/orders/`：订单资源的别名路径，实际映射到`/api/production/orders/`
- `/api/alerts/`：系统告警的别名路径，实际映射到`/api/system/alerts/`
- `/api/design-files/`：设计文件的别名路径，实际映射到`/api/design/files/`

这些特殊路径是为了提供更直观的API访问方式，同时保持与后端模块结构的一致性。
