import apiClient from '../apiClient';
import authService from '../authService';

export const designFileService = {
  // 获取设计文件列表
  getDesignFiles: async (params = {}) => {
    const response = await apiClient.get('/design-files/', { params });
    return response.data;
  },
  
  // 获取单个设计文件
  getDesignFile: async (id) => {
    const response = await apiClient.get(`/design-files/${id}/`);
    return response.data;
  },
  
  // 创建设计文件
  createDesignFile: async (data) => {
    try {
      // 创建数据的副本，避免修改原始对象
      const designData = { ...data };
      console.log('[Debug] Received data in createDesignFile:', JSON.stringify(designData)); // <-- Log 1: Original data

      // ---- Add created_by ----
      const userInfo = authService.getCurrentUser(); // Get user info
      console.log('[Debug] UserInfo from authService:', userInfo); // <-- Log 2: User info object
      if (userInfo && userInfo.id) {
        designData.created_by = userInfo.id; // Add user ID
        console.log('[Debug] Added created_by:', userInfo.id); // <-- Log 3: Log added ID
      } else {
        // Handle case where user info is not available (e.g., not logged in)
        console.error('User ID not available for created_by field.');
        // Optionally, throw an error or handle appropriately
        // throw new Error('User is not logged in.'); 
      }
      // ------------------------
      console.log('[Debug] Data after adding created_by:', JSON.stringify(designData)); // <-- Log 4: Data after adding ID

      // 确保URL字段格式正确
      if (designData.file_url) {
        console.log('[Debug] file_url exists:', designData.file_url); // <-- Log 5: Check file_url
        // 如果URL不是以http开头，则添加基础URL
        if (!designData.file_url.startsWith('http')) {
          console.log('[Debug] file_url does not start with http. Trying to prepend base URL.'); // <-- Log 6
          const baseUrl = process.env.REACT_APP_API_BASE_URL || 'fallback-if-env-missing'; // Use REACT_APP_API_BASE_URL
          console.log('[Debug] Base URL from env:', baseUrl); // <-- Log 7: Check base URL value
          // Make sure baseUrl doesn't end with / and file_url starts with /
          const formattedBaseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
          const formattedFileUrl = designData.file_url.startsWith('/') ? designData.file_url : '/' + designData.file_url;
          designData.file_url = `${formattedBaseUrl}${formattedFileUrl}`; 
          console.log('[Debug] Constructed absolute file_url:', designData.file_url); // <-- Log 8: Show constructed URL
        }
        
        // 确保URL是有效的
        try {
          new URL(designData.file_url);
        } catch (e) {
          console.error('无效的URL格式:', designData.file_url);
          throw new Error(`无效的URL格式: ${designData.file_url}`);
        }
      }
      
      console.log('发送到服务器的设计稿数据:', designData);
      
      // 发送请求到正确的端点
      const response = await apiClient.post('/design-files/', designData);
      return response.data;
    } catch (error) {
      console.error('创建设计稿失败:', error);
      // 添加详细的错误日志
      if (error.response) {
        console.error('错误响应详情:', error.response.data);
        // 如果是验证错误，提供更友好的错误信息
        if (error.response.status === 400) {
          const errorData = error.response.data;
          let errorMessage = '验证错误:';
          
          // 处理常见的验证错误
          if (errorData.file_url) {
            errorMessage += ` 文件URL: ${errorData.file_url.join(', ')}`;
          }
          if (errorData.created_by) {
            errorMessage += ` 创建者: ${errorData.created_by.join(', ')}`;
          }
          
          error.friendlyMessage = errorMessage;
        }
      }
      throw error;
    }
  },
  
  // 更新设计文件
  updateDesignFile: async (id, data) => {
    const response = await apiClient.put(`/design-files/${id}/`, data);
    return response.data;
  },
  
  // 删除设计文件
  deleteDesignFile: async (id) => {
    const response = await apiClient.delete(`/design-files/${id}/`);
    return response.data;
  },
  
  // 上传设计文件
  uploadDesignFile: async (file, fileName = null, fileType = null) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      if (fileName) {
        formData.append('file_name', fileName);
      }
      
      if (fileType) {
        formData.append('file_type', fileType);
      }
      
      const response = await apiClient.post('/design-files/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      console.error('上传文件失败:', error);
      throw error;
    }
  },
  
  // 审批设计文件
  approveDesignFile: async (id, comment = '') => {
    const response = await apiClient.post(`/design-files/${id}/approve/`, { comment });
    return response.data;
  },
  
  // 拒绝设计文件
  rejectDesignFile: async (id, comment = '') => {
    const response = await apiClient.post(`/design-files/${id}/reject/`, { comment });
    return response.data;
  },
  
  // 发布设计文件
  publishDesignFile: async (id) => {
    const response = await apiClient.post(`/design-files/${id}/publish/`);
    return response.data;
  }
};

export default designFileService;
