# API 对接指南

## 基础信息

- **API 基础 URL**: `https://yagtpotihswf.sealosbja.site/api`
- **WebSocket URL**: `wss://yagtpotihswf.sealosbja.site:3000/ws`
- **认证方式**: JWT (JSON Web Token)

## 认证

所有API请求（除了登录和注册）都需要在请求头中包含JWT令牌：

```http
Authorization: Bearer <your_token>
```

### 获取令牌

**请求**：

```http
POST /token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**响应**：
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 刷新令牌

**请求**：

```http
POST /token/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

**响应**：
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 设计文件 API

### 获取设计文件列表

**请求**：

```http
GET /design-files/
Authorization: Bearer <your_token>
```

**响应**：
```json
[
  {
    "id": 1,
    "name": "设计稿名称",
    "version": "1.0",
    "status": "draft",
    "designer": 1,
    "designer_name": "设计师用户名",
    "description": "设计稿描述",
    "file_url": "https://yagtpotihswf.sealosbja.site/api/media/design_files/2025/04/06/filename.jpg",
    "file_name": "filename.jpg",
    "file_size": 919010,
    "file_type": "image/jpeg",
    "created_at": "2025-04-06T06:31:13Z",
    "updated_at": "2025-04-06T06:31:13Z"
  }
]
```

### 获取单个设计文件

**请求**：

```http
GET /design-files/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "id": 1,
  "name": "设计稿名称",
  "version": "1.0",
  "status": "draft",
  "designer": 1,
  "designer_name": "设计师用户名",
  "description": "设计稿描述",
  "file_url": "https://yagtpotihswf.sealosbja.site/api/media/design_files/2025/04/06/filename.jpg",
  "file_name": "filename.jpg",
  "file_size": 919010,
  "file_type": "image/jpeg",
  "created_at": "2025-04-06T06:31:13Z",
  "updated_at": "2025-04-06T06:31:13Z"
}
```

### 创建设计文件

**请求**：

```http
POST /design-files/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "name": "设计稿名称",
  "version": "1.0",
  "status": "draft",
  "description": "设计稿描述",
  "file_url": "https://yagtpotihswf.sealosbja.site/api/media/design_files/2025/04/06/filename.jpg",
  "file_name": "filename.jpg"
}
```

**响应**：
```json
{
  "id": 1,
  "name": "设计稿名称",
  "version": "1.0",
  "status": "draft",
  "designer": 1,
  "designer_name": "设计师用户名",
  "description": "设计稿描述",
  "file_url": "https://yagtpotihswf.sealosbja.site/api/media/design_files/2025/04/06/filename.jpg",
  "file_name": "filename.jpg",
  "file_size": 0,
  "file_type": null,
  "created_at": "2025-04-06T06:31:13Z",
  "updated_at": "2025-04-06T06:31:13Z"
}
```

### 更新设计文件

**请求**：

```http
PUT /design-files/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "name": "更新后的设计稿名称",
  "description": "更新后的描述"
}
```

**响应**：
```json
{
  "id": 1,
  "name": "更新后的设计稿名称",
  "version": "1.0",
  "status": "draft",
  "designer": 1,
  "designer_name": "设计师用户名",
  "description": "更新后的描述",
  "file_url": "https://yagtpotihswf.sealosbja.site/api/media/design_files/2025/04/06/filename.jpg",
  "file_name": "filename.jpg",
  "file_size": 919010,
  "file_type": "image/jpeg",
  "created_at": "2025-04-06T06:31:13Z",
  "updated_at": "2025-04-06T07:45:13Z"
}
```

### 删除设计文件

**请求**：

```http
DELETE /design-files/{id}/
Authorization: Bearer <your_token>
```

**响应**：
```
204 No Content
```

### 上传设计文件

**请求**：

```http
POST /design-files/upload/
Authorization: Bearer <your_token>
Content-Type: multipart/form-data

file: <file_data>
file_name: (可选) 文件名
file_type: (可选) 文件类型
```

**响应**：
```json
{
  "fileUrl": "/media/design_files/2025/04/06/filename.jpg",
  "filename": "filename.jpg",
  "originalFilename": "original_filename.jpg",
  "id": 12345678901234567890,
  "fileType": "image/jpeg",
  "size": 919010
}
```

### 审批设计文件

**请求**：

```http
POST /design-files/{id}/approve/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "comment": "审批意见"
}
```

**响应**：
```json
{
  "status": "approved"
}
```

### 拒绝设计文件

**请求**：

```http
POST /design-files/{id}/reject/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "comment": "拒绝原因"
}
```

**响应**：
```json
{
  "status": "rejected"
}
```

### 发布设计文件

**请求**：

```http
POST /design-files/{id}/publish/
Authorization: Bearer <your_token>
```

**响应**：
```json
{
  "status": "published"
}
```

## 用户 API

### 获取用户列表

