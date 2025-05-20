export const websocketService = {
  socket: null,
  
  connect: (token) => {
    const wsUrl = process.env.REACT_APP_WS_URL;
    if (!wsUrl) {
      console.error("错误：REACT_APP_WS_URL 环境变量未设置!");
      return;
    }
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
