import apiClient from '../apiClient';

export const userService = {
  // 获取用户列表
  getUsers: async (params = {}) => {
    const response = await apiClient.get('/users/', { params });
    return response.data;
  },
  
  // 获取单个用户
  getUser: async (id) => {
    const response = await apiClient.get(`/users/${id}/`);
    return response.data;
  },
  
  // 获取待审核用户
  getPendingUsers: async () => {
    const response = await apiClient.get('/users/pending/');
    return response.data;
  },
  
  // 审批用户
  approveUser: async (id) => {
    const response = await apiClient.post(`/users/${id}/approve/`);
    return response.data;
  },
  
  // 拒绝用户
  rejectUser: async (id, reason = '') => {
    const response = await apiClient.post(`/users/${id}/reject/`, { reason });
    return response.data;
  },
  
  // 更新用户
  updateUser: async (id, data) => {
    const response = await apiClient.put(`/users/${id}/`, data);
    return response.data;
  },
  
  // 删除用户
  deleteUser: async (id) => {
    const response = await apiClient.delete(`/users/${id}/`);
    return response.data;
  }
};

export default userService;
