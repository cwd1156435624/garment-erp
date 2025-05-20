import apiClient from '../apiClient';

export const materialService = {
  // 获取材料列表
  getMaterials: async (params = {}) => {
    try {
      const response = await apiClient.get('/materials/', { params });
      return response.data;
    } catch (error) {
      console.error('获取材料列表失败:', error);
      
      // 处理500错误，返回空数据而不是抛出异常
      if (error.response && error.response.status === 500) {
        console.warn('服务器内部错误，返回空数据');
        return { 
          results: [], 
          count: 0,
          next: null,
          previous: null
        };
      }
      
      throw error;
    }
  },
  
  // 获取单个材料
  getMaterial: async (id) => {
    try {
      const response = await apiClient.get(`/materials/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`获取材料(ID:${id})失败:`, error);
      throw error;
    }
  },
  
  // 创建材料
  createMaterial: async (data) => {
    try {
      const response = await apiClient.post('/materials/', data);
      return response.data;
    } catch (error) {
      console.error('创建材料失败:', error);
      if (error.response) {
        console.error('错误响应详情:', error.response.data);
      }
      throw error;
    }
  },
  
  // 更新材料
  updateMaterial: async (id, data) => {
    try {
      const response = await apiClient.put(`/materials/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error(`更新材料(ID:${id})失败:`, error);
      if (error.response) {
        console.error('错误响应详情:', error.response.data);
      }
      throw error;
    }
  },
  
  // 删除材料
  deleteMaterial: async (id) => {
    try {
      const response = await apiClient.delete(`/materials/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`删除材料(ID:${id})失败:`, error);
      throw error;
    }
  },
  
  // 获取库位列表
  getLocations: async (params = {}) => {
    try {
      const response = await apiClient.get('/locations/', { params });
      return response.data;
    } catch (error) {
      console.error('获取库位列表失败:', error);
      
      // 处理500错误，返回空数据而不是抛出异常
      if (error.response && error.response.status === 500) {
        console.warn('服务器内部错误，返回空数据');
        return { 
          results: [], 
          count: 0,
          next: null,
          previous: null
        };
      }
      
      throw error;
    }
  },
  
  // 获取库存列表
  getInventory: async (params = {}) => {
    try {
      const response = await apiClient.get('/inventory/', { params });
      return response.data;
    } catch (error) {
      console.error('获取库存列表失败:', error);
      
      // 处理500错误，返回空数据而不是抛出异常
      if (error.response && error.response.status === 500) {
        console.warn('服务器内部错误，返回空数据');
        return { 
          results: [], 
          count: 0,
          next: null,
          previous: null
        };
      }
      
      throw error;
    }
  },
  
  // 获取供应商列表
  getSuppliers: async (params = {}) => {
    try {
      const response = await apiClient.get('/suppliers/', { params });
      return response.data;
    } catch (error) {
      console.error('获取供应商列表失败:', error);
      
      // 处理500错误，返回空数据而不是抛出异常
      if (error.response && error.response.status === 500) {
        console.warn('服务器内部错误，返回空数据');
        return { 
          results: [], 
          count: 0,
          next: null,
          previous: null
        };
      }
      
      throw error;
    }
  }
};

export default materialService;
