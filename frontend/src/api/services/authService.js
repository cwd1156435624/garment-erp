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
