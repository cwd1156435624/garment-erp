import service from '../apiClient';

// Function to format time difference (example, adjust as needed)
const formatTimeAgo = (date) => {
  const seconds = Math.floor((new Date() - date) / 1000);
  let interval = seconds / 31536000;
  if (interval > 1) return Math.floor(interval) + "年前";
  interval = seconds / 2592000;
  if (interval > 1) return Math.floor(interval) + "月前";
  interval = seconds / 86400;
  if (interval > 1) return Math.floor(interval) + "天前";
  interval = seconds / 3600;
  if (interval > 1) return Math.floor(interval) + "小时前";
  interval = seconds / 60;
  if (interval > 1) return Math.floor(interval) + "分钟前";
  return Math.floor(seconds) + "秒前";
};

/**
 * @typedef {object} OrderStats
 * @property {number} total        - 订单总数
 * @property {number} inProduction - 生产中订单数
 * @property {number} abnormal     - 异常订单数
 * @property {number} newAdded     - 新增订单数
 * @property {number} completed    - 已完成订单数
 */

/**
 * 获取订单统计数据
 * @returns {Promise<OrderStats>}
 */
export const fetchOrderStats = async () => {
  try {
    const response = await service.get('/orders/stats');
    // Ensure default values if API returns incomplete data
    return {
      total: response.data?.total ?? 0,
      inProduction: response.data?.inProduction ?? 0,
      abnormal: response.data?.abnormal ?? 0,
      newAdded: response.data?.newAdded ?? 0,
      completed: response.data?.completed ?? 0,
    };
  } catch (error) {
    console.error('获取订单统计数据失败:', error);
    return {
      total: 0,
      inProduction: 0,
      completed: 0,
      abnormal: 0,
      newAdded: 0
    };
  }
};

/**
 * @typedef {object} MaterialStats
 * @property {number} total    - 物料总数
 * @property {number} inStock  - 库存充足物料数
 * @property {number} lowStock - 库存不足物料数
 */

/**
 * 获取物料统计数据
 * @returns {Promise<MaterialStats>}
 */
export const fetchMaterialStats = async () => {
  try {
    const response = await service.get('/materials/stats');
    return {
        total: response.data?.total ?? 0,
        inStock: response.data?.inStock ?? 0,
        lowStock: response.data?.lowStock ?? 0,
    };
  } catch (error) {
    console.error('获取物料统计数据失败:', error);
    return {
      total: 0,
      inStock: 0,
      lowStock: 0
    };
  }
};

/**
 * @typedef {object} Order
 * @property {string} key
 * @property {string} orderNo     - 订单编号
 * @property {string} customer    - 客户名称
 * @property {string} amount      - 订单金额
 * @property {string} createTime  - 创建时间
 * @property {string} shipDate    - 发货日期
 * @property {string} status      - 订单状态
 */

/**
 * 获取最近要发货订单
 * @returns {Promise<Order[]>}
 */
export const fetchRecentOrders = async () => {
  try {
    const response = await service.get('/orders', {
      params: {
        ordering: '-created_at',
        page_size: 5
      }
    });

    const ordersData = Array.isArray(response.data?.results) ? response.data.results : [];

    return ordersData.map((item) => ({
      key: String(item.id),
      orderNo: item.order_no,
      customer: item.customer,
      amount: item.amount,
      createTime: item.created_at,
      shipDate: item.ship_date,
      status: item.status
    }));
  } catch (error) {
    console.error('获取最近订单失败:', error);
    return [];
  }
};

/**
 * @typedef {object} Notice
 * @property {string} id
 * @property {string} content    - 公告内容
 * @property {string} createdAt - 创建时间
 * @property {boolean} isRead   - 是否已读
 */

/**
 * 获取系统公告
 * @returns {Promise<Notice[]>}
 */
export const fetchNotices = async () => {
  try {
    const response = await service.get('/v1/notices');
    const noticesData = Array.isArray(response.data?.results) ? response.data.results : [];

    return noticesData.map((item) => ({
      id: String(item.id),
      content: item.content,
      createdAt: item.created_at,
      isRead: item.is_read || false
    }));
  } catch (error) {
    console.error('获取系统公告失败:', error);
    return [];
  }
};

/**
 * @typedef {object} Alert
 * @property {string} id
 * @property {string} title       - 告警标题
 * @property {string} description - 告警描述
 * @property {string} time        - 格式化后的时间
 * @property {string} status      - 优先级文本 (紧急, 高优, 中优, 低优)
 * @property {string} createdAt   - 原始创建时间
 * @property {string} priority    - 原始优先级 (critical, high, medium, low)
 */

/**
 * 获取系统告警
 * @returns {Promise<Alert[]>}
 */
export const fetchAlerts = async () => {
  try {
    const response = await service.get('/alerts', {
      params: {
        ordering: '-created_at',
        page_size: 10
      }
    });

    const alertsData = Array.isArray(response.data?.results) ? response.data.results : [];

    return alertsData.map((item) => ({
      id: String(item.id),
      title: item.title,
      description: item.description,
      time: item.created_at ? formatTimeAgo(new Date(item.created_at)) : '',
      status: item.priority === 'critical' ? '紧急' :
              item.priority === 'high' ? '高优' :
              item.priority === 'medium' ? '中优' : '低优',
      createdAt: item.created_at,
      priority: item.priority
    }));
  } catch (error) {
    console.error('获取系统告警失败:', error);
    // Return empty array on failure, as seen in previous logs
    return [];
  }
};

const homeService = {
    fetchOrderStats,
    fetchMaterialStats,
    fetchRecentOrders,
    fetchNotices,
    fetchAlerts
};

export default homeService;
