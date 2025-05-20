import request from '../utils/request';

/**
 * 开发者控制台 API 服务
 */

// 系统监控
export function getSystemMonitor() {
  return request({
    url: '/api/developer/system-monitor/',
    method: 'get'
  });
}

// 获取系统监控历史数据
export function getSystemMonitorHistory(params) {
  return request({
    url: '/api/developer/system-monitor/history/',
    method: 'get',
    params
  });
}

// API指标
export function getApiMetrics(params) {
  return request({
    url: '/api/developer/api-metrics/',
    method: 'get',
    params
  });
}

// 获取API指标详情
export function getApiMetricDetail(id) {
  return request({
    url: `/api/developer/api-metrics/${id}/`,
    method: 'get'
  });
}

// 系统日志
export function getSystemLogs(params) {
  return request({
    url: '/api/developer/system-logs/',
    method: 'get',
    params
  });
}

// 获取系统日志详情
export function getSystemLogDetail(id) {
  return request({
    url: `/api/developer/system-logs/${id}/`,
    method: 'get'
  });
}

// 配置管理
export function getConfigItems(params) {
  return request({
    url: '/api/developer/config/',
    method: 'get',
    params
  });
}

// 获取配置项详情
export function getConfigItemDetail(id) {
  return request({
    url: `/api/developer/config/${id}/`,
    method: 'get'
  });
}

// 创建配置项
export function createConfigItem(data) {
  return request({
    url: '/api/developer/config/',
    method: 'post',
    data
  });
}

// 更新配置项
export function updateConfigItem(id, data) {
  return request({
    url: `/api/developer/config/${id}/`,
    method: 'put',
    data
  });
}

// 删除配置项
export function deleteConfigItem(id) {
  return request({
    url: `/api/developer/config/${id}/`,
    method: 'delete'
  });
}

// WebSocket会话
export function getWebSocketSessions(params) {
  return request({
    url: '/api/developer/websocket-sessions/',
    method: 'get',
    params
  });
}

// 获取WebSocket会话详情
export function getWebSocketSessionDetail(id) {
  return request({
    url: `/api/developer/websocket-sessions/${id}/`,
    method: 'get'
  });
}

// WebSocket消息
export function getWebSocketMessages(params) {
  return request({
    url: '/api/developer/websocket-messages/',
    method: 'get',
    params
  });
}

// 获取WebSocket消息详情
export function getWebSocketMessageDetail(id) {
  return request({
    url: `/api/developer/websocket-messages/${id}/`,
    method: 'get'
  });
}