**请求**：
```
GET /users/
Authorization: Bearer <your_token>
```

### 获取当前用户信息

**请求**：
```
GET /users/me/
Authorization: Bearer <your_token>
```

### 获取待审核用户

**请求**：
```
GET /users/pending/
Authorization: Bearer <your_token>
```

### 审批用户

**请求**：
```
POST /users/{id}/approve/
Authorization: Bearer <your_token>
```

## WebSocket 集成

### 连接 WebSocket

```javascript
const socket = new WebSocket('wss://yagtpotihswf.sealosbja.site:3000/ws');

socket.onopen = () => {
  console.log('WebSocket连接已建立');
  // 发送认证消息
  const token = localStorage.getItem('token');
  if (token) {
    socket.send(JSON.stringify({ type: 'authenticate', token }));
  }
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到WebSocket消息:', data);
};

socket.onerror = (error) => {
  console.error('WebSocket错误:', error);
};

socket.onclose = () => {
  console.log('WebSocket连接已关闭');
};
```

## 材料 API

### 获取材料列表

**请求**：

```http
GET /materials/materials/?page=1&page_size=10
Authorization: Bearer <your_token>
```

**响应**：

```json
{
  "count": 100,
  "next": "https://yagtpotihswf.sealosbja.site/api/materials/materials/?page=2&page_size=10",
  "previous": null,
  "results": [
    {
      "id": 1,
      "code": "M001",
      "name": "铝合金型材",
      "category": "金属材料",
      "unit": "米",
      "specifications": "100mm×50mm×2mm",
      "min_stock": 10,
      "max_stock": 100,
      "unit_price": "15.00",
      "status": "active",
      "status_display": "启用",
      "remarks": "常用材料",
      "created_at": "2025-04-06T06:31:13Z",
      "updated_at": "2025-04-06T06:31:13Z",
      "is_deleted": false
    }
  ]
}
```

### 获取单个材料

**请求**：

```http
GET /materials/materials/{id}/
Authorization: Bearer <your_token>
```

**响应**：

```json
{
  "id": 1,
  "code": "M001",
  "name": "铝合金型材",
  "category": "金属材料",
  "unit": "米",
  "specifications": "100mm×50mm×2mm",
  "min_stock": 10,
  "max_stock": 100,
  "unit_price": "15.00",
  "status": "active",
  "status_display": "启用",
  "remarks": "常用材料",
  "created_at": "2025-04-06T06:31:13Z",
  "updated_at": "2025-04-06T06:31:13Z",
  "is_deleted": false,
  "suppliers": [
    {
      "id": 1,
      "supplier": {
        "id": 1,
        "name": "供应商名称",
        "code": "S001"
      },
      "price": "14.50",
      "is_primary": true,
      "lead_time": 7,
      "min_order_quantity": 10
    }
  ]
}
```

### 创建材料

**请求**：

```http
POST /materials/materials/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "code": "M002",
  "name": "不锈钢板",
  "category": "金属材料",
  "unit": "张",
  "specifications": "1000mm×2000mm×1.5mm",
  "min_stock": 5,
  "max_stock": 50,
  "unit_price": "120.00",
  "status": "active",
  "remarks": "耐腐蚀材料"
}
```

**响应**：

```json
{
  "id": 2,
  "code": "M002",
  "name": "不锈钢板",
  "category": "金属材料",
  "unit": "张",
  "specifications": "1000mm×2000mm×1.5mm",
  "min_stock": 5,
  "max_stock": 50,
  "unit_price": "120.00",
  "status": "active",
  "status_display": "启用",
  "remarks": "耐腐蚀材料",
  "created_at": "2025-04-07T08:45:22Z",
  "updated_at": "2025-04-07T08:45:22Z",
  "is_deleted": false
}
```

### 更新材料

**请求**：

```http
PUT /materials/materials/{id}/
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "name": "304不锈钢板",
  "specifications": "1000mm×2000mm×2mm",
  "unit_price": "150.00"
}
```

**响应**：

```json
{
  "id": 2,
  "code": "M002",
  "name": "304不锈钢板",
  "category": "金属材料",
  "unit": "张",
  "specifications": "1000mm×2000mm×2mm",
  "min_stock": 5,
  "max_stock": 50,
  "unit_price": "150.00",
  "status": "active",
  "status_display": "启用",
  "remarks": "耐腐蚀材料",
  "created_at": "2025-04-07T08:45:22Z",
  "updated_at": "2025-04-07T09:15:30Z",
  "is_deleted": false
}
```

### 删除材料

**请求**：

```http
DELETE /materials/materials/{id}/
Authorization: Bearer <your_token>
```

**响应**：

```
204 No Content
```

## 前端集成示例

### API 客户端


