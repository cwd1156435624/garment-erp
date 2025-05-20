import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { taskReminderApi } from '../taskReminder';

// 创建axios模拟适配器
const mock = new MockAdapter(axios);

// 在每个测试后重置模拟
afterEach(() => {
  mock.reset();
});

describe('Task Reminder API', () => {
  // 测试获取任务提醒列表
  describe('getList', () => {
    it('成功获取任务提醒列表', async () => {
      const mockResponse = {
        code: 200,
        data: [
          { id: 1, title: '设备维护提醒', content: '设备A需要进行定期维护', status: 'pending' },
          { id: 2, title: '订单跟进提醒', content: '客户B的订单需要跟进', status: 'completed' }
        ],
        total: 2
      };
      
      mock.onGet('/api/system/task-reminders/').reply(200, mockResponse);
      
      const response = await taskReminderApi.getList({ page: 1, limit: 10 });
      
      expect(response).toEqual(mockResponse);
    });
    
    it('获取任务提醒列表失败', async () => {
      mock.onGet('/api/system/task-reminders/').reply(500);
      
      await expect(taskReminderApi.getList({ page: 1, limit: 10 }))
        .rejects.toThrow();
    });
  });
  
  // 测试获取任务提醒详情
  describe('getDetail', () => {
    it('成功获取任务提醒详情', async () => {
      const taskId = 1;
      const mockResponse = {
        code: 200,
        data: {
          id: taskId,
          title: '设备维护提醒',
          content: '设备A需要进行定期维护',
          status: 'pending',
          priority: 'high',
          due_date: '2023-06-15',
          created_at: '2023-06-01T00:00:00Z',
          assigned_to: '张三',
          category: 'maintenance'
        }
      };
      
      mock.onGet(`/api/system/task-reminders/${taskId}/`).reply(200, mockResponse);
      
      const response = await taskReminderApi.getDetail(taskId);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('获取不存在的任务提醒详情', async () => {
      const taskId = 999;
      const mockResponse = {
        code: 404,
        message: '任务提醒不存在'
      };
      
      mock.onGet(`/api/system/task-reminders/${taskId}/`).reply(404, mockResponse);
      
      await expect(taskReminderApi.getDetail(taskId))
        .rejects.toThrow();
    });
  });
  
  // 测试创建任务提醒
  describe('create', () => {
    it('成功创建任务提醒', async () => {
      const newTask = {
        title: '新任务提醒',
        content: '这是一个新的任务提醒',
        priority: 'medium',
        due_date: '2023-07-15',
        assigned_to: '李四',
        category: 'order'
      };
      
      const mockResponse = {
        code: 200,
        data: {
          id: 3,
          ...newTask,
          status: 'pending',
          created_at: '2023-06-10T00:00:00Z'
        },
        message: '创建成功'
      };
      
      mock.onPost('/api/system/task-reminders/').reply(201, mockResponse);
      
      const response = await taskReminderApi.create(newTask);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('创建任务提醒失败 - 缺少必填字段', async () => {
      const invalidTask = {
        title: '新任务提醒' // 缺少其他必填字段
      };
      
      const mockResponse = {
        code: 400,
        message: '缺少必填字段',
        errors: {
          content: ['此字段是必填项'],
          due_date: ['此字段是必填项']
        }
      };
      
      mock.onPost('/api/system/task-reminders/').reply(400, mockResponse);
      
      await expect(taskReminderApi.create(invalidTask))
        .rejects.toThrow();
    });
  });
  
  // 测试更新任务提醒
  describe('update', () => {
    it('成功更新任务提醒', async () => {
      const taskId = 1;
      const updateData = {
        priority: 'urgent',
        due_date: '2023-06-10', // 提前截止日期
        content: '设备A需要紧急维护'
      };
      
      const mockResponse = {
        code: 200,
        data: {
          id: taskId,
          title: '设备维护提醒',
          content: updateData.content,
          status: 'pending',
          priority: updateData.priority,
          due_date: updateData.due_date,
          created_at: '2023-06-01T00:00:00Z',
          updated_at: '2023-06-05T00:00:00Z',
          assigned_to: '张三',
          category: 'maintenance'
        },
        message: '更新成功'
      };
      
      mock.onPut(`/api/system/task-reminders/${taskId}/`).reply(200, mockResponse);
      
      const response = await taskReminderApi.update(taskId, updateData);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('更新不存在的任务提醒', async () => {
      const taskId = 999;
      const updateData = {
        priority: 'urgent'
      };
      
      const mockResponse = {
        code: 404,
        message: '任务提醒不存在'
      };
      
      mock.onPut(`/api/system/task-reminders/${taskId}/`).reply(404, mockResponse);
      
      await expect(taskReminderApi.update(taskId, updateData))
        .rejects.toThrow();
    });
  });
  
  // 测试删除任务提醒
  describe('delete', () => {
    it('成功删除任务提醒', async () => {
      const taskId = 2;
      
      const mockResponse = {
        code: 200,
        message: '删除成功'
      };
      
      mock.onDelete(`/api/system/task-reminders/${taskId}/`).reply(200, mockResponse);
      
      const response = await taskReminderApi.delete(taskId);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('删除不存在的任务提醒', async () => {
      const taskId = 999;
      
      const mockResponse = {
        code: 404,
        message: '任务提醒不存在'
      };
      
      mock.onDelete(`/api/system/task-reminders/${taskId}/`).reply(404, mockResponse);
      
      await expect(taskReminderApi.delete(taskId))
        .rejects.toThrow();
    });
  });
  
  // 测试更新任务状态
  describe('updateStatus', () => {
    it('成功更新任务状态', async () => {
      const taskId = 1;
      const statusData = {
        status: 'completed',
        comment: '任务已完成'
      };
      
      const mockResponse = {
        code: 200,
        data: {
          id: taskId,
          title: '设备维护提醒',
          status: statusData.status,
          completed_at: '2023-06-10T00:00:00Z',
          comment: statusData.comment
        },
        message: '状态更新成功'
      };
      
      mock.onPost(`/api/system/task-reminders/${taskId}/update_status/`).reply(200, mockResponse);
      
      const response = await taskReminderApi.updateStatus(taskId, statusData);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('更新任务状态失败 - 无效的状态值', async () => {
      const taskId = 1;
      const invalidStatusData = {
        status: 'invalid_status', // 无效的状态值
        comment: '测试'
      };
      
      const mockResponse = {
        code: 400,
        message: '无效的状态值',
        errors: {
          status: ['状态值必须是以下之一: pending, in_progress, completed, cancelled']
        }
      };
      
      mock.onPost(`/api/system/task-reminders/${taskId}/update_status/`).reply(400, mockResponse);
      
      await expect(taskReminderApi.updateStatus(taskId, invalidStatusData))
        .rejects.toThrow();
    });
  });
  
  // 测试获取待办任务
  describe('getPendingTasks', () => {
    it('成功获取待办任务', async () => {
      const mockResponse = {
        code: 200,
        data: [
          {
            id: 1,
            title: '设备维护提醒',
            priority: 'high',
            due_date: '2023-06-15',
            status: 'pending'
          },
          {
            id: 3,
            title: '新任务提醒',
            priority: 'medium',
            due_date: '2023-07-15',
            status: 'pending'
          }
        ],
        total: 2
      };
      
      mock.onGet('/api/system/task-reminders/pending/').reply(200, mockResponse);
      
      const response = await taskReminderApi.getPendingTasks();
      
      expect(response).toEqual(mockResponse);
    });
  });
  
  // 测试获取逾期任务
  describe('getOverdueTasks', () => {
    it('成功获取逾期任务', async () => {
      const mockResponse = {
        code: 200,
        data: [
          {
            id: 4,
            title: '逾期任务1',
            priority: 'high',
            due_date: '2023-05-15', // 已过期
            status: 'pending'
          },
          {
            id: 5,
            title: '逾期任务2',
            priority: 'urgent',
            due_date: '2023-05-20', // 已过期
            status: 'in_progress'
          }
        ],
        total: 2
      };
      
      mock.onGet('/api/system/task-reminders/overdue/').reply(200, mockResponse);
      
      const response = await taskReminderApi.getOverdueTasks();
      
      expect(response).toEqual(mockResponse);
    });
  });
});