import React, { Component } from 'react';
import { handleComponentError, getErrorState } from './errorHandler';

/**
 * 错误边界组件
 * 用于捕获子组件树中的JavaScript错误，记录错误并展示备用UI
 * 
 * 使用方式：
 * <ErrorBoundary fallback={<ErrorFallback />}>
 *   <YourComponent />
 * </ErrorBoundary>
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // 更新状态，下次渲染时显示备用UI
    return getErrorState(error);
  }

  componentDidCatch(error, errorInfo) {
    // 记录错误信息
    handleComponentError(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // 渲染备用UI
      return this.props.fallback ? (
        this.props.fallback
      ) : (
        <div className="error-boundary-fallback">
          <h2>出错了</h2>
          <p>应用遇到了一个错误，请刷新页面或联系管理员。</p>
          <details>
            <summary>错误详情</summary>
            <p>{this.state.error?.toString()}</p>
          </details>
          <button onClick={() => window.location.reload()}>刷新页面</button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;