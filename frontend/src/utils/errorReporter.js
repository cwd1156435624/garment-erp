import axios from 'axios';

/**
 * 错误报告工具
 * 用于捕获、格式化和上报前端错误
 */

// 存储错误信息
const errorStore = [];

// 错误类型枚举
export const ErrorTypes = {
  API_ERROR: 'api_error',      // API请求错误
  NETWORK_ERROR: 'network_error', // 网络错误
  BUSINESS_ERROR: 'business_error', // 业务逻辑错误
  RUNTIME_ERROR: 'runtime_error',  // 运行时错误
  UNKNOWN_ERROR: 'unknown_error'   // 未知错误
};

/**
 * 格式化错误信息
 * @param {Error} error - 错误对象
 * @param {string} type - 错误类型
 * @param {Object} context - 错误上下文信息
 * @returns {Object} - 格式化后的错误信息
 */
export const formatError = (error, type = ErrorTypes.UNKNOWN_ERROR, context = {}) => {
  // 基础错误信息
  const baseError = {
    type,
    message: error.message || '未知错误',
    timestamp: new Date().toISOString(),
    url: window.location.href,
    userAgent: navigator.userAgent,
  };

  // 根据错误类型添加特定信息
  switch (type) {
    case ErrorTypes.API_ERROR:
      return {
        ...baseError,
        status: error.response?.status,
        statusText: error.response?.statusText,
        endpoint: error.config?.url,
        method: error.config?.method,
        params: error.config?.params,
        data: error.config?.data,
        responseData: error.response?.data,
        ...context
      };
    case ErrorTypes.NETWORK_ERROR:
      return {
        ...baseError,
        online: navigator.onLine,
        ...context
      };
    case ErrorTypes.BUSINESS_ERROR:
      return {
        ...baseError,
        code: error.code || context.code,
        ...context
      };
    case ErrorTypes.RUNTIME_ERROR:
      return {
        ...baseError,
        stack: error.stack,
        componentStack: error.componentStack, // React错误边界提供
        ...context
      };
    default:
      return {
        ...baseError,
        stack: error.stack,
        ...context
      };
  }
};

/**
 * 记录错误
 * @param {Error} error - 错误对象
 * @param {string} type - 错误类型
 * @param {Object} context - 错误上下文信息
 */
export const logError = (error, type = ErrorTypes.UNKNOWN_ERROR, context = {}) => {
  const formattedError = formatError(error, type, context);
  
  // 添加到错误存储
  errorStore.push(formattedError);
  
  // 在控制台输出详细错误信息
  console.error('Error captured:', formattedError);
  
  return formattedError;
};

/**
 * 上报错误到服务器
 * @param {Object} errorData - 错误数据
 * @param {string} endpoint - 上报端点
 * @returns {Promise} - 上报结果
 */
export const reportError = async (errorData, endpoint = '/api/system/errors/') => {
  try {
    const response = await axios.post(endpoint, errorData);
    return response.data;
  } catch (error) {
    console.error('Error reporting failed:', error);
    return null;
  }
};

/**
 * 批量上报错误
 * @param {Array} errors - 错误数组
 * @param {string} endpoint - 上报端点
 * @returns {Promise} - 上报结果
 */
export const batchReportErrors = async (errors = errorStore, endpoint = '/api/system/errors/batch/') => {
  if (errors.length === 0) return { success: true, count: 0 };
  
  try {
    const response = await axios.post(endpoint, { errors });
    // 上报成功后清空错误存储
    if (errors === errorStore) {
      errorStore.length = 0;
    }
    return response.data;
  } catch (error) {
    console.error('Batch error reporting failed:', error);
    return null;
  }
};

/**
 * 创建全局错误处理器
 * 用于捕获未处理的Promise错误和全局JavaScript错误
 */
export const setupGlobalErrorHandlers = () => {
  // 捕获未处理的Promise错误
  window.addEventListener('unhandledrejection', (event) => {
    const error = event.reason;
    logError(error, ErrorTypes.RUNTIME_ERROR, { unhandledRejection: true });
  });
  
  // 捕获全局JavaScript错误
  window.addEventListener('error', (event) => {
    const { message, filename, lineno, colno, error } = event;
    logError(
      error || new Error(message),
      ErrorTypes.RUNTIME_ERROR,
      { filename, lineno, colno, globalError: true }
    );
  });
  
  // 定期上报错误
  setInterval(() => {
    if (errorStore.length > 0) {
      batchReportErrors();
    }
  }, 60000); // 每分钟上报一次
};

/**
 * 创建API错误处理器
 * @param {Object} error - Axios错误对象
 * @param {Object} context - 额外上下文信息
 * @returns {Object} - 格式化后的错误信息
 */
export const handleApiError = (error, context = {}) => {
  // 判断错误类型
  let errorType = ErrorTypes.API_ERROR;
  
  if (error.message && error.message.includes('Network Error')) {
    errorType = ErrorTypes.NETWORK_ERROR;
  } else if (error.response && error.response.data && error.response.data.code !== 200) {
    errorType = ErrorTypes.BUSINESS_ERROR;
  }
  
  // 记录错误
  return logError(error, errorType, context);
};

export default {
  ErrorTypes,
  formatError,
  logError,
  reportError,
  batchReportErrors,
  setupGlobalErrorHandlers,
  handleApiError
};