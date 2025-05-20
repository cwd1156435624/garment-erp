import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { productionApi } from '../production';

// 创建axios模拟适配器
const mock = new MockAdapter(axios);

// 在每个测试后重置模拟
afterEach(() => {
  mock.reset();
});

describe('Production API', () => {
  // 测试获取生产订单列表
  describe('getOrderList', () => {
    it('成功获取生产订单列表', async () => {
      const mockResponse = {
        code: 200,
        data: [
          { id: 1, order_number: 'PRD-2023-001', product_name: '产品A', status: 'processing' },
          { id: 2, order_number: 'PRD-2023-002', product_name: '产品B', status: 'completed' }
        ],
        total: 2
      };
      
      mock.onGet('/api/production/orders/').reply(200, mockResponse);
      
      const response = await productionApi.getOrderList({ page: 1, limit: 10 });
      
      expect(response).toEqual(mockResponse);
    });
    
    it('获取生产订单列表失败', async () => {
      mock.onGet('/api/production/orders/').reply(500);
      
      await expect(productionApi.getOrderList({ page: 1, limit: 10 }))
        .rejects.toThrow();
    });
  });
  
  // 测试获取生产订单详情
  describe('getOrderDetail', () => {
    it('成功获取生产订单详情', async () => {
      const orderId = 1;
      const mockResponse = {
        code: 200,
        data: {
          id: orderId,
          order_number: 'PRD-2023-001',
          product_name: '产品A',
          quantity: 100,
          start_date: '2023-01-15',
          end_date: '2023-02-15',
          status: 'processing',
          priority: 'high',
          description: '这是一个测试生产订单'
        }
      };
      
      mock.onGet(`/api/production/orders/${orderId}/`).reply(200, mockResponse);
      
      const response = await productionApi.getOrderDetail(orderId);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('获取不存在的生产订单详情', async () => {
      const orderId = 999;
      const mockResponse = {
        code: 404,
        message: '生产订单不存在'
      };
      
      mock.onGet(`/api/production/orders/${orderId}/`).reply(404, mockResponse);
      
      await expect(productionApi.getOrderDetail(orderId))
        .rejects.toThrow();
    });
  });
  
  // 测试创建生产订单
  describe('createOrder', () => {
    it('成功创建生产订单', async () => {
      const newOrder = {
        product_name: '新产品',
        quantity: 50,
        start_date: '2023-05-01',
        end_date: '2023-06-01',
        priority: 'medium',
        description: '这是一个新的生产订单'
      };
      
      const mockResponse = {
        code: 200,
        data: {
          id: 3,
          order_number: 'PRD-2023-003',
          ...newOrder,
          status: 'pending',
          created_at: '2023-04-25T00:00:00Z'
        },
        message: '创建成功'
      };
      
      mock.onPost('/api/production/orders/').reply(201, mockResponse);
      
      const response = await productionApi.createOrder(newOrder);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('创建生产订单失败 - 缺少必填字段', async () => {
      const invalidOrder = {
        product_name: '新产品' // 缺少其他必填字段
      };
      
      const mockResponse = {
        code: 400,
        message: '缺少必填字段',
        errors: {
          quantity: ['此字段是必填项'],
          start_date: ['此字段是必填项'],
          end_date: ['此字段是必填项']
        }
      };
      
      mock.onPost('/api/production/orders/').reply(400, mockResponse);
      
      await expect(productionApi.createOrder(invalidOrder))
        .rejects.toThrow();
    });
  });
  
  // 测试更新生产订单
  describe('updateOrder', () => {
    it('成功更新生产订单', async () => {
      const orderId = 1;
      const updateData = {
        end_date: '2023-03-01', // 延长结束日期
        priority: 'urgent',
        description: '紧急订单，需要提前完成'
      };
      
      const mockResponse = {
        code: 200,
        data: {
          id: orderId,
          order_number: 'PRD-2023-001',
          product_name: '产品A',
          quantity: 100,
          start_date: '2023-01-15',
          end_date: updateData.end_date,
          status: 'processing',
          priority: updateData.priority,
          description: updateData.description,
          updated_at: '2023-02-10T00:00:00Z'
        },
        message: '更新成功'
      };
      
      mock.onPut(`/api/production/orders/${orderId}/`).reply(200, mockResponse);
      
      const response = await productionApi.updateOrder(orderId, updateData);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('更新不存在的生产订单', async () => {
      const orderId = 999;
      const updateData = {
        priority: 'urgent'
      };
      
      const mockResponse = {
        code: 404,
        message: '生产订单不存在'
      };
      
      mock.onPut(`/api/production/orders/${orderId}/`).reply(404, mockResponse);
      
      await expect(productionApi.updateOrder(orderId, updateData))
        .rejects.toThrow();
    });
  });
  
  // 测试删除生产订单
  describe('deleteOrder', () => {
    it('成功删除生产订单', async () => {
      const orderId = 2;
      
      const mockResponse = {
        code: 200,
        message: '删除成功'
      };
      
      mock.onDelete(`/api/production/orders/${orderId}/`).reply(200, mockResponse);
      
      const response = await productionApi.deleteOrder(orderId);
      
      expect(response).toEqual(mockResponse);
    });
    
    it('删除不存在的生产订单', async () => {
      const orderId = 999;
      
      const mockResponse = {
        code: 404,
        message: '生产订单不存在'
      };
      
      mock.onDelete(`/api/production/orders/${orderId}/`).reply(404, mockResponse);
      
      await expect(productionApi.deleteOrder(orderId))
        .rejects.toThrow();
    });
  });
  
  // 测试获取生产计划列表
  describe('getPlanList', () => {
    it('成功获取生产计划列表', async () => {
      const mockResponse = {
        code: 200,
        data: [
          { id: 1, plan_number: 'PLAN-2023-001', order_id: 1, status: 'in_progress' },
          { id: 2, plan_number: 'PLAN-2023-002', order_id: 2, status: 'completed' }
        ],
        total: 2
      };
      
      mock.onGet('/api/production/plans/').reply(200, mockResponse);
      
      const response = await productionApi.getPlanList({ page: 1, limit: 10 });
      
      expect(response).toEqual(mockResponse);
    });
  });
  
  // 测试获取生产计划详情
  describe('getPlanDetail', () => {
    it('成功获取生产计划详情', async () => {
      const planId = 1;
      const mockResponse = {
        code: 200,
        data: {
          id: planId,
          plan_number: 'PLAN-2023-001',
          order_id: 1,
          order_number: 'PRD-2023-001',
          product_name: '产品A',
          start_date: '2023-01-20',
          end_date: '2023-02-10',
          status: 'in_progress',
          steps: [
            { id: 101, name: '原料准备', status: 'completed' },
            { id: 102, name: '生产加工', status: 'in_progress' },
            { id: 103, name: '质量检测', status: 'pending' }
          ]
        }
      };
      
      mock.onGet(`/api/production/plans/${planId}/`).reply(200, mockResponse);
      
      const response = await productionApi.getPlanDetail(planId);
      
      expect(response).toEqual(mockResponse);
    });
  });
  
  // 测试创建生产计划
  describe('createPlan', () => {
    it('成功创建生产计划', async () => {
      const newPlan = {
        order_id: 1,
        start_date: '2023-01-20',
        end_date: '2023-02-10',
        steps: [
          { name: '原料准备', estimated_hours: 24 },
          { name: '生产加工', estimated_hours: 72 },
          { name: '质量检测', estimated_hours: 8 }
        ]
      };
      
      const mockResponse = {
        code: 200,
        data: {
          id: 3,
          plan_number: 'PLAN-2023-003',
          order_id: newPlan.order_id,
          order_number: 'PRD-2023-001',
          product_name: '产品A',
          start_date: newPlan.start_date,
          end_date: newPlan.end_date,
          status: 'pending',
          steps: [
            { id: 104, name: '原料准备', status: 'pending', estimated_hours: 24 },
            { id: 105, name: '生产加工', status: 'pending', estimated_hours: 72 },
            { id: 106, name: '质量检测', status: 'pending', estimated_hours: 8 }
          ],
          created_at: '2023-01-15T00:00:00Z'
        },
        message: '创建成功'
      };
      
      mock.onPost('/api/production/plans/').reply(201, mockResponse);
      
      const response = await productionApi.createPlan(newPlan);
      
      expect(response).toEqual(mockResponse);
    });
  });
  
  // 测试获取生产进度统计
  describe('getProductionProgress', () => {
    it('成功获取生产进度统计', async () => {
      const mockResponse = {
        code: 200,
        data: {
          total_orders: 10,
          pending_orders: 2,
          processing_orders: 5,
          completed_orders: 3,
          delayed_orders: 1,
          on_time_rate: 90,
          average_completion_days: 25
        }
      };
      
      mock.onGet('/api/production/statistics/progress/').reply(200, mockResponse);
      
      const response = await productionApi.getProductionProgress();
      
      expect(response).toEqual(mockResponse);
    });
  });
  
  // 测试获取生产效率统计
  describe('getProductionEfficiency', () => {
    it('成功获取生产效率统计', async () => {
      const mockResponse = {
        code: 200,
        data: {
          efficiency_rate: 85,
          monthly_output: [
            { month: '2023-01', output: 120 },
            { month: '2023-02', output: 150 },
            { month: '2023-03', output: 135 }
          ],
          bottleneck_processes: [
            { process: '质量检测', delay_hours: 48 },
            { process: '包装', delay_hours: 24 }
          ]
        }
      };
      
      mock.onGet('/api/production/statistics/efficiency/').reply(200, mockResponse);
      
      const response = await productionApi.getProductionEfficiency({ period: 'quarter' });
      
      expect(response).toEqual(mockResponse);
    });
  });
});