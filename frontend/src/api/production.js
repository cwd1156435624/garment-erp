import request from '../utils/request';

const getProductionOrders = (params) => {
  return request({
    url: `${import.meta.env.VITE_API_BASE_URL}/production/orders/`,
    method: 'get',
    params
  })
}

const getOrderDetail = (id) => {
  return request({
    url: `${import.meta.env.VITE_API_BASE_URL}/production/orders/${id}/`,
    method: 'get'
  })
}

const createProductionOrder = (data) => {
  return request({
    url: `${import.meta.env.VITE_API_BASE_URL}/production/orders/`,
    method: 'post',
    data
  })
}

const updateProductionOrder = (id, data) => {
  return request({
    url: `${import.meta.env.VITE_API_BASE_URL}/production/orders/${id}/`,
    method: 'put',
    data
  })
}

const deleteProductionOrder = (id) => {
  return request({
    url: `${import.meta.env.VITE_API_BASE_URL}/production/orders/${id}/`,
    method: 'delete'
  })
}