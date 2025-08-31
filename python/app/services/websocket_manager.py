# app/services/websocket_manager.py
"""
WebSocket连接管理器 - 管理所有活跃的WebSocket连接
"""

import json
import logging
from typing import Dict, List, Set
from datetime import datetime
from fastapi import WebSocket
from app.models.user import User

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储活跃连接 {user_id: {websocket, user_info}}
        self.active_connections: Dict[int, Dict] = {}
        # 房间连接映射 {house_id: [user_ids]}
        self.house_connections: Dict[int, Set[int]] = {}

    async def connect(self, websocket: WebSocket, user: User):
        """建立新的WebSocket连接"""
        await websocket.accept()

        # 如果用户已有连接，先断开旧连接
        if user.id in self.active_connections:
            try:
                old_ws = self.active_connections[user.id]["websocket"]
                await old_ws.close()
            except:
                pass

        # 注册新连接
        self.active_connections[user.id] = {
            "websocket": websocket,
            "user": user,
            "connected_at": datetime.now()
        }

        # 添加到房间连接映射
        if user.house_id not in self.house_connections:
            self.house_connections[user.house_id] = set()
        self.house_connections[user.house_id].add(user.id)

        logger.info(f"🔌 用户 {user.username} (ID: {user.id}) WebSocket连接已建立")

        # 发送欢迎消息
        await self.send_to_user(user.id, {
            "type": "status",
            "content": f"你好 {user.username}，我是你的鸿蒙智能管家！有什么可以帮您的吗？"
        })

    def disconnect(self, user_id: int):
        """断开WebSocket连接"""
        if user_id in self.active_connections:
            user_info = self.active_connections[user_id]
            house_id = user_info["user"].house_id

            # 从连接字典中移除
            del self.active_connections[user_id]

            # 从房间连接映射中移除
            if house_id in self.house_connections:
                self.house_connections[house_id].discard(user_id)
                if not self.house_connections[house_id]:
                    del self.house_connections[house_id]

            logger.info(f"🔌 用户 ID: {user_id} WebSocket连接已断开")

    async def send_to_user(self, user_id: int, message: Dict):
        """向指定用户发送消息"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]["websocket"]
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
                return True
            except Exception as e:
                logger.error(f"向用户 {user_id} 发送消息失败: {e}")
                self.disconnect(user_id)
                return False
        return False

    async def broadcast_to_house(self, house_id: int, message: Dict, exclude_user_id: int = None):
        """向指定房屋的所有连接用户广播消息"""
        if house_id not in self.house_connections:
            return

        user_ids = self.house_connections[house_id].copy()
        if exclude_user_id:
            user_ids.discard(exclude_user_id)

        for user_id in user_ids:
            await self.send_to_user(user_id, message)

    async def send_device_update(self, house_id: int, device_info: Dict, operator_user_id: int = None):
        """发送设备状态更新通知"""
        message = {
            "type": "device_update",
            "content": f"设备 {device_info.get('name', '未知')} 状态已更新",
            "device": device_info
        }
        await self.broadcast_to_house(house_id, message, exclude_user_id=operator_user_id)

    async def send_scene_notification(self, house_id: int, scene_name: str, operator_user_id: int = None):
        """发送场景执行通知"""
        message = {
            "type": "scene_notification",
            "content": f"场景 '{scene_name}' 已执行",
            "scene_name": scene_name
        }
        await self.broadcast_to_house(house_id, message, exclude_user_id=operator_user_id)

    async def send_alert(self, house_id: int, alert_info: Dict):
        """发送安全警报"""
        message = {
            "type": "alert",
            "content": f"⚠️ 安全警报: {alert_info.get('message', '未知警报')}",
            "alert": alert_info,
            "priority": "high"
        }
        await self.broadcast_to_house(house_id, message)

    def get_connection_stats(self) -> Dict:
        """获取连接统计信息"""
        return {
            "total_connections": len(self.active_connections),
            "active_houses": len(self.house_connections),
            "connections_per_house": {
                house_id: len(user_ids)
                for house_id, user_ids in self.house_connections.items()
            }
        }

    def is_user_connected(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self.active_connections

    def get_house_online_users(self, house_id: int) -> List[Dict]:
        """获取指定房屋的在线用户列表"""
        if house_id not in self.house_connections:
            return []

        online_users = []
        for user_id in self.house_connections[house_id]:
            if user_id in self.active_connections:
                user_info = self.active_connections[user_id]
                online_users.append({
                    "user_id": user_id,
                    "username": user_info["user"].username,
                    "role": user_info["user"].role.value,
                    "connected_at": user_info["connected_at"]
                })

        return online_users


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()