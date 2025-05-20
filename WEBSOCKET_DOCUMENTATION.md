# WebSocket服务文档

本文档详细说明了系统中WebSocket服务的实现和使用方法，用于支持实时更新功能。

## 基础信息

**WebSocket URL**: `wss://yagtpotihswf.sealosbja.site/ws/notifications/`

**认证方式**: JWT (JSON Web Token)

所有WebSocket连接都需要在查询参数中包含有效的JWT令牌：

```
wss://yagtpotihswf.sealosbja.site/ws/notifications/?token=<your_jwt_token>
```

## 功能概述

WebSocket服务提供以下实时更新功能：

1. **通知推送**: 当系统创建新通知时，相关用户会立即收到通知。
2. **系统告警**: 当系统产生新告警时，所有用户会立即收到告警信息。
3. **订单状态更新**: 当订单状态发生变化时，相关用户会立即收到更新信息。
4. **物料库存更新**: 当物料库存发生变化时，相关用户会立即收到更新信息。

## 消息格式

### 服务器发送的消息

服务器发送的所有消息都遵循以下JSON格式：

```json
{
  "type": "消息类型",
  "data": {
    // 消息内容，根据type不同而不同
  }
}
```

### 消息类型

#### 1. 通知消息 (notification)

```json
{
  "type": "notification",
  "data": {
    "id": "通知ID",
    "title": "通知标题",
    "content": "通知内容",
    "type": "通知类型",
    "is_read": false,
    "created_at": "创建时间"
  }
}
```

#### 2. 系统告警 (alert)

```json
{
  "type": "alert",
  "data": {
    "id": "告警ID",
    "title": "告警标题",
    "content": "告警内容",
    "severity": "严重程度",
    "status": "告警状态",
    "created_at": "创建时间"
  }
}
```

#### 3. 订单更新 (order_update)

```json
{
  "type": "order_update",
  "data": {
    "id": "订单ID",
    "order_no": "订单编号",
    "status": "订单状态",
    "updated_at": "更新时间"
  }
}
```

#### 4. 物料更新 (material_update)

```json
{
  "type": "material_update",
  "data": {
    "id": "物料ID",
    "code": "物料编码",
    "name": "物料名称",
    "stock_quantity": "库存数量",
    "updated_at": "更新时间"
  }
}
```

### 客户端发送的消息

客户端可以发送以下类型的消息：

#### 1. Ping消息

```json
{
  "type": "ping"
}
```

服务器会响应：

```json
{
  "type": "pong",
  "timestamp": "当前时间戳"
}
```

#### 2. 订阅特定频道

```json
{
  "type": "subscribe",
  "channels": ["notifications", "alerts", "orders"]
}
```

服务器会响应：

```json
{
  "type": "subscription_success",
  "channels": ["notifications", "alerts", "orders"]
}
```

## 前端集成示例

### 建立连接

```javascript
// 获取JWT令牌
const token = localStorage.getItem('token');

// 创建WebSocket连接
const socket = new WebSocket(`wss://yagtpotihswf.sealosbja.site/ws/notifications/?token=${token}`);

// 连接打开时的处理
socket.onopen = (event) => {
  console.log('WebSocket连接已建立');
  
  // 订阅频道
  socket.send(JSON.stringify({
    type: 'subscribe',
    channels: ['notifications', 'alerts', 'orders']
  }));
};

// 接收消息的处理
socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'notification':
      // 处理新通知
      handleNewNotification(message.data);
      break;
    case 'alert':
      // 处理系统告警
      handleSystemAlert(message.data);
      break;
    case 'order_update':
      // 处理订单更新
      handleOrderUpdate(message.data);
      break;
    case 'material_update':
      // 处理物料更新
      handleMaterialUpdate(message.data);
      break;
    case 'pong':
      // 处理pong响应
      console.log('收到pong响应:', message.timestamp);
      break;
    case 'subscription_success':
      // 处理订阅成功
      console.log('成功订阅频道:', message.channels);
      break;
    case 'error':
      // 处理错误
      console.error('WebSocket错误:', message.message);
      break;
    default:
      console.log('未知消息类型:', message);
  }
};

