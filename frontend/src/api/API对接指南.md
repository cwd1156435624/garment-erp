# 前后端API对接指南

## 概述

本项目采用了基于Axios的封装请求工具，实现了前后端API的统一调用方式。前端API模块位于`src/api`目录下，按照业务模块进行了拆分，包括设备管理、客户管理、生产管理等模块。

## API调用流程

1. **导入API模块**：根据业务需求，导入对应的API模块
2. **调用API方法**：使用模块中提供的方法发起请求
3. **处理响应结果**：通过Promise的then/catch处理返回结果

## 请求封装说明

所有API请求都经过统一处理：

1. **请求拦截**：自动从localStorage获取token并添加到请求头
   ```js
   Authorization: Bearer {token}
   ```

2. **响应拦截**：统一处理返回格式
   ```js
   {
     code: 200, // 状态码
     message: "success", // 提示信息
     data: {} // 返回数据
   }
   ```

3. **错误处理**：
   - HTTP错误会被响应拦截器捕获并打印错误日志
   - 业务错误(code !== 200)会被拒绝并返回错误信息

## 使用示例

### 设备管理模块

```javascript
// 1. 导入设备API模块
import { equipmentApi } from '@/api/equipment';

// 2. 获取设备列表
function getEquipmentList() {
  // 设置查询参数
  const params = {
    equipment_type: 'machine',
    status: 'normal',
    page: 1,
    page_size: 10
  };
  
  // 调用API方法
  equipmentApi.getList(params)
    .then(res => {
      // 处理成功响应
      console.log('设备列表:', res.data.results);
      // 这里可以更新组件状态或进行其他操作
    })
    .catch(error => {
      // 处理错误
      console.error('获取设备列表失败:', error);
    });
}

// 3. 创建新设备
function createEquipment() {
  // 设置创建数据
  const equipmentData = {
    name: '新设备',
    equipment_type: 'machine',
    location: '车间A',
    status: 'normal'
  };
  
  // 调用API方法
  equipmentApi.create(equipmentData)
    .then(res => {
      // 处理成功响应
      console.log('设备创建成功:', res.data);
      // 可以进行页面跳转或提示用户
    })
    .catch(error => {
      // 处理错误
      console.error('设备创建失败:', error);
    });
}

// 4. 更新设备信息
function updateEquipment(id) {
  // 设置更新数据
  const updateData = {
    name: '更新后的设备名称',
    status: 'maintenance'
  };
  
  // 调用API方法
  equipmentApi.update(id, updateData)
    .then(res => {
      // 处理成功响应
      console.log('设备更新成功:', res.data);
    })
    .catch(error => {
      // 处理错误
      console.error('设备更新失败:', error);
    });
}

// 5. 删除设备
function deleteEquipment(id) {
  // 调用API方法
  equipmentApi.delete(id)
    .then(res => {
      // 处理成功响应
      console.log('设备删除成功');
    })
    .catch(error => {
      // 处理错误
      console.error('设备删除失败:', error);
    });
}
```

### 在Vue组件中使用

```javascript
<template>
  <div>
    <h1>设备列表</h1>
    <button @click="loadEquipments">刷新列表</button>
    <ul v-if="equipments.length > 0">
      <li v-for="item in equipments" :key="item.id">
        {{ item.name }} - {{ item.status }}
        <button @click="editEquipment(item.id)">编辑</button>
        <button @click="removeEquipment(item.id)">删除</button>
      </li>
    </ul>
    <p v-else>暂无设备数据</p>
  </div>
</template>

<script>
import { equipmentApi } from '@/api/equipment';

export default {
  data() {
    return {
      equipments: [],
      loading: false,
      error: null
    };
  },
  created() {
    // 组件创建时加载数据
    this.loadEquipments();
  },
  methods: {
    loadEquipments() {
      this.loading = true;
      equipmentApi.getList()
        .then(res => {
          this.equipments = res.data.results;
          this.loading = false;
        })
        .catch(error => {
          this.error = error.message || '加载失败';
          this.loading = false;
        });
    },
    editEquipment(id) {
      // 跳转到编辑页面或打开编辑弹窗
      this.$router.push(`/equipment/edit/${id}`);
    },
    removeEquipment(id) {
      if (confirm('确定要删除此设备吗？')) {
        equipmentApi.delete(id)
          .then(() => {
            // 删除成功后重新加载列表
            this.loadEquipments();
          })
          .catch(error => {
            alert('删除失败: ' + (error.message || '未知错误'));
          });
      }
    }
  }
};
</script>
```

