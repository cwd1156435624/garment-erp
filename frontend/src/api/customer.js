import request from '../utils/request';

// 客户管理相关接口
export const customerApi = {
  // 获取客户列表
  getList(params) {
    return request({
      url: '/customer/customers/',
      method: 'get',
      params
    });
  },

  // 获取客户详情
  getDetail(id) {
    return request({
      url: `/customer/customers/${id}/`,
      method: 'get'
    });
  },

  // 创建客户
  create(data) {
    return request({
      url: '/customer/customers/',
      method: 'post',
      data
    });
  },

  // 更新客户信息
  update(id, data) {
    return request({
      url: `/customer/customers/${id}/`,
      method: 'put',
      data
    });
  },

  // 删除客户
  delete(id) {
    return request({
      url: `/customer/customers/${id}/`,
      method: 'delete'
    });
  },

  // 获取客户订单历史
  getOrderHistory(customerId, params) {
    return request({
      url: `/customer/customers/${customerId}/orders/`,
      method: 'get',
      params
    });
  },

  // 获取客户统计信息
  getStatistics(customerId) {
    return request({
      url: `/customer/customers/${customerId}/statistics/`,
      method: 'get'
    });
  },
  
  // 更新客户信用额度
  updateCreditLimit(customerId, data) {
    return request({
      url: `/customer/customers/${customerId}/update_credit_limit/`,
      method: 'post',
      data
    });
  }
};