// 连接关闭时的处理
socket.onclose = (event) => {
  console.log('WebSocket连接已关闭:', event.code, event.reason);
  
  // 可以在这里实现重连逻辑
  if (event.code !== 1000) {
    setTimeout(() => {
      // 重新连接
      console.log('尝试重新连接...');
      // 重新初始化WebSocket连接
    }, 5000); // 5秒后重试
  }
};

// 发生错误时的处理
socket.onerror = (error) => {
  console.error('WebSocket错误:', error);
};

// 定期发送ping以保持连接活跃
setInterval(() => {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: 'ping' }));
  }
}, 30000); // 每30秒发送一次
```

### 处理消息示例

```javascript
// 处理新通知
function handleNewNotification(notification) {
  // 更新通知计数
  updateNotificationCount();
  
  // 显示通知提醒
  showNotificationToast(notification);
  
  // 如果用户当前在通知页面，更新通知列表
  if (window.location.pathname === '/notifications') {
    addNotificationToList(notification);
  }
}

// 处理系统告警
function handleSystemAlert(alert) {
  // 显示告警提醒
  showAlertToast(alert);
  
  // 如果是高严重性告警，可能需要特殊处理
  if (alert.severity === 'critical') {
    playAlertSound();
  }
}

// 处理订单更新
function handleOrderUpdate(order) {
  // 如果用户当前在订单详情页面，更新订单状态
  const currentOrderId = getCurrentOrderId();
  if (currentOrderId === order.id) {
    updateOrderStatus(order.status);
  }
  
  // 如果用户当前在订单列表页面，更新列表项
  if (window.location.pathname === '/orders') {
    updateOrderInList(order);
  }
}
```

## 实现细节

### 后端实现

WebSocket服务使用Django Channels框架实现，主要包括以下组件：

1. **消费者(Consumer)**: 处理WebSocket连接、消息接收和发送。
2. **路由(Routing)**: 定义WebSocket URL路径与消费者的映射关系。
3. **信号处理器(Signal Handlers)**: 监听模型变化，并通过WebSocket发送更新。

### 数据库模型

系统使用以下模型来跟踪WebSocket会话和消息：

1. **WebSocketSession**: 记录用户的WebSocket连接会话信息。
2. **WebSocketMessage**: 记录通过WebSocket发送和接收的消息。

### 安全性考虑

1. **认证**: 所有WebSocket连接都需要有效的JWT令牌。
2. **授权**: 用户只能接收与其相关的消息。
3. **消息验证**: 所有接收的消息都经过格式验证。
4. **速率限制**: 防止客户端发送过多消息导致服务器过载。

## 部署和扩展

WebSocket服务使用Redis作为Channel Layer，支持多实例部署和水平扩展：

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

在生产环境中，可以配置Redis集群以提高可用性和性能。

## 监控和调试

系统提供了WebSocket会话和消息的管理界面，可以通过以下API进行访问：

```
GET /api/developer/websocket-sessions/
GET /api/developer/websocket-messages/
```

这些API提供了对WebSocket连接和消息的监控和调试功能，仅供开发人员使用。

## 已知问题和限制

1. 当前WebSocket实现不支持消息持久化，如果客户端离线，将无法接收离线期间的消息。
2. 长时间空闲的连接可能会被代理服务器关闭，客户端需要实现重连机制。
3. 大量并发连接可能需要调整服务器和Redis配置以优化性能。

## 未来计划

1. 实现消息持久化，支持离线消息同步。
2. 添加消息确认机制，确保重要消息被客户端接收。
3. 实现更细粒度的订阅机制，允许客户端只订阅特定类型的消息。
4. 添加WebSocket连接和消息的详细监控指标。