### 在React组件中使用

```javascript
import React, { useState, useEffect } from 'react';
import { equipmentApi } from '../api/equipment';

function EquipmentList() {
  const [equipments, setEquipments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 加载设备列表
  const loadEquipments = async () => {
    setLoading(true);
    try {
      const response = await equipmentApi.getList();
      setEquipments(response.data.results);
      setError(null);
    } catch (err) {
      setError(err.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除设备
  const handleDelete = async (id) => {
    if (window.confirm('确定要删除此设备吗？')) {
      try {
        await equipmentApi.delete(id);
        // 删除成功后重新加载列表
        loadEquipments();
      } catch (err) {
        alert('删除失败: ' + (err.message || '未知错误'));
      }
    }
  };

  // 组件挂载时加载数据
  useEffect(() => {
    loadEquipments();
  }, []);

  return (
    <div>
      <h1>设备列表</h1>
      <button onClick={loadEquipments} disabled={loading}>
        {loading ? '加载中...' : '刷新列表'}
      </button>
      
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      {equipments.length > 0 ? (
        <ul>
          {equipments.map(item => (
            <li key={item.id}>
              {item.name} - {item.status}
              <button onClick={() => window.location.href = `/equipment/edit/${item.id}`}>编辑</button>
              <button onClick={() => handleDelete(item.id)}>删除</button>
            </li>
          ))}
        </ul>
      ) : (
        <p>暂无设备数据</p>
      )}
    </div>
  );
}

export default EquipmentList;
```

## 新增API接口

如果需要添加新的API接口，请按照以下步骤操作：

1. 在对应的API模块文件中添加新方法，例如在`equipment.js`中添加：

```javascript
// 获取设备使用记录
getUsageRecords(equipmentId, params) {
  return request({
    url: `/equipment/equipment/${equipmentId}/usage-records/`,
    method: 'get',
    params
  });
},
```

2. 在组件中导入并使用新添加的API方法：

```javascript
import { equipmentApi } from '@/api/equipment';

// 使用新添加的API方法
equipmentApi.getUsageRecords(1, { page: 1, page_size: 10 })
  .then(res => {
    console.log('设备使用记录:', res.data);
  })
  .catch(error => {
    console.error('获取设备使用记录失败:', error);
  });
```

## 最佳实践

1. **统一管理API**：所有API调用都应该通过API模块进行，不要在组件中直接使用axios发起请求
2. **参数验证**：在调用API前，确保参数格式正确
3. **错误处理**：始终添加catch捕获错误，并给用户友好提示
4. **加载状态**：请求过程中显示加载状态，提升用户体验
5. **缓存策略**：对于不常变化的数据，可以考虑本地缓存

## 常见问题

### Q: API请求返回401错误

A: 检查用户是否已登录，token是否有效。可能需要重新登录获取新token。

### Q: API请求返回404错误

A: 检查API路径是否正确，后端是否已实现该接口。

### Q: 如何处理大量数据的分页请求？

A: 使用params参数传递分页信息：

```javascript
equipmentApi.getList({
  page: 1,
  page_size: 10,
  // 其他筛选条件
  status: 'normal'
});
```

### Q: 如何上传文件？

A: 可以使用FormData对象：

```javascript
// 添加文件上传方法到API模块
uploadEquipmentImage(id, file) {
  const formData = new FormData();
  formData.append('image', file);
  
  return request({
    url: `/equipment/equipment/${id}/upload-image/`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}
```

使用示例：

```javascript
// 文件上传示例
function handleFileUpload(event, equipmentId) {
  const file = event.target.files[0];
  if (!file) return;
  
  equipmentApi.uploadEquipmentImage(equipmentId, file)
    .then(res => {
      console.log('文件上传成功:', res.data);
    })
    .catch(error => {
      console.error('文件上传失败:', error);
    });
}
```