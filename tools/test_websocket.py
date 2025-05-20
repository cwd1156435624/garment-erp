#!/usr/bin/env python
"""
WebSocket连接测试脚本
用于测试WebSocket服务的连接和消息接收功能
"""

import asyncio
import json
import sys
import websockets
import argparse
from datetime import datetime

async def test_websocket(url, token, timeout=30):
    """测试WebSocket连接和消息接收"""
    full_url = f"{url}?token={token}"
    print(f"正在连接到 {url}...")
    
    try:
        async with websockets.connect(full_url, ping_interval=5, ping_timeout=10) as websocket:
            print(f"连接成功! 等待消息 {timeout} 秒...")
            
            # 发送订阅消息
            subscribe_msg = {
                "type": "subscribe",
                "channels": ["notifications", "alerts", "orders"]
            }
            await websocket.send(json.dumps(subscribe_msg))
            print(f"已发送订阅请求: {json.dumps(subscribe_msg)}")
            
            # 设置超时
            start_time = datetime.now()
            
            # 等待并处理消息
            while (datetime.now() - start_time).total_seconds() < timeout:
                try:
                    # 设置接收超时
                    message = await asyncio.wait_for(websocket.recv(), timeout=5)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    try:
                        parsed = json.loads(message)
                        print(f"[{timestamp}] 收到消息: {json.dumps(parsed, indent=2, ensure_ascii=False)}")
                        
                        # 如果收到ping，回复pong
                        if parsed.get("type") == "ping":
                            pong_msg = {"type": "pong", "timestamp": datetime.now().isoformat()}
                            await websocket.send(json.dumps(pong_msg))
                            print(f"回复pong: {json.dumps(pong_msg)}")
                    except json.JSONDecodeError:
                        print(f"[{timestamp}] 收到非JSON消息: {message}")
                except asyncio.TimeoutError:
                    # 发送ping保持连接
                    ping_msg = {"type": "ping"}
                    await websocket.send(json.dumps(ping_msg))
                    print(f"发送ping保持连接...")
            
            print(f"测试完成，总共运行了 {timeout} 秒")
    
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"连接错误 - 状态码: {e.status_code}")
        if e.status_code == 401:
            print("认证失败，请检查token是否有效")
        return False
    except Exception as e:
        print(f"连接错误: {type(e).__name__} - {str(e)}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='测试WebSocket连接')
    parser.add_argument('--url', default='wss://yagtpotihswf.sealosbja.site/ws/notifications/', help='WebSocket服务URL')
    parser.add_argument('--token', required=True, help='JWT认证令牌')
    parser.add_argument('--timeout', type=int, default=30, help='测试运行时间(秒)')
    
    args = parser.parse_args()
    
    if asyncio.run(test_websocket(args.url, args.token, args.timeout)):
        print("WebSocket测试成功!")
        sys.exit(0)
    else:
        print("WebSocket测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
