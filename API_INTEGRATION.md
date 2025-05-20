# API接口集成指南

## 概述
本文档用于记录和管理前后端接口的匹配关系，确保接口实现的一致性和可追踪性。

## 接口规范
- 基础URL: `/api/v1`
- 认证方式: JWT Token
- 响应格式: JSON
- 状态码使用标准HTTP状态码

## 模块接口清单

### 1. 用户管理 (/api/v1/users/)
- [ ] 用户登录 (POST /login/)
- [ ] 用户注册 (POST /register/)
- [ ] 获取用户信息 (GET /profile/)
- [ ] 更新用户信息 (PUT /profile/)

### 2. 系统管理 (/api/v1/system/)
- [ ] 系统配置获取 (GET /config/)
- [ ] 日志查询 (GET /logs/)
- [ ] 开发者接口 (GET /developer/)
- [ ] 通知管理 (GET /notices/)

### 3. 生产管理 (/api/v1/production/)
- [ ] 订单管理 (CRUD /orders/)
- [ ] 生产进度 (GET /progress/)
- [ ] 生产计划 (CRUD /schedule/)
- [ ] 裁剪管理 (CRUD /cutting/)
- [ ] 异常处理 (POST /exception/)

### 4. 仓库管理 (/api/v1/warehouse/)
- [ ] 库存查询 (GET /inventory/)
- [ ] 入库管理 (POST /inbound/)
- [ ] 出库管理 (POST /outbound/)
- [ ] 库存调整 (PUT /adjust/)

### 5. 财务管理 (/api/v1/finance/)
- [ ] 账单管理 (CRUD /bills/)
- [ ] 付款记录 (CRUD /payments/)
- [ ] 收款记录 (CRUD /receipts/)

### 6. 供应商管理 (/api/v1/supplier/)
- [ ] 供应商信息 (CRUD /info/)
- [ ] 供应商评级 (GET /rating/)
- [ ] 采购记录 (CRUD /purchases/)

### 7. 客户管理 (/api/v1/customer/)
- [ ] 客户信息 (CRUD /info/)
- [ ] 订单历史 (GET /orders/)
- [ ] 客户反馈 (CRUD /feedback/)

### 8. 设备管理 (/api/v1/equipment/)
- [ ] 设备列表 (GET /list/)
- [ ] 设备状态 (GET /status/)
- [ ] 维护记录 (CRUD /maintenance/)

### 9. 员工管理 (/api/v1/employee/)
- [ ] 员工信息 (CRUD /info/)
- [ ] 考勤记录 (CRUD /attendance/)
- [ ] 绩效评估 (CRUD /performance/)

### 10. 报表管理 (/api/v1/reports/)
- [ ] 生产报表 (GET /production/)
- [ ] 财务报表 (GET /finance/)
- [ ] 库存报表 (GET /inventory/)

### 11. 结算管理 (/api/v1/settlement/)
- [ ] 工资结算 (CRUD /salary/)
- [ ] 供应商结算 (CRUD /supplier/)
- [ ] 客户结算 (CRUD /customer/)

### 12. 扫描管理 (/api/v1/scanning/)
- [ ] 扫描记录 (POST /record/)
- [ ] 扫描查询 (GET /query/)

### 13. 搜索功能 (/api/v1/search/)
- [ ] 全局搜索 (GET /global/)
- [ ] 高级搜索 (POST /advanced/)

### 14. 物料管理 (/api/v1/materials/)
- [ ] 物料信息 (CRUD /info/)
- [ ] 物料库存 (GET /inventory/)
- [ ] 物料使用记录 (CRUD /usage/)

## 接口状态说明
- [ ] 待实现
- [x] 已实现
- [!] 需要修改

## 注意事项
1. 所有接口都需要在header中携带token进行认证
2. 分页接口统一使用limit/offset参数
3. 查询接口支持多字段过滤和排序
4. 所有时间字段使用ISO 8601格式
5. 文件上传接口使用multipart/form-data格式

## 更新记录
- 2024-03-19: 初始化接口文档
- 后续更新将在此处记录...