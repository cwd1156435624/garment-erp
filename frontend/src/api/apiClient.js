import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'https://yagtpotihswf.sealosbja.site/api',
  headers: {
    'Content-Type': 'application/json',
  },
  // 允许跨域请求携带凭证
  withCredentials: true,
});

// 输出配置的baseURL信息，便于调试
console.log('Axios baseURL configured as:', apiClient.defaults.baseURL);

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
