# API增强功能使用指南

## 概述

为了提升前端API调用的稳定性、性能和用户体验，我们在原有API封装的基础上，增加了以下增强功能：

1. **请求重试**：自动重试失败的请求，提高请求成功率
2. **请求超时控制**：更精细的请求超时控制
3. **请求防抖**：避免短时间内重复发起相同请求
4. **请求节流**：限制请求频率
5. **请求缓存**：缓存请求结果，减少重复请求
6. **请求取消**：支持取消正在进行的请求
7. **批量请求**：优化多个相关请求的处理
8. **Mock数据**：便于前端开发和测试

## 使用方法

### 1. 基础用法

增强版API请求工具完全兼容原有API用法，可以直接替换：

```javascript
// 原来的用法
import request from '../utils/request';

// 替换为增强版
import enhancedRequest from '../utils/enhancedRequest';

// 使用方式相同
enhancedRequest({
  url: '/users/info/',
  method: 'get'
});

// 或使用简化方法
enhancedRequest.get('/users/info/');
```

### 2. 请求重试

适用场景：网络不稳定、服务器临时故障等情况。

```javascript
// 带重试机制的请求
enhancedRequest.get('/api/data', {}, {
  useRetry: true,
  retryOptions: {
    retries: 3,           // 最多重试3次
    retryDelay: 1000,     // 重试间隔1秒
    shouldRetry: (error) => {
      // 自定义重试条件，例如只在网络错误或5xx错误时重试
      return error.message.includes('Network Error') || 
             (error.response && error.response.status >= 500);
    }
  }
});
```

### 3. 请求防抖

适用场景：用户快速输入搜索条件、表单输入实时验证等。

```javascript
// 带防抖的请求
enhancedRequest.get('/api/search', { keyword: searchText }, {
  useDebounce: true,
  debounceWait: 500  // 等待500ms后才发起请求
});
```

### 4. 请求节流

适用场景：高频操作如滚动加载、按钮快速点击等。

```javascript
// 带节流的请求
enhancedRequest.get('/api/data', {}, {
  useThrottle: true,
  throttleLimit: 2000  // 2秒内只发起一次请求
});
```

### 5. 请求缓存

适用场景：短时间内多次请求相同数据、字典数据等不常变化的数据。

```javascript
// 带缓存的请求
enhancedRequest.get('/api/dictionary', {}, {
  useCache: true,
  cacheOptions: {
    maxAge: 300000,  // 缓存有效期5分钟
    cacheKey: (args) => `dictionary-${JSON.stringify(args[0].params)}`  // 自定义缓存键
  }
});

// 清除缓存
enhancedRequest.clearCache();  // 清除所有缓存
enhancedRequest.clearCache('dictionary-{"type":"status"}');  // 清除特定缓存
```

### 6. 请求超时控制

适用场景：对请求响应时间有严格要求的场景。

```javascript
// 带超时控制的请求
enhancedRequest.get('/api/data', {}, {
  useTimeout: true,
  timeoutMs: 5000  // 5秒超时
});
```

### 7. 请求取消

适用场景：搜索框输入过程中取消上一次请求、切换页面时取消未完成的请求。

```javascript
// 创建取消令牌
const cancelToken = enhancedRequest.createCancelToken();

// 使用取消令牌发起请求
enhancedRequest.get('/api/search', { keyword: searchText }, {
  cancelToken: cancelToken.token
});

// 取消请求
cancelToken.cancel('用户取消了请求');

// 判断请求是否被取消
try {
  await enhancedRequest.get('/api/data', {}, { cancelToken: token });
} catch (error) {
  if (enhancedRequest.isRequestCancelled(error)) {
    console.log('请求被取消了');
  } else {
    console.error('请求失败:', error);
  }
}
```

### 8. 批量请求

适用场景：需要同时发起多个请求并等待所有结果。

```javascript
// 批量处理请求
const requestFns = [
  () => enhancedRequest.get('/api/users'),
  () => enhancedRequest.get('/api/products'),
  () => enhancedRequest.get('/api/orders')
];

// 并行执行，但限制并发数为2
enhancedRequest.batchRequests(requestFns, {
  parallel: true,
  concurrency: 2
}).then(results => {
  const [users, products, orders] = results;
  console.log('所有数据加载完成', users, products, orders);
});

// 串行执行
enhancedRequest.batchRequests(requestFns, { parallel: false })
  .then(results => {
    console.log('串行请求完成', results);
  });
```

### 9. Mock数据

适用场景：前端开发阶段，后端API尚未完成时。

```javascript
// 创建Mock请求
const mockUserApi = enhancedRequest.createMockRequest({
  id: 1,
  name: '测试用户',
  role: 'admin'
}, 300);  // 模拟300ms延迟

// 使用Mock请求
mockUserApi().then(res => {
  console.log('模拟用户数据:', res.data);
});

// 动态生成Mock数据
const mockListApi = enhancedRequest.createMockRequest((params) => {
  const { page = 1, pageSize = 10 } = params;
  const list = [];
  for (let i = 0; i < pageSize; i++) {
    list.push({
      id: (page - 1) * pageSize + i + 1,
      name: `Item ${(page - 1) * pageSize + i + 1}`,
      status: Math.random() > 0.5 ? 'active' : 'inactive'
    });
  }
  return {
    list,
    total: 100,
    page,
    pageSize
  };
});

// 使用动态Mock数据
mockListApi({ page: 2, pageSize: 5 }).then(res => {
  console.log('模拟列表数据:', res.data);
});
```

## 在现有API模块中使用

可以在现有的API模块中集成增强功能：

```javascript
import enhancedRequest from '../utils/enhancedRequest';

// 设备管理相关接口
export const equipmentApi = {
  // 获取设备列表 (带缓存)
  getList(params) {
    return enhancedRequest({
      url: '/equipment/equipment/',
      method: 'get',
      params
    }, {
      useCache: true,
      cacheOptions: {
        maxAge: 60000,  // 缓存1分钟
        cacheKey: () => `equipment-list-${JSON.stringify(params)}`
      }
    });
  },
  
  // 获取设备详情 (带重试)
  getDetail(id) {
    return enhancedRequest({
      url: `/equipment/equipment/${id}/`,
      method: 'get'
    }, {
      useRetry: true,
      retryOptions: {
        retries: 2,
        retryDelay: 1000
      }
    });
  },
  
  // 创建设备 (带超时控制)
  create(data) {
    return enhancedRequest({
      url: '/equipment/equipment/',
      method: 'post',
      data
    }, {
      useTimeout: true,
      timeoutMs: 8000
    });
  },
  
  // 搜索设备 (带防抖)
  search(keyword) {
    return enhancedRequest.get('/equipment/equipment/search/', { keyword }, {
      useDebounce: true,
      debounceWait: 500
    });
  },
  
  // 获取故障记录 (带节流)
  getFaultRecords(params) {
    return enhancedRequest({
      url: '/equipment/fault-records/',
      method: 'get',
      params
    }, {
      useThrottle: true,