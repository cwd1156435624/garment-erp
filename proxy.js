const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');

const app = express();

// 启用CORS
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001'],
  credentials: true
}));

// 创建API代理
const apiProxy = createProxyMiddleware({
  target: 'https://yagtpotihswf.sealosbja.site',
  changeOrigin: true,
  pathRewrite: {
    '^/api': '/api' // 保持路径不变
  },
  onProxyRes: function(proxyRes, req, res) {
    // 添加CORS头部
    proxyRes.headers['Access-Control-Allow-Origin'] = req.headers.origin || '*';
    proxyRes.headers['Access-Control-Allow-Credentials'] = 'true';
    proxyRes.headers['Access-Control-Allow-Methods'] = 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS';
    proxyRes.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With';
  }
});

// 使用代理中间件
app.use('/api', apiProxy);

// 启动服务器
const PORT = 8080;
app.listen(PORT, () => {
  console.log(`代理服务器运行在 http://localhost:${PORT}`);
});
