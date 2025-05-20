import request from '../utils/request';

/**
 * 系统公告 API 服务
 */

// 获取所有公告
export function getNotices(params) {
  return request({
    url: '/api/system/notices/',
    method: 'get',
    params
  });
}

// 获取公告详情
export function getNoticeDetail(id) {
  return request({
    url: `/api/system/notices/${id}/`,
    method: 'get'
  });
}

// 创建公告
export function createNotice(data) {
  return request({
    url: '/api/system/notices/',
    method: 'post',
    data
  });
}

// 更新公告
export function updateNotice(id, data) {
  return request({
    url: `/api/system/notices/${id}/`,
    method: 'put',
    data
  });
}

// 删除公告
export function deleteNotice(id) {
  return request({
    url: `/api/system/notices/${id}/`,
    method: 'delete'
  });
}

// 标记公告为已读
export function markNoticeAsRead(id) {
  return request({
    url: `/api/system/notices/${id}/mark_as_read/`,
    method: 'post'
  });
}

// 获取未读公告
export function getUnreadNotices(params) {
  return request({
    url: '/api/system/notices/unread/',
    method: 'get',
    params
  });
}

// 获取当前有效的公告
export function getActiveNotices(params) {
  return request({
    url: '/api/system/notices/active/',
    method: 'get',
    params
  });
}
