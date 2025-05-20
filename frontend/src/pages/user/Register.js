import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Typography, Alert } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { userApi } from '../../api/user';

const { Title, Paragraph } = Typography;

/**
 * 用户注册页面
 * 新用户可以在此页面注册账号，注册后需要等待管理员审核
 */
const Register = () => {
  const [loading, setLoading] = useState(false);
  const [registered, setRegistered] = useState(false);

  // 提交注册表单
  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      await userApi.register(values);
      message.success('注册成功，请等待管理员审核');
      setRegistered(true);
    } catch (error) {
      console.error('注册失败:', error);
      if (error.response && error.response.data) {
        // 显示后端返回的错误信息
        const errorData = error.response.data;
        if (typeof errorData === 'object') {
          Object.keys(errorData).forEach(key => {
            message.error(`${key}: ${errorData[key]}`);
          });
        } else {
          message.error(errorData.toString());
        }
      } else {
        message.error('注册失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card style={{ maxWidth: 400, margin: '0 auto', marginTop: 50 }}>
      <Title level={2} style={{ textAlign: 'center' }}>用户注册</Title>
      
      {registered ? (
        <Alert
          message="注册成功"
          description="您的账号已成功注册，但需要管理员审核后才能登录。请耐心等待，审核通过后会通知您。"
          type="success"
          showIcon
          style={{ marginBottom: 20 }}
        />
      ) : (
        <>
          <Paragraph type="secondary" style={{ textAlign: 'center', marginBottom: 20 }}>
            注册成功后，需要管理员审核才能登录系统
          </Paragraph>
          
          <Form
            name="register"
            onFinish={handleSubmit}
            layout="vertical"
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, message: '用户名至少3个字符' }
              ]}
            >
              <Input prefix={<UserOutlined />} placeholder="用户名" />
            </Form.Item>
            
            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '请输入有效的邮箱地址' }
              ]}
            >
              <Input prefix={<MailOutlined />} placeholder="邮箱" />
            </Form.Item>
            
            <Form.Item
              name="password"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' }
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="密码" />
            </Form.Item>
            
            <Form.Item
              name="confirm_password"
              dependencies={['password']}
              rules={[
                { required: true, message: '请确认密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'));
                  },
                }),
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="确认密码" />
            </Form.Item>
            
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block>
                注册
              </Button>
            </Form.Item>
            
            <div style={{ textAlign: 'center' }}>
              <a href="/login">已有账号？立即登录</a>
            </div>
          </Form>
        </>
      )}
    </Card>
  );
};

export default Register;
