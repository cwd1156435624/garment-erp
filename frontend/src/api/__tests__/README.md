# API 接口测试用例

本目录包含前端 API 接口的测试用例，使用 Jest 和 axios-mock-adapter 进行模拟测试。

## 测试文件结构

- `customer.test.js` - 客户管理相关接口测试
- `user.test.js` - 用户管理相关接口测试
- `equipment.test.js` - 设备管理相关接口测试
- `production.test.js` - 生产管理相关接口测试
- `taskReminder.test.js` - 任务提醒相关接口测试

## 测试内容

每个测试文件包含对应 API 模块的所有方法测试，每个方法测试包括：

1. 成功场景测试 - 验证接口在正常情况下返回的数据结构和状态码
2. 失败场景测试 - 验证接口在异常情况下返回的错误信息和状态码

## 测试数据结构

所有测试用例遵循统一的响应数据结构：

```javascript
// 成功响应
{
  code: 200,          // 状态码
  data: {...},        // 响应数据
  message: '操作成功'  // 可选的成功消息
}

// 失败响应
{
  code: 400/401/404/500, // 错误状态码
  message: '错误信息',    // 错误消息
  errors: {...}          // 可选的详细错误信息
}
```

## 运行测试

在项目根目录执行以下命令运行测试：

```bash
npm test
```

运行单个测试文件：

```bash
npm test -- src/api/__tests__/customer.test.js
```

## 测试覆盖率

测试覆盖率报告将生成在 `coverage` 目录下，可通过以下命令查看：

```bash
npm test -- --coverage
```

## 注意事项

1. 所有测试用例使用 `axios-mock-adapter` 模拟 API 请求，不会发送真实的网络请求
2. 测试用例中的模拟数据结构应与实际 API 响应保持一致
3. 每个测试用例执行后会重置模拟适配器，确保测试之间相互独立