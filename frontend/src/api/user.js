import request from '../utils/request';

// 用户管理相关接口
export const userApi = {
  // 用户登录
  login(data) {
    return request({
      url: '/api/users/login/',
      method: 'post',
      data
    });
  },

  // 用户注册
  register(data) {
    return request({
      url: '/api/users/',
      method: 'post',
      data
    });
  },

  // 获取用户信息
  getUserInfo() {
    return request({
      url: '/api/users/profile/',
      method: 'get'
    });
  },

  // 更新用户信息
  updateUserInfo(data) {
    const userId = data.id;
    return request({
      url: `/api/users/${userId}/`,
      method: 'put',
      data
    });
  },

  // 修改密码
  changePassword(data) {
    return request({
      url: '/api/users/change_password/',
      method: 'post',
      data
    });
  },

  // 重置密码
  resetPassword(userId, data) {
    return request({
      url: `/api/users/${userId}/reset_password/`,
      method: 'post',
      data
    });
  },

  // 获取用户列表
  getList(params) {
    return request({
      url: '/api/users/',
      method: 'get',
      params
    });
  },

  // 获取用户详情
  getDetail(id) {
    return request({
      url: `/api/users/${id}/`,
      method: 'get'
    });
  },

  // 创建用户
  create(data) {
    return request({
      url: '/api/users/',
      method: 'post',
      data
    });
  },

  // 更新用户
  update(id, data) {
    return request({
      url: `/api/users/${id}/`,
      method: 'put',
      data
    });
  },

  // 删除用户
  delete(id) {
    return request({
      url: `/api/users/${id}/`,
      method: 'delete'
    });
  },

  // 获取用户权限列表
  getPermissions() {
    return request({
      url: '/api/users/permissions/',
      method: 'get'
    });
  },

  // 更新用户权限
  updatePermissions(userId, data) {
    return request({
      url: `/api/users/${userId}/permissions/`,
      method: 'put',
      data
    });
  },
  
  // 审核用户注册
  approveUser(userId) {
    return request({
      url: `/api/users/${userId}/approve/`,
      method: 'post'
    });
  },
  
  // 获取待审核用户列表
  getPendingUsers(params) {
    return request({
      url: '/api/users/pending/',
      method: 'get',
      params
    });
  }
};