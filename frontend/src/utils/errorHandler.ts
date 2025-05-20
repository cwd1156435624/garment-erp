import errorReporter from './errorReporter';

/**
 * 初始化全局错误处理
 * 在应用启动时调用此函数，设置全局错误捕获
 */
export const initErrorHandling = () => {
  // 设置全局错误处理器
  errorReporter.setupGlobalErrorHandlers();
  
  console.log('全局错误处理已初始化');
  
  // 返回错误报告工具，方便在其他地方使用
  return errorReporter;
};

/**
 * 创建React错误边界的错误处理函数
 * 用于React组件的componentDidCatch方法中
 */
export const handleComponentError = (error: Error, errorInfo: { componentStack: string }) => {
  const message = error.message || 'An error occurred in the component';
  errorReporter.logError(
    error,
    errorReporter.ErrorTypes.RUNTIME_ERROR,
    { message, componentStack: errorInfo.componentStack }
  );
};

/**
 * 创建React错误边界的错误处理函数
 * 用于React组件的getDerivedStateFromError方法中
 */
export const getErrorState = (error: Error) => {
  const message = error.message || 'An error occurred';
  return { hasError: true, error, message };
};

export default {
  initErrorHandling,
  handleComponentError,
  getErrorState,
  errorReporter
};