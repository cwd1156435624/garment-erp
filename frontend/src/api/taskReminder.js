import request from '../utils/request';

// 任务提醒相关接口
export const taskReminderApi = {
  // 获取任务提醒列表
  getList(params) {
    return request({
      url: '/customer/task-reminders/',
      method: 'get',
      params
    });
  },

  // 获取任务提醒详情
  getDetail(id) {
    return request({
      url: `/customer/task-reminders/${id}/`,
      method: 'get'
    });
  },

  // 创建任务提醒
  create(data) {
    return request({
      url: '/customer/task-reminders/',
      method: 'post',
      data
    });
  },

  // 更新任务提醒
  update(id, data) {
    return request({
      url: `/customer/task-reminders/${id}/`,
      method: 'put',
      data
    });
  },

  // 删除任务提醒
  delete(id) {
    return request({
      url: `/customer/task-reminders/${id}/`,
      method: 'delete'
    });
  },

  // 完成任务
  completeTask(id) {
    return request({
      url: `/customer/task-reminders/${id}/complete_task/`,
      method: 'post'
    });
  }
};