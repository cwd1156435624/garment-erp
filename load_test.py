#!/usr/bin/env python
"""
API 压力测试脚本
用于测试系统公告和开发者控制台 API 的性能和稳定性
"""

import requests
import time
import threading
import statistics
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from requests.auth import HTTPBasicAuth

# 配置参数
DEFAULT_BASE_URL = 'http://localhost:8000'
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'
DEFAULT_CONCURRENCY = 10
DEFAULT_REQUESTS = 100
DEFAULT_TIMEOUT = 30

# 测试端点
ENDPOINTS = {
    'system_notices': '/api/system/notices/',
    'system_notices_active': '/api/system/notices/active/',
    'system_notices_unread': '/api/system/notices/unread/',
    'developer_system_monitor': '/api/developer/system-monitor/',
    'developer_api_metrics': '/api/developer/api-metrics/',
    'developer_system_logs': '/api/developer/system-logs/',
    'developer_config_items': '/api/developer/config-items/',
    'developer_websocket_sessions': '/api/developer/websocket-sessions/',
    'developer_websocket_messages': '/api/developer/websocket-messages/',
    'users': '/api/users/',
    'users_pending': '/api/users/pending/'
}

class LoadTester:
    """API 负载测试器"""
    
    def __init__(self, base_url, username, password, concurrency, num_requests, timeout):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.concurrency = concurrency
        self.num_requests = num_requests
        self.timeout = timeout
        self.token = None
        self.results = {}
        
    def get_token(self):
        """获取认证令牌"""
        try:
            response = requests.post(
                f"{self.base_url}/api/token/",
                data={"username": self.username, "password": self.password},
                timeout=self.timeout
            )
            if response.status_code == 200:
                self.token = response.json()['access']
                print(f"成功获取认证令牌")
                return True
            else:
                print(f"获取令牌失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"获取令牌时出错: {str(e)}")
            return False
    
    def make_request(self, endpoint_name):
        """发送单个请求并记录响应时间"""
        url = f"{self.base_url}{ENDPOINTS[endpoint_name]}"
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            elapsed = time.time() - start_time
            status_code = response.status_code
            
            return {
                "elapsed": elapsed * 1000,  # 转换为毫秒
                "status_code": status_code,
                "success": 200 <= status_code < 300
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "elapsed": elapsed * 1000,
                "status_code": 0,
                "success": False,
                "error": str(e)
            }
    
    def test_endpoint(self, endpoint_name):
        """测试单个端点的性能"""
        print(f"开始测试端点: {endpoint_name}")
        results = []
        
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            futures = [executor.submit(self.make_request, endpoint_name) for _ in range(self.num_requests)]
            for future in futures:
                result = future.result()
                results.append(result)
        
        # 计算统计数据
        response_times = [r["elapsed"] for r in results]
        success_count = sum(1 for r in results if r["success"])
        
        stats = {
            "min": min(response_times),
            "max": max(response_times),
            "avg": statistics.mean(response_times),
            "median": statistics.median(response_times),
            "p95": sorted(response_times)[int(len(response_times) * 0.95)],
            "success_rate": (success_count / len(results)) * 100,
            "requests": len(results)
        }
        
        self.results[endpoint_name] = stats
        
        print(f"端点 {endpoint_name} 测试完成:")
        print(f"  请求数: {stats['requests']}")
        print(f"  成功率: {stats['success_rate']:.2f}%")
        print(f"  最小响应时间: {stats['min']:.2f}ms")
        print(f"  最大响应时间: {stats['max']:.2f}ms")
        print(f"  平均响应时间: {stats['avg']:.2f}ms")
        print(f"  中位响应时间: {stats['median']:.2f}ms")
        print(f"  95%响应时间: {stats['p95']:.2f}ms")
        print("")
    
    def run_tests(self, endpoints=None):
        """运行所有端点的测试"""
        if not self.get_token():
            print("无法获取认证令牌，测试终止")
            return False
        
        if endpoints is None:
            endpoints = list(ENDPOINTS.keys())
        
        start_time = time.time()
        
        for endpoint in endpoints:
            if endpoint in ENDPOINTS:
                self.test_endpoint(endpoint)
            else:
                print(f"未知端点: {endpoint}")
        
        total_time = time.time() - start_time
        
        print(f"\n所有测试完成，总耗时: {total_time:.2f}秒")
        print(f"总请求数: {len(endpoints) * self.num_requests}")
        
        # 保存结果到文件
        with open('load_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("测试结果已保存到 load_test_results.json")
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='API 负载测试工具')
    parser.add_argument('--url', default=DEFAULT_BASE_URL, help='API 基础 URL')
    parser.add_argument('--username', default=DEFAULT_USERNAME, help='用户名')
    parser.add_argument('--password', default=DEFAULT_PASSWORD, help='密码')
    parser.add_argument('--concurrency', type=int, default=DEFAULT_CONCURRENCY, help='并发请求数')
    parser.add_argument('--requests', type=int, default=DEFAULT_REQUESTS, help='每个端点的请求总数')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help='请求超时时间（秒）')
    parser.add_argument('--endpoints', nargs='+', help='要测试的端点列表，不指定则测试所有端点')
    
    args = parser.parse_args()
    
    tester = LoadTester(
        args.url,
        args.username,
        args.password,
        args.concurrency,
        args.requests,
        args.timeout
    )
    
    tester.run_tests(args.endpoints)

if __name__ == '__main__':
    main()