```javascript
// apiClient.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'https://yagtpotihswf.sealosbja.site/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加JWT令牌
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器 - 处理常见错误
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // 处理401未授权错误
    if (error.response && error.response.status === 401) {
      // 清除无效令牌
      localStorage.removeItem('token');
      // 可以在这里添加重定向到登录页面的逻辑
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 设计文件服务


```javascript
// designFileService.js
import apiClient from '../apiClient';

export const designFileService = {
  // 获取设计文件列表
  getDesignFiles: async (params = {}) => {
    const response = await apiClient.get('/design-files/', { params });
    return response.data;
  },
  
  // 获取单个设计文件
  getDesignFile: async (id) => {
    const response = await apiClient.get(`/design-files/${id}/`);
    return response.data;
  },
  
  // 创建设计文件
  createDesignFile: async (data) => {
    try {
      // 确保URL字段格式正确
      if (data.file_url && !data.file_url.startsWith('http')) {
        // 构造完整URL
        const baseUrl = process.env.REACT_APP_API_URL || 'https://yagtpotihswf.sealosbja.site/api';
        data.file_url = `${baseUrl}${data.file_url.startsWith('/') ? '' : '/'}${data.file_url}`;
      }
      
      const response = await apiClient.post('/design-files/', data);
      return response.data;
    } catch (error) {
      console.error('创建设计稿失败:', error);
      // 添加详细的错误日志
      if (error.response) {
        console.error('错误响应详情:', error.response.data);
      }
      throw error;
    }
  },
  
  // 更新设计文件
  updateDesignFile: async (id, data) => {
    const response = await apiClient.put(`/design-files/${id}/`, data);
    return response.data;
  },
  
  // 删除设计文件
  deleteDesignFile: async (id) => {
    const response = await apiClient.delete(`/design-files/${id}/`);
    return response.data;
  },
  
  // 上传设计文件
  uploadDesignFile: async (file, fileName = null, fileType = null) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      if (fileName) {
        formData.append('file_name', fileName);
      }
      
      if (fileType) {
        formData.append('file_type', fileType);
      }
      
      const response = await apiClient.post('/design-files/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      console.error('上传文件失败:', error);
      throw error;
    }
  },
  
  // 审批设计文件
  approveDesignFile: async (id, comment = '') => {
    const response = await apiClient.post(`/design-files/${id}/approve/`, { comment });
    return response.data;
  },
  
  // 拒绝设计文件
  rejectDesignFile: async (id, comment = '') => {
    const response = await apiClient.post(`/design-files/${id}/reject/`, { comment });
    return response.data;
  },
  
  // 发布设计文件
  publishDesignFile: async (id) => {
    const response = await apiClient.post(`/design-files/${id}/publish/`);
    return response.data;
  }
};

export default designFileService;
```

### 认证服务


```javascript
// authService.js
import apiClient from '../apiClient';

export const authService = {
  // 用户登录
  login: async (username, password) => {
    const response = await apiClient.post('/token/', { username, password });
    // 保存JWT令牌
    if (response.data.access) {
      localStorage.setItem('token', response.data.access);
      // 如果有刷新令牌，也保存它
      if (response.data.refresh) {
        localStorage.setItem('refreshToken', response.data.refresh);
      }
    }
    return response.data;
  },
  
  // 用户注册
  register: async (userData) => {
    const response = await apiClient.post('/users/', userData);
    return response.data;
  },
  
  // 刷新令牌
  refreshToken: async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    const response = await apiClient.post('/token/refresh/', { refresh: refreshToken });
    if (response.data.access) {
      localStorage.setItem('token', response.data.access);
    }
    return response.data;
  },
  
  // 登出
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  },
  
  // 获取当前用户信息
  getCurrentUser: async () => {
    const response = await apiClient.get('/users/me/');
    return response.data;
  },
  
  // 检查是否已认证
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  }
};

export default authService;
```

### WebSocket 服务


```javascript
// websocketService.js
export const websocketService = {
  socket: null,
  
  connect: (token) => {
    const wsUrl = process.env.REACT_APP_WS_URL || 'wss://yagtpotihswf.sealosbja.site:3000/ws';
    websocketService.socket = new WebSocket(wsUrl);
    
    websocketService.socket.onopen = () => {
      console.log('WebSocket连接已建立');
      // 发送认证消息
      if (token) {
        websocketService.socket.send(JSON.stringify({ type: 'authenticate', token }));
      }
    };
    
    websocketService.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // 处理不同类型的消息
      console.log('收到WebSocket消息:', data);
      // 这里可以添加事件分发逻辑
    };
    
    websocketService.socket.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };
    
    websocketService.socket.onclose = () => {
      console.log('WebSocket连接已关闭');
    };
  },
  
  disconnect: () => {
    if (websocketService.socket) {
      websocketService.socket.close();
    }
  },
  
  send: (message) => {
    if (websocketService.socket && websocketService.socket.readyState === WebSocket.OPEN) {
      websocketService.socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket未连接，无法发送消息');
    }
  }
};

export default websocketService;
```
