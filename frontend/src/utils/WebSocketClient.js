/**
 * WebSocket客户端
 * 处理与后端的WebSocket连接
 */

class WebSocketClient {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectTimeout = null;
    this.messageCallbacks = [];
    this.connectionCallbacks = [];
    this.errorCallbacks = [];
    
    // 使用环境变量中的WebSocket地址
    this.wsUrl = process.env.REACT_APP_WS_URL || 'wss://yagtpotihswf.sealosbja.site/ws';
    
    // 确保WebSocket URL不包含额外的端口号
    if (this.wsUrl.includes(':3000/ws')) {
      this.wsUrl = this.wsUrl.replace(':3000/ws', '/ws');
    }
    
    // 记录WebSocket地址到控制台，便于调试
    console.log('WebSocket URL configured as:', this.wsUrl);
  }

  /**
   * 连接到WebSocket服务器
   */
  connect() {
    if (this.socket && (this.socket.readyState === WebSocket.CONNECTING || this.socket.readyState === WebSocket.OPEN)) {
      console.log('WebSocket已连接或正在连接中');
      return;
    }

    try {
      console.log('正在连接WebSocket:', this.wsUrl);
      this.socket = new WebSocket(this.wsUrl);
      
      this.socket.onopen = () => {
        console.log('WebSocket连接已建立');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this._notifyConnectionCallbacks(true);
      };

      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this._notifyMessageCallbacks(message);
        } catch (error) {
          console.error('解析WebSocket消息出错:', error);
        }
      };

      this.socket.onclose = (event) => {
        console.log('WebSocket连接已关闭', event.code, event.reason);
        this.isConnected = false;
        this._notifyConnectionCallbacks(false);
        
        // 尝试重连
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
          console.log(`WebSocket将在${delay}ms后重连，尝试次数: ${this.reconnectAttempts}`);
          
          this.reconnectTimeout = setTimeout(() => {
            this.connect();
          }, delay);
        } else {
          console.error('WebSocket重连失败，已达最大尝试次数');
          this._notifyErrorCallbacks('重连失败');
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket发生错误:', error);
        this._notifyErrorCallbacks(error);
      };
    } catch (error) {
      console.error('创建WebSocket连接失败:', error);
      this._notifyErrorCallbacks(error);
    }
  }

  /**
   * 断开WebSocket连接
   */
  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
    }
  }

  /**
   * 发送消息到WebSocket服务器
   * @param {Object} data - 要发送的数据对象
   * @returns {boolean} - 发送是否成功
   */
  sendMessage(data) {
    if (!this.isConnected || !this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket未连接，无法发送消息');
      return false;
    }

    try {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(message);
      return true;
    } catch (error) {
      console.error('发送WebSocket消息失败:', error);
      return false;
    }
  }

  /**
   * 添加消息处理回调
   * @param {Function} callback - 消息处理回调函数
   */
  onMessage(callback) {
    if (typeof callback === 'function' && !this.messageCallbacks.includes(callback)) {
      this.messageCallbacks.push(callback);
    }
  }

  /**
   * 添加连接状态回调
   * @param {Function} callback - 连接状态回调函数
   */
  onConnectionChange(callback) {
    if (typeof callback === 'function' && !this.connectionCallbacks.includes(callback)) {
      this.connectionCallbacks.push(callback);
    }
  }

  /**
   * 添加错误处理回调
   * @param {Function} callback - 错误处理回调函数
   */
  onError(callback) {
    if (typeof callback === 'function' && !this.errorCallbacks.includes(callback)) {
      this.errorCallbacks.push(callback);
    }
  }

  /**
   * 移除消息处理回调
   * @param {Function} callback - 要移除的回调函数
   */
  removeMessageCallback(callback) {
    const index = this.messageCallbacks.indexOf(callback);
    if (index !== -1) {
      this.messageCallbacks.splice(index, 1);
    }
  }

  /**
   * 通知所有消息回调
   * @param {Object} message - 收到的消息
   * @private
   */
  _notifyMessageCallbacks(message) {
    this.messageCallbacks.forEach(callback => {
      try {
        callback(message);
      } catch (error) {
        console.error('执行消息回调时出错:', error);
      }
    });
  }

  /**
   * 通知所有连接状态回调
   * @param {boolean} isConnected - 连接状态
   * @private
   */
  _notifyConnectionCallbacks(isConnected) {
    this.connectionCallbacks.forEach(callback => {
      try {
        callback(isConnected);
      } catch (error) {
        console.error('执行连接状态回调时出错:', error);
      }
    });
  }

  /**
   * 通知所有错误回调
   * @param {Error} error - 错误信息
   * @private
   */
  _notifyErrorCallbacks(error) {
    this.errorCallbacks.forEach(callback => {
      try {
        callback(error);
      } catch (err) {
        console.error('执行错误回调时出错:', err);
      }
    });
  }
}

// 导出单例实例
const wsClient = new WebSocketClient();
export default wsClient;
