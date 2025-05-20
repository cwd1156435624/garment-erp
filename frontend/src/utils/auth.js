// Token相关的工具函数

// Token的key
const TokenKey = 'token';

// 获取token
export function getToken() {
  return localStorage.getItem(TokenKey);
}

// 设置token
export function setToken(token) {
  return localStorage.setItem(TokenKey, token);
}

// 移除token
export function removeToken() {
  return localStorage.removeItem(TokenKey);
}