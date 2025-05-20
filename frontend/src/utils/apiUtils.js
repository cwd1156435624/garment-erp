import axios from 'axios';

/**
 * API工具函数集合，提供API请求的增强功能
 * 包括：请求重试、节流防抖、缓存策略、批量处理等
 */

// 缓存存储
const cacheStore = new Map();

/**
 * 带重试机制的请求函数
 * @param {Function} requestFn - 原始请求函数
 * @param {Object} options - 配置选项
 * @param {number} options.retries - 最大重试次数，默认3次
 * @param {number} options.retryDelay - 重试延迟时间(ms)，默认1000ms
 * @param {Function} options.shouldRetry - 判断是否应该重试的函数
 * @returns {Promise} - 返回Promise
 */
export const withRetry = (requestFn, options = {}) => {
  const { retries = 3, retryDelay = 1000, shouldRetry = (error) => true } = options;
  
  return async (...args) => {
    let lastError;
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        return await requestFn(...args);
      } catch (error) {
        lastError = error;
        
        // 判断是否应该重试
        if (attempt >= retries || !shouldRetry(error)) {
          break;
        }
        
        // 等待一段时间后重试
        await new Promise(resolve => setTimeout(resolve, retryDelay));
      }
    }
    
    throw lastError;
  };
};

/**
 * 请求防抖函数
 * @param {Function} requestFn - 原始请求函数
 * @param {number} wait - 等待时间(ms)，默认300ms
 * @returns {Function} - 返回防抖后的函数
 */
export const debounceRequest = (requestFn, wait = 300) => {
  let timeout;
  let pendingPromise = null;
  
  return function(...args) {
    // 如果已经有等待中的Promise，直接返回
    if (pendingPromise) return pendingPromise;
    
    // 创建一个新的Promise
    pendingPromise = new Promise((resolve, reject) => {
      // 清除之前的定时器
      if (timeout) clearTimeout(timeout);
      
      timeout = setTimeout(() => {
        // 执行请求
        requestFn(...args)
          .then(result => {
            pendingPromise = null;
            resolve(result);
          })
          .catch(error => {
            pendingPromise = null;
            reject(error);
          });
      }, wait);
    });
    
    return pendingPromise;
  };
};

/**
 * 请求节流函数
 * @param {Function} requestFn - 原始请求函数
 * @param {number} limit - 节流时间间隔(ms)，默认1000ms
 * @returns {Function} - 返回节流后的函数
 */
export const throttleRequest = (requestFn, limit = 1000) => {
  let inThrottle = false;
  let lastResult = null;
  
  return function(...args) {
    // 如果在节流时间内，直接返回上次的结果
    if (inThrottle) return Promise.resolve(lastResult);
    
    inThrottle = true;
    
    // 设置定时器，在limit时间后允许再次请求
    setTimeout(() => {
      inThrottle = false;
    }, limit);
    
    // 执行请求
    return requestFn(...args).then(result => {
      lastResult = result;
      return result;
    });
  };
};

/**
 * 带缓存的请求函数
 * @param {Function} requestFn - 原始请求函数
 * @param {Object} options - 缓存配置选项
 * @param {number} options.maxAge - 缓存最大有效期(ms)，默认60000ms(1分钟)
 * @param {Function} options.cacheKey - 生成缓存键的函数，默认使用URL和参数
 * @returns {Function} - 返回带缓存的请求函数
 */
export const withCache = (requestFn, options = {}) => {
  const { maxAge = 60000, cacheKey = (args) => JSON.stringify(args) } = options;
  
  return async (...args) => {
    const key = cacheKey(args);
    const cached = cacheStore.get(key);
    
    // 如果缓存存在且未过期，直接返回缓存数据
    if (cached && Date.now() - cached.timestamp < maxAge) {
      return cached.data;
    }
    
    // 执行请求
    const result = await requestFn(...args);
    
    // 更新缓存
    cacheStore.set(key, {
      data: result,
      timestamp: Date.now()
    });
    
    return result;
  };
};

/**
 * 清除指定键的缓存
 * @param {string} key - 缓存键
 */
export const clearCache = (key) => {
  if (key) {
    cacheStore.delete(key);
  } else {
    cacheStore.clear();
  }
};

/**
 * 批量处理请求
 * @param {Array<Function>} requestFns - 请求函数数组
 * @param {Object} options - 配置选项
 * @param {boolean} options.parallel - 是否并行执行，默认true
 * @param {number} options.concurrency - 并发数，默认5
 * @returns {Promise<Array>} - 返回所有请求结果的数组
 */
export const batchRequests = async (requestFns, options = {}) => {
  const { parallel = true, concurrency = 5 } = options;
  
  if (parallel) {
    // 并行执行所有请求，但限制并发数
    const results = [];
    for (let i = 0; i < requestFns.length; i += concurrency) {
      const batch = requestFns.slice(i, i + concurrency);
      const batchResults = await Promise.all(batch.map(fn => fn()));
      results.push(...batchResults);
    }
    return results;
  } else {
    // 串行执行所有请求
    const results = [];
    for (const requestFn of requestFns) {
      results.push(await requestFn());
    }
    return results;
  }
};

/**
 * 创建Mock请求函数
 * @param {Object|Function} mockData - 模拟数据或返回模拟数据的函数
 * @param {number} delay - 模拟延迟时间(ms)，默认300ms
 * @param {boolean} shouldFail - 是否模拟失败，默认false
 * @returns {Function} - 返回模拟请求函数
 */
export const createMockRequest = (mockData, delay = 300, shouldFail = false) => {
  return (...args) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (shouldFail) {
          reject(new Error('Mock request failed'));
        } else {
          const data = typeof mockData === 'function' ? mockData(...args) : mockData;
          resolve({
            code: 200,
            message: 'success',
            data
          });
        }
      }, delay);
    });
  };
};

/**
 * 创建取消令牌
 * @returns {Object} - 返回取消令牌对象
 */
export const createCancelToken = () => {
  const source = axios.CancelToken.source();
  return {
    token: source.token,
    cancel: source.cancel
  };
};

/**
 * 判断请求是否被取消
 * @param {Error} error - 错误对象
 * @returns {boolean} - 是否被取消
 */
export const isRequestCancelled = (error) => {
  return axios.isCancel(error);
};

/**
 * 超时处理函数
 * @param {Promise} promise - 原始Promise
 * @param {number} timeout - 超时时间(ms)
 * @returns {Promise} - 返回带超时处理的Promise
 */
export const withTimeout = (promise, timeout = 10000) => {
  let timeoutId;
  
  // 创建一个超时Promise
  const timeoutPromise = new Promise((_, reject) => {
    timeoutId = setTimeout(() => {
      reject(new Error(`Request timeout after ${timeout}ms`));
    }, timeout);
  });
  
  // 竞争Promise
  return Promise.race([promise, timeoutPromise])
    .finally(() => {
      clearTimeout(timeoutId);
    });
};