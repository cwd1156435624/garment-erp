import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { userApi } from '../user';

// 创建axios模拟适配器
const mock = new MockAdapter(axios);

// 在每个测试后重置模拟
afterEach(() => {
  mock.reset();
});

describe('User API', () => {
  // 测试用户登录
  describe('login', () => {
    it('登录成功', async () => {
      const loginData = {
        username: 'testuser',
        password: 'password123'
      };
      
      const mockResponse = {
        code: 200,
        data: {
          id: 1,
          username: 'testuser',
          name: '测试用户',
          email: 'test@example.com',
          token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.example'
        },
        message: '登录成功'
      };
      
      mock.onPost('/api/users/login/').reply(200, mockResponse);
      
      const response = await userApi.login(loginData);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('登录失败 - 用户名或密码错误', async () => {
      const loginData = {
        username: 'wronguser',
        password: 'wrongpass'
      };
      
      const mockResponse = {
        code: 401,
        message: '用户名或密码错误'
      };
      
      mock.onPost('/api/users/login/').reply(401, mockResponse);
      
      await expect(userApi.login(loginData))
        .rejects.toThrow();
    });
  });
  
  // 测试用户注册
  describe('register', () => {
    it('注册成功', async () => {
      const registerData = {
        username: 'newuser',
        password: 'password123',
        email: 'newuser@example.com',
        name: '新用户'
      };
      
      const mockResponse = {
        code: 200,
        data: {
          id: 2,
          username: 'newuser',
          name: '新用户',
          email: 'newuser@example.com'
        },
        message: '注册成功'
      };
      
      mock.onPost('/api/users/register/').reply(201, mockResponse);
      
      const response = await userApi.register(registerData);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('注册失败 - 用户名已存在', async () => {
      const registerData = {
        username: 'existinguser',
        password: 'password123',
        email: 'existing@example.com',
        name: '已存在用户'
      };
      
      const mockResponse = {
        code: 400,
        message: '用户名已存在',
        errors: {
          username: ['该用户名已被注册']
        }
      };
      
      mock.onPost('/api/users/register/').reply(400, mockResponse);
      
      await expect(userApi.register(registerData))
        .rejects.toThrow();
    });
    
    it('注册失败 - 邮箱已存在', async () => {
      const registerData = {
        username: 'newuser2',
        password: 'password123',
        email: 'existing@example.com',
        name: '新用户2'
      };
      
      const mockResponse = {
        code: 400,
        message: '邮箱已被使用',
        errors: {
          email: ['该邮箱已被注册']
        }
      };
      
      mock.onPost('/api/users/register/').reply(400, mockResponse);
      
      await expect(userApi.register(registerData))
        .rejects.toThrow();
    });
  });
  
  // 测试获取用户信息
  describe('getUserInfo', () => {
    it('成功获取用户信息', async () => {
      const mockResponse = {
        code: 200,
        data: {
          id: 1,
          username: 'testuser',
          name: '测试用户',
          email: 'test@example.com',
          role: 'admin',
          last_login: '2023-05-01T10:30:00Z'
        }
      };
      
      mock.onGet('/api/users/info/').reply(200, mockResponse);
      
      const response = await userApi.getUserInfo();
      
      expect(response).toEqual(mockResponse);
    });
    
    it('获取用户信息失败 - 未授权', async () => {
      const mockResponse = {
        code: 401,
        message: '未授权，请先登录'
      };
      
      mock.onGet('/api/users/info/').reply(401, mockResponse);
      
      await expect(userApi.getUserInfo())
        .rejects.toThrow();
    });
  });
  
  // 测试更新用户信息
  describe('updateUserInfo', () => {
    it('成功更新用户信息', async () => {
      const updateData = {
        name: '更新后的用户名',
        email: 'updated@example.com'
      };
      
      const mockResponse = {
        code: 200,
        data: {
          id: 1,
          username: 'testuser',
          name: updateData.name,
          email: updateData.email,
          role: 'admin',
          last_login: '2023-05-01T10:30:00Z'
        },
        message: '更新成功'
      };
      
      mock.onPut('/api/users/info/').reply(200, mockResponse);
      
      const response = await userApi.updateUserInfo(updateData);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('更新用户信息失败 - 邮箱格式错误', async () => {
      const updateData = {
        name: '更新后的用户名',
        email: 'invalid-email'
      };
      
      const mockResponse = {
        code: 400,
        message: '邮箱格式错误',
        errors: {
          email: ['请输入有效的邮箱地址']
        }
      };
      
      mock.onPut('/api/users/info/').reply(400, mockResponse);
      
      await expect(userApi.updateUserInfo(updateData))
        .rejects.toThrow();
    });
  });
  
  // 测试修改密码
  describe('changePassword', () => {
    it('成功修改密码', async () => {
      const passwordData = {
        old_password: 'oldpassword123',
        new_password: 'newpassword123',
        confirm_password: 'newpassword123'
      };
      
      const mockResponse = {
        code: 200,
        message: '密码修改成功'
      };
      
      mock.onPost('/api/users/change-password/').reply(200, mockResponse);
      
      const response = await userApi.changePassword(passwordData);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('修改密码失败 - 原密码错误', async () => {
      const passwordData = {
        old_password: 'wrongoldpassword',
        new_password: 'newpassword123',
        confirm_password: 'newpassword123'
      };
      
      const mockResponse = {
        code: 400,
        message: '原密码错误'
      };
      
      mock.onPost('/api/users/change-password/').reply(400, mockResponse);
      
      await expect(userApi.changePassword(passwordData))
        .rejects.toThrow();
    });
    
    it('修改密码失败 - 两次输入的新密码不一致', async () => {
      const passwordData = {
        old_password: 'oldpassword123',
        new_password: 'newpassword123',
        confirm_password: 'differentpassword'
      };
      
      const mockResponse = {
        code: 400,
        message: '两次输入的新密码不一致',
        errors: {
          confirm_password: ['两次输入的密码不一致']
        }
      };
      
      mock.onPost('/api/users/change-password/').reply(400, mockResponse);
      
      await expect(userApi.changePassword(passwordData))
        .rejects.toThrow();
    });
  });
  
  // 测试重置密码
  describe('resetPassword', () => {
    it('成功发送重置密码邮件', async () => {
      const resetData = {
        email: 'test@example.com'
      };
      
      const mockResponse = {
        code: 200,
        message: '重置密码邮件已发送，请查收'
      };
      
      mock.onPost('/api/users/reset-password/').reply(200, mockResponse);
      
      const response = await userApi.resetPassword(resetData);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('重置密码失败 - 邮箱不存在', async () => {
      const resetData = {
        email: 'nonexistent@example.com'
      };
      
      const mockResponse = {
        code: 404,
        message: '该邮箱未注册'
      };
      
      mock.onPost('/api/users/reset-password/').reply(404, mockResponse);
      
      await expect(userApi.resetPassword(resetData))
        .rejects.toThrow();
    });
  });
});