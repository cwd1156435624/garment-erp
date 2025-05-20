import service from '../apiClient';

/**
 * @typedef {object} Notification
 * @property {string} id
 * @property {string} title       - 通知标题
 * @property {string} content     - 通知内容
 * @property {string} datetime    - 创建时间
 * @property {boolean} read       - 是否已读
 * @property {string} type        - 通知类型
 */

/**
 * 获取通知列表
 * @param {number} [page=1] - 页码
 * @param {number} [pageSize=10] - 每页数量
 * @returns {Promise<{results: Notification[], count: number}>}
 */
export const getNotifications = async (page = 1, pageSize = 10) => {
  try {
    // apiClient 已经包含了 base URL，所以这里使用不带/api前缀的路径
    const response = await service.get('/v1/notifications/', {
        params: { page, page_size: pageSize }
    });

    const notificationsData = Array.isArray(response.data?.results) ? response.data.results : [];
    const count = response.data?.count ?? 0;

    const formattedResults = notificationsData.map((item) => ({
      id: String(item.id),
      title: item.title || '系统通知',
      content: item.content,
      datetime: item.created_at,
      read: item.is_read || false,
      type: item.type || 'default'
    }));

    return { results: formattedResults, count };

  } catch (error) {
    console.error('获取通知列表失败:', error);
    return { results: [], count: 0 };
  }
};

/**
 * 标记单个通知为已读
 * @param {string} id - 通知 ID
 * @returns {Promise<boolean>} - 操作是否成功
 */
export const markNotificationAsRead = async (id) => {
  try {
    // apiClient 已经包含了 base URL，所以这里使用不带/api前缀的路径
    await service.post(`/v1/notifications/${id}/read/`);
    return true;
  } catch (error) {
    console.error(`标记通知 ${id} 为已读失败:`, error);
    return false;
  }
};

/**
 * 标记所有通知为已读
 * @returns {Promise<boolean>} - 操作是否成功
 */
export const markAllNotificationsAsRead = async () => {
  try {
    // apiClient 已经包含了 base URL，所以这里使用不带/api前缀的路径
    await service.post('/v1/notifications/read-all/');
    return true;
  } catch (error) {
    console.error('标记所有通知为已读失败:', error);
    return false;
  }
};

/**
 * 获取未读通知数量
 * @returns {Promise<number>} - 未读数量
 */
export const getUnreadCount = async () => {
  try {
    // apiClient 已经包含了 base URL，所以这里使用不带/api前缀的路径
    const response = await service.get('/v1/notifications/unread-count/');
    return response.data?.count ?? 0;
  } catch (error) {
    console.error('获取未读通知数量失败:', error);
    return 0;
  }
};

const notificationService = {
    getNotifications,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    getUnreadCount
};

export default notificationService;
