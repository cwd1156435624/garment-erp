# API迁移指南：从非版本化API迁移到v1版本

本文档提供了从当前非版本化API迁移到v1版本API的详细指南，帮助开发者顺利完成迁移过程。

## 迁移概述

我们已经实施了API版本控制策略，将所有现有API端点整合到v1版本下。这一变更旨在提高API的可维护性和向后兼容性，同时为未来的API演进提供更清晰的路径。

## 迁移时间表

| 阶段 | 日期 | 说明 |
|------|------|------|
| 并行支持 | 2023-11-01 至 2024-04-30 | 同时支持非版本化API和v1版本API |
| 弃用通知 | 2024-05-01 | 非版本化API将添加弃用响应头 |
| 正式弃用 | 2024-11-01 | 非版本化API将被移除 |

## 端点映射

以下是当前API端点到v1版本API端点的映射：

| 当前端点 | v1版本端点 | 说明 |
|---------|-----------|------|
| `/api/users/` | `/api/v1/users/` | 用户管理API |
| `/api/notifications/` | `/api/v1/notifications/` | 通知API |
| `/api/system/` | `/api/v1/system/` | 系统API |
| `/api/production/` | `/api/v1/production/` | 生产API |
| `/api/orders/` | `/api/v1/orders/` | 订单API |
| `/api/alerts/` | `/api/v1/alerts/` | 系统告警API |
| `/api/equipment/` | `/api/v1/equipment/` | 设备API |
| `/api/inventory/` | `/api/v1/inventory/` | 库存API |
| `/api/supplier/` | `/api/v1/supplier/` | 供应商API |
| `/api/warehouse/` | `/api/v1/warehouse/` | 仓库API |
| `/api/settlement/` | `/api/v1/settlement/` | 结算API |
| `/api/scanning/` | `/api/v1/scanning/` | 扫描API |
| `/api/reports/` | `/api/v1/reports/` | 报表API |
| `/api/materials/` | `/api/v1/materials/` | 物料API |
| `/api/search/` | `/api/v1/search/` | 搜索API |
| `/api/design/` | `/api/v1/design/` | 设计API |
| `/api/design-files/` | `/api/v1/design-files/` | 设计文件API |
| `/api/customer/` | `/api/v1/customer/` | 客户API |
| `/api/finance/` | `/api/v1/finance/` | 财务API |
| `/api/employee/` | `/api/v1/employee/` | 员工API |
| `/api/bom/` | `/api/v1/bom/` | 物料清单API |

## 客户端迁移步骤

### 1. 更新API基础URL

将API基础URL从：

```javascript
const API_BASE_URL = 'https://yagtpotihswf.sealosbja.site/api';
```

更新为：

```javascript
const API_BASE_URL = 'https://yagtpotihswf.sealosbja.site/api/v1';
```

### 2. 更新API客户端配置

如果您使用了API客户端库（如axios），请更新配置：

```javascript
// 旧配置
const apiClient = axios.create({
  baseURL: 'https://yagtpotihswf.sealosbja.site/api',
  // 其他配置...
});

// 新配置
const apiClient = axios.create({
  baseURL: 'https://yagtpotihswf.sealosbja.site/api/v1',
  // 其他配置...
});
```

### 3. 移除冗余路径前缀

由于基础URL已包含`/api/v1`，因此在构建API路径时，应移除冗余的`/api`前缀：

```javascript
// 旧代码
const getUsers = () => apiClient.get('/users');

// 新代码 - 无需更改，因为基础URL已更新
const getUsers = () => apiClient.get('/users');

// 旧代码 - 错误示例，包含冗余前缀
const getOrders = () => apiClient.get('/api/orders');

// 新代码 - 移除冗余前缀
const getOrders = () => apiClient.get('/orders');
```

### 4. 检查自定义API路径

如果您的代码中有硬编码的完整API URL，请更新这些URL：

```javascript
// 旧代码
fetch('https://yagtpotihswf.sealosbja.site/api/users/1')

// 新代码
fetch('https://yagtpotihswf.sealosbja.site/api/v1/users/1')
```

### 5. 更新API文档引用

如果您的代码或文档中引用了API文档URL，请更新这些引用：

```
旧URL: https://yagtpotihswf.sealosbja.site/swagger/
新URL: https://yagtpotihswf.sealosbja.site/swagger/
```

注意：Swagger UI URL保持不变，但其中显示的API端点将包含v1版本路径。

## 测试迁移

为确保迁移顺利，我们建议：

1. 使用我们提供的API测试脚本验证所有v1版本端点：
   ```bash
   python /home/devbox/project/tools/test_api.py --version v1
   ```

2. 使用API性能监控工具比较非版本化API和v1版本API的性能：
   ```bash
   python /home/devbox/project/tools/monitor_api_performance.py --compare-versions
   ```

## 常见问题

### Q: 迁移到v1版本API是否需要更改请求/响应格式？
A: 不需要。v1版本API与当前API保持完全相同的请求和响应格式，只是路径前缀发生了变化。

### Q: 非版本化API何时会被移除？
A: 非版本化API计划于2024年11月1日移除。在此之前，我们将提供至少6个月的并行支持和弃用通知期。

### Q: v1版本API是否支持所有现有功能？
A: 是的。v1版本API完全支持所有现有功能，没有任何功能缺失或行为变更。

### Q: 如何知道我的API请求是否使用了正确的版本？
A: v1版本API的响应头中会包含`X-API-Version: v1`，您可以通过检查此响应头来确认。

## 支持和反馈

如果您在迁移过程中遇到任何问题，或有任何建议，请通过以下渠道联系我们：

- 提交GitHub Issue
- 发送电子邮件至 api-support@example.com
- 在开发者论坛中发帖

我们的团队将及时回应并提供必要的支持。
