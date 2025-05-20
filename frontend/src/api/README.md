# API 调用示例文档

## 统一说明

所有API请求都会经过以下处理：

1. 请求拦截器会自动从localStorage获取token并添加到请求头：
   ```js
   Authorization: Bearer {token}
   ```

2. 响应拦截器会统一处理返回格式：
   ```js
   {
     code: 200, // 状态码
     message: "success", // 提示信息
     data: {} // 返回数据
   }
   ```

3. 错误处理：
   - HTTP错误会被响应拦截器捕获并打印错误日志
   - 业务错误(code !== 200)会被拒绝并返回错误信息

## 模块说明

### 用户模块 (userApi)

```js
// 登录
userApi.login({
  username: "admin",
  password: "123456"
}).then(res => {
  // res.data: { token: "xxx", user: {...} }
});

// 获取用户信息
userApi.getUserInfo().then(res => {
  // res.data: { id: 1, username: "admin", ... }
});
```

### 设备模块 (equipmentApi)

```js
// 获取设备列表
equipmentApi.getList({
  equipment_type: "machine",
  status: "normal",
  page: 1,
  page_size: 10
}).then(res => {
  // res.data: { count: 100, results: [{...}] }
});

// 创建设备
equipmentApi.create({
  name: "设备1",
  equipment_type: "machine",
  location: "车间A"
}).then(res => {
  // res.data: { id: 1, name: "设备1", ... }
});

// 获取故障统计
equipmentApi.getFaultStatistics().then(res => {
  // res.data: { total: 100, by_status: {...}, by_severity: {...} }
});
```

### 客户模块 (customerApi)

```js
// 获取客户列表
customerApi.getList({
  page: 1,
  page_size: 10
}).then(res => {
  // res.data: { count: 100, results: [{...}] }
});

// 获取客户订单历史
customerApi.getOrderHistory(1, {
  page: 1,
  page_size: 10
}).then(res => {
  // res.data: { count: 50, results: [{...}] }
});
```

### 生产模块 (productionApi)

```js
// 获取生产订单列表
productionApi.getOrderList({
  status: "processing",
  page: 1,
  page_size: 10
}).then(res => {
  // res.data: { count: 100, results: [{...}] }
});

// 获取生产效率统计
productionApi.getProductionEfficiency({
  start_date: "2023-01-01",
  end_date: "2023-12-31"
}).then(res => {
  // res.data: { efficiency: 0.85, details: [...] }
});
```