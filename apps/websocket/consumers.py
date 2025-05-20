import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth import get_user_model
from developer.models import WebSocketSession, WebSocketMessage

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    """通知WebSocket消费者"""
    
    async def connect(self):
        """处理WebSocket连接"""
        # 获取用户信息
        self.user = self.scope["user"]
        self.user_id = self.user.id if self.user.is_authenticated else None
        
        if not self.user.is_authenticated:
            # 拒绝未认证的用户
            await self.close(code=4001)
            return
        
        # 为每个用户创建一个唯一的组名
        self.group_name = f"user_{self.user_id}"
        
        # 将用户添加到组
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # 记录会话信息
        self.session_id = await self.create_websocket_session()
        
        # 接受WebSocket连接
        await self.accept()
        
        # 发送连接成功消息
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': '连接已建立',
            'session_id': str(self.session_id)
        }))
    
    async def disconnect(self, close_code):
        """处理WebSocket断开连接"""
        if hasattr(self, 'group_name'):
            # 将用户从组中移除
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        
        # 更新会话状态
        if hasattr(self, 'session_id'):
            await self.update_websocket_session_disconnect()
    
    async def receive(self, text_data):
        """处理从WebSocket接收到的消息"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            # 记录接收到的消息
            await self.create_websocket_message(text_data, 'incoming')
            
            # 根据消息类型处理
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
            elif message_type == 'subscribe':
                # 处理订阅请求
                channels = text_data_json.get('channels', [])
                for channel in channels:
                    if channel in ['notifications', 'alerts', 'orders']:
                        # 将用户添加到额外的组
                        await self.channel_layer.group_add(
                            f"{channel}_{self.user_id}",
                            self.channel_name
                        )
                
                await self.send(text_data=json.dumps({
                    'type': 'subscription_success',
                    'channels': channels
                }))
            else:
                # 未知消息类型
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'未知的消息类型: {message_type}'
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': '无效的JSON格式'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    # 处理不同类型的消息
    
    async def notification_message(self, event):
        """处理通知消息"""
        # 直接将消息发送到WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data']
        }))
        
        # 记录发送的消息
        await self.create_websocket_message(json.dumps(event), 'outgoing')
    
    async def alert_message(self, event):
        """处理告警消息"""
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'data': event['data']
        }))
        
        # 记录发送的消息
        await self.create_websocket_message(json.dumps(event), 'outgoing')
    
    async def order_update(self, event):
        """处理订单更新消息"""
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'data': event['data']
        }))
        
        # 记录发送的消息
        await self.create_websocket_message(json.dumps(event), 'outgoing')
    
    # 数据库操作方法
    
    @database_sync_to_async
    def create_websocket_session(self):
        """创建WebSocket会话记录"""
        client_ip = self.scope.get('client')[0] if 'client' in self.scope else None
        
        session = WebSocketSession.objects.create(
            user_id=self.user_id,
            client_ip=client_ip,
            is_active=True
        )
        return session.session_id
    
    @database_sync_to_async
    def update_websocket_session_disconnect(self):
        """更新WebSocket会话断开状态"""
        try:
            session = WebSocketSession.objects.get(session_id=self.session_id)
            session.is_active = False
            session.disconnected_at = timezone.now()
            session.save()
        except WebSocketSession.DoesNotExist:
            pass
    
    @database_sync_to_async
    def create_websocket_message(self, message, direction):
        """记录WebSocket消息"""
        try:
            session = WebSocketSession.objects.get(session_id=self.session_id)
            WebSocketMessage.objects.create(
                session=session,
                direction=direction,
                message=message
            )
        except WebSocketSession.DoesNotExist:
            pass
