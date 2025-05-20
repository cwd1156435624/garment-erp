import React, { useState, useEffect } from 'react';
import { Table, Button, message, Card, Typography, Space, Tag } from 'antd';
import { userApi } from '../../api/user';

const { Title } = Typography;

/**
 * 待审核用户列表页面
 * 管理员可以在此页面查看所有待审核的用户，并进行审核操作
 */
const PendingUsers = () => {
  const [loading, setLoading] = useState(false);
  const [pendingUsers, setPendingUsers] = useState([]);

  // 获取待审核用户列表
  const fetchPendingUsers = async () => {
    setLoading(true);
    try {
      const response = await userApi.getPendingUsers();
      if (response && response.data) {
        setPendingUsers(response.data);
      }
    } catch (error) {
      console.error('获取待审核用户列表失败:', error);
      // 在开发环境中使用模拟数据
      if (process.env.NODE_ENV === 'development') {
        console.log('开发环境：使用待审核用户模拟数据');
        setPendingUsers([
          {
            id: 1,
            username: 'testuser1',
            email: 'test1@example.com',
            date_joined: new Date().toISOString(),
            is_active: false
          },
          {
            id: 2,
            username: 'testuser2',
            email: 'test2@example.com',
            date_joined: new Date().toISOString(),
            is_active: false
          }
        ]);
      } else {
        message.error('获取待审核用户列表失败');
      }
    } finally {
      setLoading(false);
    }
  };

  // 审核用户
  const handleApprove = async (userId) => {
    try {
      await userApi.approveUser(userId);
      message.success('用户审核通过');
      // 刷新列表
      fetchPendingUsers();
    } catch (error) {
      console.error('审核通过用户失败:', error);
      // 在开发环境中模拟审核成功
      if (process.env.NODE_ENV === 'development') {
        message.success('模拟审核: 用户审核通过');
        // 更新本地数据，模拟审核成功
        setPendingUsers(pendingUsers.map(user => {
          if (user.id === userId) {
            return { ...user, is_active: true };
          }
          return user;
        }));
      } else {
        message.error('审核操作失败: ' + (error.message || '未知错误'));
      }
    }
  };

  // 组件挂载时获取待审核用户列表
  useEffect(() => {
    fetchPendingUsers();
  }, []);

  // 表格列定义
  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '注册时间',
      dataIndex: 'date_joined',
      key: 'date_joined',
      render: (text) => new Date(text).toLocaleString(),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '已激活' : '未激活'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button 
            type="primary" 
            onClick={() => handleApprove(record.id)}
            disabled={record.is_active}
          >
            {record.is_active ? '已审核' : '审核通过'}
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Card>
      <Title level={4}>待审核用户列表</Title>
      <Table
        rowKey="id"
        columns={columns}
        dataSource={pendingUsers}
        loading={loading}
        pagination={{ pageSize: 10 }}
        locale={{ emptyText: '暂无待审核用户' }}
      />
    </Card>
  );
};

export default PendingUsers;
