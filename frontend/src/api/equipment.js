import request from '../utils/request';

// 设备管理相关接口
export const equipmentApi = {
  // 获取设备列表
  getList(params) {
    return request({
      url: '/equipment/equipment/',
      method: 'get',
      params
    });
  },

  // 获取设备详情
  getDetail(id) {
    return request({
      url: `/equipment/equipment/${id}/`,
      method: 'get'
    });
  },

  // 创建设备
  create(data) {
    return request({
      url: '/equipment/equipment/',
      method: 'post',
      data
    });
  },

  // 更新设备
  update(id, data) {
    return request({
      url: `/equipment/equipment/${id}/`,
      method: 'put',
      data
    });
  },

  // 删除设备
  delete(id) {
    return request({
      url: `/equipment/equipment/${id}/`,
      method: 'delete'
    });
  },

  // 获取设备维护记录
  getMaintenanceRecords(params) {
    return request({
      url: '/equipment/maintenance-records/',
      method: 'get',
      params
    });
  },

  // 创建维护记录
  createMaintenanceRecord(data) {
    return request({
      url: '/equipment/maintenance-records/',
      method: 'post',
      data
    });
  },

  // 获取故障记录
  getFaultRecords(params) {
    return request({
      url: '/equipment/fault-records/',
      method: 'get',
      params
    });
  },

  // 创建故障记录
  createFaultRecord(data) {
    return request({
      url: '/equipment/fault-records/',
      method: 'post',
      data
    });
  },

  // 更新故障记录状态
  updateFaultStatus(id, data) {
    return request({
      url: `/equipment/fault-records/${id}/update_status/`,
      method: 'post',
      data
    });
  },

  // 分配故障处理人员
  assignFault(id, data) {
    return request({
      url: `/equipment/fault-records/${id}/assign/`,
      method: 'post',
      data
    });
  },

  // 获取故障统计信息
  getFaultStatistics() {
    return request({
      url: '/equipment/fault-records/statistics/',
      method: 'get'
    });
  }
};