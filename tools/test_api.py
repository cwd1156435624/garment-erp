#!/usr/bin/env python
"""
API自动化测试脚本
用于测试系统中的关键API端点
"""

import requests
import json
import argparse
import sys
import time
from datetime import datetime
from tabulate import tabulate

class APITester:
    """API测试工具类"""
    
    def __init__(self, base_url, token=None, verbose=False):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.verbose = verbose
        self.results = []
        self.session = requests.Session()
        
        # 如果提供了token，设置认证头
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def log(self, message):
        """打印详细日志"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def run_test(self, name, method, endpoint, expected_status=200, data=None, params=None):
        """运行单个API测试"""
        url = f"{self.base_url}{endpoint}"
        self.log(f"测试: {name}")
        self.log(f"请求: {method} {url}")
        
        if data:
            self.log(f"数据: {json.dumps(data, ensure_ascii=False)}")
        
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=10)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=10)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=10)
            else:
                self.log(f"不支持的HTTP方法: {method}")
                return False
            
            end_time = time.time()
            duration = round((end_time - start_time) * 1000)  # 毫秒
            
            status_code = response.status_code
            success = status_code == expected_status
            
            # 尝试解析响应JSON
            try:
                response_data = response.json()
                response_preview = json.dumps(response_data, ensure_ascii=False)[:100] + "..." if len(json.dumps(response_data, ensure_ascii=False)) > 100 else json.dumps(response_data, ensure_ascii=False)
            except:
                response_preview = response.text[:100] + "..." if len(response.text) > 100 else response.text
            
            self.log(f"状态码: {status_code} (预期: {expected_status})")
            self.log(f"响应: {response_preview}")
            self.log(f"耗时: {duration}ms")
            self.log(f"结果: {'成功' if success else '失败'}")
            
            # 记录测试结果
            self.results.append({
                'name': name,
                'endpoint': f"{method} {endpoint}",
                'status': status_code,
                'expected': expected_status,
                'duration': duration,
                'result': '✅ 通过' if success else '❌ 失败'
            })
            
            return success
            
        except requests.exceptions.Timeout:
            self.log("请求超时")
            self.results.append({
                'name': name,
                'endpoint': f"{method} {endpoint}",
                'status': 'N/A',
                'expected': expected_status,
                'duration': 'N/A',
                'result': '❌ 超时'
            })
            return False
        except Exception as e:
            self.log(f"请求错误: {str(e)}")
            self.results.append({
                'name': name,
                'endpoint': f"{method} {endpoint}",
                'status': 'N/A',
                'expected': expected_status,
                'duration': 'N/A',
                'result': f'❌ 错误: {type(e).__name__}'
            })
            return False
    
    def print_results(self):
        """打印测试结果表格"""
        headers = ['测试名称', '端点', '状态码', '预期状态码', '耗时(ms)', '结果']
        table_data = [[r['name'], r['endpoint'], r['status'], r['expected'], r['duration'], r['result']] for r in self.results]
        
        print("\n测试结果汇总:")
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # 计算统计信息
        total = len(self.results)
        passed = sum(1 for r in self.results if r['result'].startswith('✅'))
        failed = total - passed
        pass_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"\n总计: {total} 测试")
        print(f"通过: {passed} ({pass_rate:.1f}%)")
        print(f"失败: {failed} ({100-pass_rate:.1f}%)")
    
    def run_all_tests(self):
        """运行所有API测试"""
        print(f"开始API测试 - 目标: {self.base_url}")
        
        # 认证API测试
        if not self.token:
            self.run_test("获取认证令牌", "POST", "/api/token/", 200, {
                "username": "test_user",
                "password": "test_password"
            })
        
        # 用户API测试
        self.run_test("获取当前用户信息", "GET", "/api/users/me/")
        self.run_test("获取用户列表", "GET", "/api/users/")
        
        # 通知API测试
        self.run_test("获取通知列表", "GET", "/api/notifications/")
        self.run_test("获取未读通知数量", "GET", "/api/notifications/unread-count/")
        
        # 首页API测试
        self.run_test("获取订单统计", "GET", "/api/orders/stats/")
        self.run_test("获取物料统计", "GET", "/api/materials/stats/")
        self.run_test("获取最近订单", "GET", "/api/orders/")
        self.run_test("获取系统公告", "GET", "/api/notices/")
        self.run_test("获取系统告警", "GET", "/api/alerts/")
        
        # 设计文件API测试
        self.run_test("获取设计文件列表", "GET", "/api/design-files/")
        
        # 物料API测试
        self.run_test("获取物料列表", "GET", "/api/materials/")
        
        # 开发者API测试
        self.run_test("获取系统健康状态", "GET", "/api/developer/health/")
        
        # 打印结果
        self.print_results()
        
        # 返回测试是否全部通过
        return all(r['result'].startswith('✅') for r in self.results)

def main():
    parser = argparse.ArgumentParser(description='API自动化测试工具')
    parser.add_argument('--url', default='https://yagtpotihswf.sealosbja.site', help='API基础URL')
    parser.add_argument('--token', help='JWT认证令牌')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细日志')
    
    args = parser.parse_args()
    
    tester = APITester(args.url, args.token, args.verbose)
    success = tester.run_all_tests()
    
    if success:
        print("\nAPI测试全部通过! ✅")
        sys.exit(0)
    else:
        print("\nAPI测试部分失败! ❌")
        sys.exit(1)

if __name__ == "__main__":
    main()
