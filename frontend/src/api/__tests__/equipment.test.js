import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { equipmentApi } from '../equipment';

// 创建axios模拟适配器
const mock = new MockAdapter(axios);

// 在每个测试后重置模拟
afterEach(() => {
    mock.reset();
});

describe('Equipment API', () => {
    // 测试获取设备列表
    describe('getList', () => {
        it('成功获取设备列表', async () => {
            const mockResponse = {
                code: 200,
                data: [
                    { id: 1, name: '设备A', model: 'Model-A', status: 'normal' },
                    { id: 2, name: '设备B', model: 'Model-B', status: 'maintenance' }
                ],
                total: 2
            };

            mock.onGet('/api/equipment/equipment/').reply(200, mockResponse);

            const response = await equipmentApi.getList({ page: 1, limit: 10 });

            expect(response).toEqual(mockResponse);
        });

        it('获取设备列表失败', async () => {
            mock.onGet('/api/equipment/equipment/').reply(500);

            await expect(equipmentApi.getList({ page: 1, limit: 10 }))
                .rejects.toThrow();
        });
    });

    // 测试获取设备详情
    describe('getDetail', () => {
        it('成功获取设备详情', async () => {
            const equipmentId = 1;
            const mockResponse = {
                code: 200,
                data: {
                    id: equipmentId,
                    name: '设备A',
                    model: 'Model-A',
                    serial_number: 'SN12345678',
                    manufacturer: '制造商A',
                    purchase_date: '2022-01-15',
                    warranty_period: 24,
                    status: 'normal',
                    location: '车间A',
                    description: '这是一台测试设备'
                }
            };

            mock.onGet(`/api/equipment/equipment/${equipmentId}/`).reply(200, mockResponse);

            const response = await equipmentApi.getDetail(equipmentId);

            expect(response).toEqual(mockResponse);
        });

        it('获取不存在的设备详情', async () => {
            const equipmentId = 999;
            const mockResponse = {
                code: 404,
                message: '设备不存在'
            };

            mock.onGet(`/api/equipment/equipment/${equipmentId}/`).reply(404, mockResponse);

            await expect(equipmentApi.getDetail(equipmentId))
                .rejects.toThrow();
        });
    });

    // 测试创建设备
    describe('create', () => {
        it('成功创建设备', async () => {
            const newEquipment = {
                name: '新设备',
                model: 'New-Model',
                serial_number: 'SN87654321',
                manufacturer: '制造商B',
                purchase_date: '2023-03-10',
                warranty_period: 12,
                status: 'normal',
                location: '车间B',
                description: '这是一台新设备'
            };

            const mockResponse = {
                code: 200,
                data: {
                    id: 3,
                    ...newEquipment,
                    created_at: '2023-05-01T00:00:00Z'
                },
                message: '创建成功'
            };

            mock.onPost('/api/equipment/equipment/').reply(201, mockResponse);

            const response = await equipmentApi.create(newEquipment);

            expect(response).toEqual(mockResponse);
        });

        it('创建设备失败 - 缺少必填字段', async () => {
            const invalidEquipment = {
                name: '新设备' // 缺少其他必填字段
            };

            const mockResponse = {
                code: 400,
                message: '缺少必填字段',
                errors: {
                    model: ['此字段是必填项'],
                    serial_number: ['此字段是必填项']
                }
            };

            mock.onPost('/api/equipment/equipment/').reply(400, mockResponse);

            await expect(equipmentApi.create(invalidEquipment))
                .rejects.toThrow();
        });

        it('创建设备失败 - 序列号已存在', async () => {
            const duplicateEquipment = {
                name: '重复设备',
                model: 'Duplicate-Model',
                serial_number: 'SN12345678', // 已存在的序列号
                manufacturer: '制造商C',
                purchase_date: '2023-04-15',
                warranty_period: 18,
                status: 'normal',
                location: '车间C'
            };

            const mockResponse = {
                code: 400,
                message: '序列号已被使用',
                errors: {
                    serial_number: ['该序列号已被注册']
                }
            };

            mock.onPost('/api/equipment/equipment/').reply(400, mockResponse);

            await expect(equipmentApi.create(duplicateEquipment))
                .rejects.toThrow();
        });
    });

    // 测试更新设备信息
    describe('update', () => {
        it('成功更新设备信息', async () => {
            const equipmentId = 1;
            const updateData = {
                status: 'maintenance',
                location: '车间D',
                description: '设备已移至车间D进行维护'
            };

            const mockResponse = {
                code: 200,
                data: {
                    id: equipmentId,
                    name: '设备A',
                    model: 'Model-A',
                    serial_number: 'SN12345678',
                    manufacturer: '制造商A',
                    purchase_date: '2022-01-15',
                    warranty_period: 24,
                    status: updateData.status,
                    location: updateData.location,
                    description: updateData.description,
                    updated_at: '2023-05-10T00:00:00Z'
                },
                message: '更新成功'
            };

            mock.onPut(`/api/equipment/equipment/${equipmentId}/`).reply(200, mockResponse);

            const response = await equipmentApi.update(equipmentId, updateData);

            expect(response).toEqual(mockResponse);
        });

        it('更新不存在的设备', async () => {
            const equipmentId = 999;
            const updateData = {
                status: 'maintenance'
            };

            const mockResponse = {
                code: 404,
                message: '设备不存在'
            };

            mock.onPut(`/api/equipment/equipment/${equipmentId}/`).reply(404, mockResponse);

            await expect(equipmentApi.update(equipmentId, updateData))
                .rejects.toThrow();
        });
    });

    // 测试删除设备
    describe('delete', () => {
        it('成功删除设备', async () => {
            const equipmentId = 2;

            const mockResponse = {
                code: 200,
                message: '删除成功'
            };

            mock.onDelete(`/api/equipment/equipment/${equipmentId}/`).reply(200, mockResponse);

            const response = await equipmentApi.delete(equipmentId);

            expect(response).toEqual(mockResponse);
        });

        it('删除不存在的设备', async () => {
            const equipmentId = 999;

            const mockResponse = {
                code: 404,
                message: '设备不存在'
            };

            mock.onDelete(`/api/equipment/equipment/${equipmentId}/`).reply(404, mockResponse);

            await expect(equipmentApi.delete(equipmentId))
                .rejects.toThrow();
        });
    });

    // 测试获取设备维护记录
    describe('getMaintenanceRecords', () => {
        it('成功获取维护记录', async () => {
            const mockResponse = {
                code: 200,
                data: [
                    {
                        id: 101,
                        equipment_id: 1,
                        equipment_name: '设备A',
                        maintenance_type: 'regular',
                        maintenance_date: '2023-02-15',
                        maintenance_staff: '张三',
                        description: '定期维护',
                        cost: 500
                    },
                    {
                        id: 102,
                        equipment_id: 1,
                        equipment_name: '设备A',
                        maintenance_type: 'repair',
                        maintenance_date: '2023-04-20',
                        maintenance_staff: '李四',
                        description: '更换零件',
                        cost: 1200
                    }
                ],
                total: 2
            };

            mock.onGet('/api/equipment/maintenance-records/').reply(200, mockResponse);

            const response = await equipmentApi.getMaintenanceRecords({ equipment_id: 1 });

            expect(response).toEqual(mockResponse);
        });
    });

    // 测试创建维护记录
    describe('createMaintenanceRecord', () => {
        it('成功创建维护记录', async () => {
            const newRecord = {
                equipment_id: 1,
                maintenance_type: 'regular',
                maintenance_date: '2023-05-15',
                maintenance_staff: '王五',
                description: '季度维护',
                cost: 800
            };

            const mockResponse = {
                code: 200,
                data: {
                    id: 103,
                    equipment_name: '设备A',
                    ...newRecord,
                    created_at: '2023-05-15T00:00:00Z'
                },
                message: '创建成功'
            };

            mock.onPost('/api/equipment/maintenance-records/').reply(201, mockResponse);

            const response = await equipmentApi.createMaintenanceRecord(newRecord);

            expect(response).toEqual(mockResponse);
        });

        it('创建维护记录失败 - 设备不存在', async () => {
            const invalidRecord = {
                equipment_id: 999, // 不存在的设备ID
                maintenance_type: 'regular',
                maintenance_date: '2023-05-15',
                maintenance_staff: '王五',
                description: '季度维护',
                cost: 800
            };

            const mockResponse = {
                code: 404,
                message: '设备不存在'
            };

            mock.onPost('/api/equipment/maintenance-records/').reply(404, mockResponse);

            await expect(equipmentApi.createMaintenanceRecord(invalidRecord))
                .rejects.toThrow();
        });
    });

    // 测试获取故障记录
    describe('getFaultRecords', () => {
        it('成功获取故障记录', async () => {
            const mockResponse = {
                code: 200,
                data: [
                    {
                        id: 201,
                        equipment_id: 1,
                        equipment_name: '设备A',
                        fault_type: 'mechanical',
                        fault_date: '2023-03-10',
                        reporter: '张三',
                        description: '设备异常噪音',
                        status: 'resolved',
                        resolution: '更换轴承',
                        resolved_date: '2023-03-12'
                    },
                    {
                        id: 202,
                        equipment_id: 2,
                        equipment_name: '设备B',
                        fault_type: 'electrical',
                        fault_date: '2023-04-05',
                        reporter: '李四',
                        description: '电路短路',
                        status: 'pending',
                        resolution: null,
                        resolved_date: null
                    }
                ],
                total: 2
            };

            mock.onGet('/api/equipment/fault-records/').reply(200, mockResponse);

            const response = await equipmentApi.getFaultRecords({ status: 'all' });

            expect(response).toEqual(mockResponse);
        });
    });

    // 测试创建故障记录
    describe('createFaultRecord', () => {
        it('成功创建故障记录', async () => {
            const newFault = {
                equipment_id: 1,
                fault_type: 'software',
                fault_date: '2023-05-20',
                reporter: '王五',
                description: '控制系统崩溃',
                status: 'pending'
            };

            const mockResponse = {
                code: 200,
                data: {
                    id: 203,
                    equipment_name: '设备A',
                    ...newFault,
                    resolution: null,
                    resolved_date: null,
                    created_at: '2023-05-20T00:00:00Z'
                },
                message: '创建成功'
            };

            mock.onPost('/api/equipment/fault-records/').reply(201, mockResponse);

            const response = await equipmentApi.createFaultRecord(newFault);

            expect(response).toEqual(mockResponse);
        });
    });

    // 测试更新故障记录状态
    describe('updateFaultStatus', () => {
        it('成功更新故障状态', async () => {
            const faultId = 202;
            const statusData = {};
