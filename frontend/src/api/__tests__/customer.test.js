import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { customerApi } from '../customer';

// 创建axios模拟适配器
const mock = new MockAdapter(axios);

// 在每个测试后重置模拟
afterEach(() => {
    mock.reset();
});

describe('Customer API', () => {
    // 测试获取客户列表
    describe('getList', () => {
        it('成功获取客户列表', async () => {
            // 模拟成功响应
            const mockResponse = {
                code: 200,
                data: [
                    { id: 1, name: '客户A', email: 'customerA@example.com' },
                    { id: 2, name: '客户B', email: 'customerB@example.com' }
                ],
                total: 2
            };

            mock.onGet('/api/customer/customers/').reply(200, mockResponse);

            const response = await customerApi.getList({ page: 1, limit: 10 });

            expect(response).toEqual(mockResponse);
        });

        it('获取客户列表失败', async () => {
            // 模拟服务器错误
            mock.onGet('/api/customer/customers/').reply(500);

            await expect(customerApi.getList({ page: 1, limit: 10 }))
                .rejects.toThrow();
        });
    });

    // 测试获取客户详情
    describe('getDetail', () => {
        it('成功获取客户详情', async () => {
            const customerId = 1;
            const mockResponse = {
                code: 200,
                data: {
                    id: customerId,
                    name: '客户A',
                    email: 'customerA@example.com',
                    address: '北京市海淀区',
                    phone: '13800138000',
                    credit_limit: 10000,
                    created_at: '2023-01-01T00:00:00Z'
                }
            };

            mock.onGet(`/api/customer/customers/${customerId}/`).reply(200, mockResponse);

            const response = await customerApi.getDetail(customerId);

            expect(response).toEqual(mockResponse);
        });

        it('获取不存在的客户详情', async () => {
            const customerId = 999;
            const mockResponse = {
                code: 404,
                message: '客户不存在'
            };

            mock.onGet(`/api/customer/customers/${customerId}/`).reply(404, mockResponse);

            await expect(customerApi.getDetail(customerId))
                .rejects.toThrow();
        });
    });

    // 测试创建客户
    describe('create', () => {
        it('成功创建客户', async () => {
            const newCustomer = {
                name: '新客户',
                email: 'newcustomer@example.com',
                address: '上海市浦东新区',
                phone: '13900139000'
            };

            const mockResponse = {
                code: 200,
                data: {
                    id: 3,
                    ...newCustomer,
                    credit_limit: 5000,
                    created_at: '2023-05-01T00:00:00Z'
                },
                message: '创建成功'
            };

            mock.onPost('/api/customer/customers/').reply(201, mockResponse);

            const response = await customerApi.create(newCustomer);

            expect(response).toEqual(mockResponse);
        });

        it('创建客户失败 - 缺少必填字段', async () => {
            const invalidCustomer = {
                name: '新客户' // 缺少必填的email字段
            };

            const mockResponse = {
                code: 400,
                message: '缺少必填字段',
                errors: {
                    email: ['此字段是必填项']
                }
            };

            mock.onPost('/api/customer/customers/').reply(400, mockResponse);

            await expect(customerApi.create(invalidCustomer))
                .rejects.toThrow();
        });

        it('创建客户失败 - 邮箱已存在', async () => {
            const duplicateCustomer = {
                name: '重复客户',
                email: 'customerA@example.com', // 已存在的邮箱
                address: '广州市天河区',
                phone: '13700137000'
            };

            const mockResponse = {
                code: 400,
                message: '邮箱已被使用',
                errors: {
                    email: ['该邮箱已被注册']
                }
            };

            mock.onPost('/api/customer/customers/').reply(400, mockResponse);

            await expect(customerApi.create(duplicateCustomer))
                .rejects.toThrow();
        });
    });

    // 测试更新客户信息
    describe('update', () => {
        it('成功更新客户信息', async () => {
            const customerId = 1;
            const updateData = {
                address: '北京市朝阳区',
                phone: '13800138001'
            };

            const mockResponse = {
                code: 200,
                data: {
                    id: customerId,
                    name: '客户A',
                    email: 'customerA@example.com',
                    address: updateData.address,
                    phone: updateData.phone,
                    credit_limit: 10000,
                    created_at: '2023-01-01T00:00:00Z',
                    updated_at: '2023-05-10T00:00:00Z'
                },
                message: '更新成功'
            };

            mock.onPut(`/api/customer/customers/${customerId}/`).reply(200, mockResponse);

            const response = await customerApi.update(customerId, updateData);

            expect(response).toEqual(mockResponse);
        });

        it('更新不存在的客户', async () => {
            const customerId = 999;
            const updateData = {
                address: '北京市朝阳区'
            };

            const mockResponse = {
                code: 404,
                message: '客户不存在'
            };

            mock.onPut(`/api/customer/customers/${customerId}/`).reply(404, mockResponse);

            await expect(customerApi.update(customerId, updateData))
                .rejects.toThrow();
        });
    });

    // 测试删除客户
    describe('delete', () => {
        it('成功删除客户', async () => {
            const customerId = 2;

            const mockResponse = {
                code: 200,
                message: '删除成功'
            };

            mock.onDelete(`/api/customer/customers/${customerId}/`).reply(200, mockResponse);

            const response = await customerApi.delete(customerId);

            expect(response).toEqual(mockResponse);
        });

        it('删除不存在的客户', async () => {
            const customerId = 999;

            const mockResponse = {
                code: 404,
                message: '客户不存在'
            };

            mock.onDelete(`/api/customer/customers/${customerId}/`).reply(404, mockResponse);

            await expect(customerApi.delete(customerId))
                .rejects.toThrow();
        });
    });

    // 测试获取客户订单历史
    describe('getOrderHistory', () => {
        it('成功获取客户订单历史', async () => {
            const customerId = 1;

            const mockResponse = {
                code: 200,
                data: [
                    {
                        id: 101,
                        order_number: 'ORD-2023-001',
                        total_amount: 5000,
                        status: 'completed',
                        created_at: '2023-02-15T00:00:00Z'
                    },
                    {
                        id: 102,
                        order_number: 'ORD-2023-002',
                        total_amount: 3500,
                        status: 'processing',
                        created_at: '2023-04-20T00:00:00Z'
                    }
                ],
                total: 2
            };

            mock.onGet(`/api/customer/customers/${customerId}/orders/`).reply(200, mockResponse);

            const response = await customerApi.getOrderHistory(customerId, { page: 1, limit: 10 });

            expect(response).toEqual(mockResponse);
        });

        it('获取不存在客户的订单历史', async () => {
            const customerId = 999;

            const mockResponse = {
                code: 404,
                message: '客户不存在'
            };

            mock.onGet(`/api/customer/customers/${customerId}/orders/`).reply(404, mockResponse);

            await expect(customerApi.getOrderHistory(customerId, { page: 1, limit: 10 }))
                .rejects.toThrow();
        });
    });

    // 测试获取客户统计信息
    describe('getStatistics', () => {
        it('成功获取客户统计信息', async () => {
            const customerId = 1;

            const mockResponse = {
                code: 200,
                data: {
                    total_orders: 10,
                    total_amount: 50000,
                    average_order_value: 5000,
                    first_order_date: '2023-01-15T00:00:00Z',
                    last_order_date: '2023-05-20T00:00:00Z'
                }
            };

            mock.onGet(`/api/customer/customers/${customerId}/statistics/`).reply(200, mockResponse);

            const response = await customerApi.getStatistics(customerId);

            expect(response).toEqual(mockResponse);
        });

        it('获取不存在客户的统计信息', async () => {
            const customerId = 999;

            const mockResponse = {
                code: 404,
                message: '客户不存在'
            };

            mock.onGet(`/api/customer/customers/${customerId}/statistics/`).reply(404, mockResponse);

            await expect(customerApi.getStatistics(customerId))
                .rejects.toThrow();
        });
    });

    // 测试更新客户信用额度
    describe('updateCreditLimit', () => {
        it('成功更新客户信用额度', async () => {
            const customerId = 1;
            const creditData = {
                credit_limit: 15000,
                reason: '客户信用良好，提高额度'
            };

            const mockResponse = {
                code: 200,
                data: {
                    id: customerId,
                    name: '客户A',
                    credit_limit: creditData.credit_limit,
                    credit_limit_updated_at: '2023-05-25T00:00:00Z'
                },
                message: '信用额度更新成功'
            };

            mock.onPost(`/api/customer/customers/${customerId}/update_credit_limit/`).reply(200, mockResponse);

            const response = await customerApi.updateCreditLimit(customerId, creditData);

            expect(response).toEqual(mockResponse);
        });

        it('更新信用额度失败 - 无效的额度值', async () => {
            const customerId = 1;
            const invalidCreditData = {
                credit_limit: -5000, // 负数额度
                reason: '测试'
            };

            const mockResponse = {
                code: 400,
                message: '信用额度不能为负数',
                errors: {
                    credit_limit: ['信用额度必须大于或等于0']
                }
            };

            mock.onPost(`/api/customer/customers/${customerId}/update_credit_limit/`).reply(400, mockResponse);
            
            await expect(customerApi.updateCreditLimit(customerId, invalidCreditData))
                .rejects.toThrow();
        });;

            await expect(customerApi.updateCreditLimit(customerId, invalidCreditData))
                .rejects.toThrow();
        });

        it('更新信用额度失败 - 缺少理由', async () => {
            const customerId = 1;
            const invalidCreditData = {
                credit_limit: 20000
                // 缺少必填的reason字段
            };

            const mockResponse = {
                code: 400,
                message: '缺少必填字段',
                errors: {
                    reason: ['更新信用额度必须提供理由']
                }
            };

            mock.onPost(`/api/customer/customers/${customerId}/update_credit_limit/`).reply(400, mockResponse);
            
            await expect(customerApi.updateCreditLimit(customerId, invalidCreditData))
                .rejects.toThrow();
        });
