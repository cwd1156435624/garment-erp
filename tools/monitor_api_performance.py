#!/usr/bin/env python
"""
API性能监控工具
用于监控API端点的响应时间和错误率，并生成性能报告
"""

import requests
import json
import time
import argparse
import sys
import csv
import os
from datetime import datetime, timedelta
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np

class APIPerformanceMonitor:
    """API性能监控工具类"""
    
    def __init__(self, base_url, token=None, output_dir='./api_performance', interval=60, duration=3600):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.output_dir = output_dir
        self.interval = interval  # 监控间隔（秒）
        self.duration = duration  # 监控持续时间（秒）
        self.session = requests.Session()
        self.endpoints = []
        self.results = []
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 如果提供了token，设置认证头
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def add_endpoint(self, name, method, path, data=None, params=None):
        """添加要监控的API端点"""
        self.endpoints.append({
            'name': name,
            'method': method.upper(),
            'path': path,
            'data': data,
            'params': params
        })
    
    def test_endpoint(self, endpoint):
        """测试单个端点的性能"""
        url = f"{self.base_url}{endpoint['path']}"
        method = endpoint['method']
        data = endpoint['data']
        params = endpoint['params']
        
        start_time = time.time()
        error = None
        status_code = None
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, json=data, timeout=10)
            elif method == 'PUT':
                response = self.session.put(url, json=data, timeout=10)
            elif method == 'PATCH':
                response = self.session.patch(url, json=data, timeout=10)
            elif method == 'DELETE':
                response = self.session.delete(url, timeout=10)
            else:
                return {
                    'timestamp': datetime.now().isoformat(),
                    'endpoint': endpoint['name'],
                    'method': method,
                    'path': endpoint['path'],
                    'status_code': None,
                    'response_time': None,
                    'error': f"不支持的HTTP方法: {method}"
                }
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 毫秒
            status_code = response.status_code
            
        except requests.exceptions.Timeout:
            error = "请求超时"
        except requests.exceptions.ConnectionError:
            error = "连接错误"
        except Exception as e:
            error = f"{type(e).__name__}: {str(e)}"
        
        return {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint['name'],
            'method': method,
            'path': endpoint['path'],
            'status_code': status_code,
            'response_time': response_time if status_code else None,
            'error': error
        }
    
    def run_monitoring(self):
        """运行API性能监控"""
        print(f"开始API性能监控 - 目标: {self.base_url}")
        print(f"监控间隔: {self.interval}秒, 持续时间: {self.duration}秒")
        print(f"监控端点数量: {len(self.endpoints)}")
        print(f"输出目录: {self.output_dir}")
        
        # 设置默认端点（如果没有添加任何端点）
        if not self.endpoints:
            self.setup_default_endpoints()
        
        # 创建CSV文件
        csv_file = os.path.join(self.output_dir, f"api_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Endpoint', 'Method', 'Path', 'Status Code', 'Response Time (ms)', 'Error'])
        
        start_time = time.time()
        iteration = 1
        
        try:
            while time.time() - start_time < self.duration:
                print(f"\n运行监控迭代 #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                for endpoint in self.endpoints:
                    result = self.test_endpoint(endpoint)
                    self.results.append(result)
                    
                    # 打印结果
                    status = result['status_code'] if result['status_code'] else 'ERROR'
                    response_time = f"{result['response_time']:.2f}ms" if result['response_time'] else 'N/A'
                    error = f" - {result['error']}" if result['error'] else ""
                    
                    print(f"{result['endpoint']} ({result['method']} {result['path']}): {status} - {response_time}{error}")
                    
                    # 写入CSV
                    with open(csv_file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            result['timestamp'],
                            result['endpoint'],
                            result['method'],
                            result['path'],
                            result['status_code'],
                            result['response_time'],
                            result['error']
                        ])
                
                # 等待下一次迭代
                iteration += 1
                next_run = start_time + (iteration * self.interval)
                sleep_time = max(0, next_run - time.time())
                
                if sleep_time > 0:
                    print(f"等待 {sleep_time:.1f} 秒进行下一次监控...")
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n监控被用户中断")
        
        # 生成报告
        self.generate_report()
        
        return csv_file
    
    def setup_default_endpoints(self):
        """设置默认监控端点"""
        self.add_endpoint("用户信息", "GET", "/api/users/me/")
        self.add_endpoint("通知列表", "GET", "/api/notifications/")
        self.add_endpoint("未读通知数量", "GET", "/api/notifications/unread-count/")
        self.add_endpoint("订单统计", "GET", "/api/orders/stats/")
        self.add_endpoint("物料统计", "GET", "/api/materials/stats/")
        self.add_endpoint("最近订单", "GET", "/api/orders/")
        self.add_endpoint("系统公告", "GET", "/api/notices/")
        self.add_endpoint("系统告警", "GET", "/api/alerts/")
        self.add_endpoint("设计文件列表", "GET", "/api/design-files/")
        self.add_endpoint("物料列表", "GET", "/api/materials/")
        self.add_endpoint("系统健康状态", "GET", "/api/developer/health/")
    
    def generate_report(self):
        """生成性能报告"""
        if not self.results:
            print("没有收集到监控数据，无法生成报告")
            return
        
        report_file = os.path.join(self.output_dir, f"api_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        # 按端点分组结果
        endpoint_results = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_results:
                endpoint_results[endpoint] = []
            endpoint_results[endpoint].append(result)
        
        # 计算每个端点的统计数据
        stats = []
        for endpoint, results in endpoint_results.items():
            response_times = [r['response_time'] for r in results if r['response_time'] is not None]
            error_count = sum(1 for r in results if r['error'] is not None)
            success_count = sum(1 for r in results if r['status_code'] in (200, 201, 204))
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                min_time = min(response_times)
                max_time = max(response_times)
                p95_time = np.percentile(response_times, 95) if len(response_times) >= 20 else None
            else:
                avg_time = min_time = max_time = p95_time = None
            
            total = len(results)
            error_rate = (error_count / total) * 100 if total > 0 else 0
            success_rate = (success_count / total) * 100 if total > 0 else 0
            
            stats.append({
                'endpoint': endpoint,
                'method': results[0]['method'],
                'path': results[0]['path'],
                'total': total,
                'success': success_count,
                'error': error_count,
                'success_rate': success_rate,
                'error_rate': error_rate,
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'p95_time': p95_time
            })
        
        # 按平均响应时间排序
        stats.sort(key=lambda x: x['avg_time'] if x['avg_time'] is not None else float('inf'))
        
        # 生成报告
        with open(report_file, 'w') as f:
            f.write(f"API性能监控报告\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"目标API: {self.base_url}\n")
            f.write(f"监控持续时间: {self.duration}秒\n")
            f.write(f"监控间隔: {self.interval}秒\n")
            f.write(f"总请求数: {len(self.results)}\n\n")
            
            # 端点性能表格
            table_data = []
            for s in stats:
                avg_time = f"{s['avg_time']:.2f}ms" if s['avg_time'] is not None else 'N/A'
                min_time = f"{s['min_time']:.2f}ms" if s['min_time'] is not None else 'N/A'
                max_time = f"{s['max_time']:.2f}ms" if s['max_time'] is not None else 'N/A'
                p95_time = f"{s['p95_time']:.2f}ms" if s['p95_time'] is not None else 'N/A'
                
                table_data.append([
                    s['endpoint'],
                    f"{s['method']} {s['path']}",
                    s['total'],
                    f"{s['success_rate']:.1f}%",
                    f"{s['error_rate']:.1f}%",
                    avg_time,
                    min_time,
                    max_time,
                    p95_time
                ])
            
            headers = ['端点', '请求', '总数', '成功率', '错误率', '平均响应时间', '最小响应时间', '最大响应时间', '95%响应时间']
            table = tabulate(table_data, headers=headers, tablefmt='grid')
            f.write(table)
            
            # 性能问题分析
            f.write("\n\n性能问题分析\n")
            f.write("----------------\n")
            
            slow_endpoints = [s for s in stats if s['avg_time'] is not None and s['avg_time'] > 500]
            high_error_endpoints = [s for s in stats if s['error_rate'] > 5]
            
            if slow_endpoints:
                f.write("\n响应时间过长的端点:\n")
                for endpoint in slow_endpoints:
                    f.write(f"- {endpoint['endpoint']} ({endpoint['method']} {endpoint['path']}): 平均响应时间 {endpoint['avg_time']:.2f}ms\n")
            else:
                f.write("\n未发现响应时间过长的端点\n")
            
            if high_error_endpoints:
                f.write("\n错误率过高的端点:\n")
                for endpoint in high_error_endpoints:
                    f.write(f"- {endpoint['endpoint']} ({endpoint['method']} {endpoint['path']}): 错误率 {endpoint['error_rate']:.1f}%\n")
            else:
                f.write("\n未发现错误率过高的端点\n")
            
            # 建议
            f.write("\n\n优化建议\n")
            f.write("----------------\n")
            
            if slow_endpoints:
                f.write("\n针对响应时间过长的端点:\n")
                f.write("1. 检查数据库查询性能，考虑添加索引\n")
                f.write("2. 实现结果缓存，减少重复计算\n")
                f.write("3. 优化序列化逻辑，减少不必要的字段\n")
                f.write("4. 考虑分页或限制返回结果数量\n")
            
            if high_error_endpoints:
                f.write("\n针对错误率过高的端点:\n")
                f.write("1. 检查错误日志，分析错误原因\n")
                f.write("2. 增加异常处理和重试机制\n")
                f.write("3. 检查依赖服务的可用性\n")
                f.write("4. 考虑添加熔断器模式，防止级联故障\n")
        
        print(f"\n性能报告已生成: {report_file}")
        
        # 生成图表
        self.generate_charts()
        
        return report_file
    
    def generate_charts(self):
        """生成性能图表"""
        if not self.results:
            return
        
        # 创建图表目录
        charts_dir = os.path.join(self.output_dir, 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        
        # 按端点分组结果
        endpoint_results = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_results:
                endpoint_results[endpoint] = []
            endpoint_results[endpoint].append(result)
        
        # 生成响应时间趋势图
        plt.figure(figsize=(12, 8))
        
        for endpoint, results in endpoint_results.items():
            timestamps = [datetime.fromisoformat(r['timestamp']) for r in results if r['response_time'] is not None]
            response_times = [r['response_time'] for r in results if r['response_time'] is not None]
            
            if timestamps and response_times:
                plt.plot(timestamps, response_times, 'o-', label=endpoint)
        
        plt.xlabel('时间')
        plt.ylabel('响应时间 (ms)')
        plt.title('API响应时间趋势')
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart_file = os.path.join(charts_dir, f"response_time_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.savefig(chart_file)
        
        # 生成平均响应时间比较图
        avg_times = []
        endpoints = []
        
        for endpoint, results in endpoint_results.items():
            response_times = [r['response_time'] for r in results if r['response_time'] is not None]
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                avg_times.append(avg_time)
                endpoints.append(endpoint)
        
        if avg_times and endpoints:
            plt.figure(figsize=(12, 8))
            bars = plt.barh(endpoints, avg_times)
            
            # 添加数值标签
            for bar in bars:
                width = bar.get_width()
                plt.text(width + 5, bar.get_y() + bar.get_height()/2, f'{width:.1f}ms', ha='left', va='center')
            
            plt.xlabel('平均响应时间 (ms)')
            plt.title('API端点平均响应时间比较')
            plt.grid(True, axis='x')
            plt.tight_layout()
            
            chart_file = os.path.join(charts_dir, f"avg_response_time_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(chart_file)
        
        print(f"性能图表已生成到目录: {charts_dir}")

def main():
    parser = argparse.ArgumentParser(description='API性能监控工具')
    parser.add_argument('--url', default='https://yagtpotihswf.sealosbja.site', help='API基础URL')
    parser.add_argument('--token', help='JWT认证令牌')
    parser.add_argument('--interval', type=int, default=60, help='监控间隔（秒）')
    parser.add_argument('--duration', type=int, default=3600, help='监控持续时间（秒）')
    parser.add_argument('--output', default='./api_performance', help='输出目录')
    
    args = parser.parse_args()
    
    monitor = APIPerformanceMonitor(
        args.url, 
        args.token, 
        args.output, 
        args.interval, 
        args.duration
    )
    
    monitor.run_monitoring()

if __name__ == "__main__":
    main()
