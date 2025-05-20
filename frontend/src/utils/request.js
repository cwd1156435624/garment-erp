import axios from 'axios';
import { getCookie } from './auth';

// 打印环境变量，便于调试
console.log('REACT_APP_API_BASE_URL:', process.env.REACT_APP_API_BASE_URL);

const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000, // 增加超时时间到30秒
  withCredentials: true
});

// 打印实际使用的baseURL
console.log('Axios baseURL configured as:', api.defaults.baseURL);

// 请求拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  const csrfToken = getCookie('csrftoken');
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  
  return config;
}, error => {
  return Promise.reject(error);
});

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 记录响应数据结构，便于调试
    console.log('API Response:', response.config.url, response.data);
    
    // 如果响应中没有 results 字段，进行格式化处理
    if (response.data && !response.data.results) {
      // 如果是数组，包装成 {results, count} 格式
      if (Array.isArray(response.data)) {
        response.data = {
          results: response.data,
          count: response.data.length
        };
      } 
      // 如果是对象，包装成 {results: [data]} 格式，适用于单个订单详情等
      else if (typeof response.data === 'object' && !Array.isArray(response.data)) {
        // 如果URL包含特定关键词，执行相应的格式化
        const url = response.config.url || '';
        if (url.includes('/orders/') || url.includes('/notices/')) {
          // 对于订单和通知相关的API，将其包装成数组
          response.data = {
            results: [response.data],
            count: 1
          };
        }
      }
    }
    
    return response;
  },
  error => {
    // 记录详细错误信息
    console.error('Response Error:', error);
    
    // 直接将错误上报，不使用模拟数据
    // 这样可以确保前端与后端直接交互，使用真实API响应
    console.error('请求错误，错误码：', error.response?.status);
    console.error('请求URL：', error.config.url);
    console.error('请求方法：', error.config.method);
    
    // 处理其他错误
    if (error.response) {
      if (error.response.status === 401 && !error.config._retry) {
        error.config._retry = true;
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }
      
      if (error.response.status === 403) {
        window.location.href = '/403';
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;