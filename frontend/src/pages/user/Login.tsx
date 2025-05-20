import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Typography, Alert } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, SafetyOutlined } from '@ant-design/icons';
import { userApi } from '../../api/user';

interface LoginFormValues {
  username: string;
  password: string;
}

const { Title, Paragraph } = Typography;

/**
 * 用户登录页面
 * 用户可以在此页面登录系统，未激活用户将无法登录
 */
const Login = () => {
  const [loading, setLoading] = useState(false);
  const [loginError, setLoginError] = useState('');

  // 提交登录表单
  const handleSubmit = async (values) => {
    setLoading(true);
    setLoginError('');
    try {
      const response = await userApi.login(values);
      if (response && response.data) {
        // 保存 token 到本地存储
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        
        // 获取用户信息
        const userInfo = await userApi.getUserInfo();
        if (userInfo && userInfo.data) {
          localStorage.setItem('user_info', JSON.stringify(userInfo.data));
        }
        
        message.success('登录成功');
        // 跳转到首页
        window.location.href = '/';
      }
    } catch (error) {
      console.error('登录失败:', error);
      if (error.response) {
        const status = error.response.status;
        const data = error.response.data;
        
        // 处理未激活用户的情况
        if (status === 401 && data && data.detail === "用户未激活") {
          setLoginError('您的账号尚未激活，请等待管理员审核后再登录。');
        } else if (data && data.detail) {
          setLoginError(data.detail);
        } else {
          setLoginError('用户名或密码错误');
        }
      } else {
        setLoginError('登录失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card style={{ maxWidth: 400, margin: '0 auto', marginTop: 50 }}>
      <Title level={2} style={{ textAlign: 'center' }}>用户登录</Title>
      
      {loginError && (
        <Alert
          message="登录失败"
          description={loginError}
          type="error"
          showIcon
          style={{ marginBottom: 20 }}
        />
      )}
      
      <Form
        name="login"
        onFinish={handleSubmit}
        layout="vertical"
      >
        <Form.Item
          name="username"
          rules={[{ required: true, message: '请输入用户名' }]}
        >
          <Input prefix={<UserOutlined />} placeholder="用户名" />
        </Form.Item>
        
        <Form.Item
          name="password"
          rules={[{ required: true, message: '请输入密码' }]}
        >
          <Input.Password prefix={<LockOutlined />} placeholder="密码" />
        </Form.Item>
        
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            登录
          </Button>
        </Form.Item>
        
        <div style={{ textAlign: 'center' }}>
          <a href="/register">没有账号？立即注册</a>
        </div>
      </Form>
      
      <Paragraph type="secondary" style={{ textAlign: 'center', marginTop: 20 }}>
        注册成功后，需要管理员审核才能登录系统
      </Paragraph>
    </Card>
  );
};

export default Login;
