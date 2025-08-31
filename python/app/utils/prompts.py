# app/utils/prompts.py - 完整的智能家居AI提示词管理器
"""
智能家居AI提示词管理系统
专门为鸿蒙智能家居项目设计的AI助手提示词
"""

import json
from typing import Dict, Any, List
from datetime import datetime


class PromptManager:
    """智能家居AI提示词管理器"""

    def __init__(self):
        self.base_prompt = """
# 🏠 鸿蒙智能家居AI助手

你是"鸿蒙管家"，一个专业、贴心、高效的智能家居AI助手。你的目标是理解用户的自然语言指令，分析家居环境状态，并执行相应的智能操作。

## 🎯 核心能力

### 1. 模糊意图理解
- "灯太亮了" → 自动调暗当前房间灯光
- "感觉冷" → 分析并调节空调温度
- "准备睡觉了" → 执行晚安场景

### 2. 上下文对话记忆
- 理解多轮对话中的指代关系
- 记住用户的偏好和习惯
- 维持连贯的对话上下文

### 3. 智能场景管理
- 一键创建复合场景
- 根据用户描述自动配置设备
- 智能推荐场景优化

### 4. 数据分析与预警
- 实时监控传感器异常
- 提供环境数据分析报告
- 主动发出安全预警

### 5. 习惯学习
- 学习用户作息规律
- 主动创建自动化任务
- 个性化推荐

## 📊 决策输出格式

你必须输出标准JSON格式，包含以下字段：

```json
{
    "intent": "设备控制|场景管理|数据查询|闲聊|预警",
    "reply": "给用户的友好回复",
    "actions": [
        {
            "type": "device_control|scene_execution|scene_creation",
            "device_id": "设备ID（如果适用）",
            "device_name": "设备名称",
            "operation": "具体操作",
            "parameters": {"参数": "值"}
        }
    ],
    "confidence": 0.85,
    "suggestions": ["建议1", "建议2", "建议3"]
}
```

## 🛡️ 安全规则

1. **安全第一**: 传感器异常时优先发出警报
2. **权限控制**: 访客只能控制灯光等基础设备
3. **操作确认**: 重要操作需要用户确认
4. **错误处理**: 优雅处理设备离线等异常情况

## 💬 对话风格

- 自然、友好、专业的语调
- 使用适当的emoji增加亲和力
- 简洁明了，避免冗长说明
- 主动关心用户需求

## 🔧 设备操作规范

### 支持的设备类型：
- **light**: 灯光控制（开关、亮度、色温）
- **air_conditioner**: 空调控制（开关、温度、模式）
- **curtain**: 窗帘控制（开关、位置）
- **fan**: 风扇控制（开关、速度）
- **tv**: 电视控制（开关、频道、音量）
- **speaker**: 音响控制（开关、音量、播放）

### 常用操作：
- turn_on/turn_off: 开关控制
- adjust_brightness: 亮度调节 (0-100)
- adjust_temperature: 温度调节 (16-30°C)
- set_position: 位置设置 (0-100%)

## 📋 场景示例

### 预设场景：
- **回家模式**: 打开玄关灯，启动空调，播放欢迎音乐
- **离家模式**: 关闭所有设备，启动安防模式
- **睡眠模式**: 关闭照明，调节空调至睡眠温度
- **起床模式**: 渐亮灯光，播放轻音乐，调节室温
- **观影模式**: 调暗灯光，优化音响效果

现在请基于以下实时信息进行决策：
"""

    def build_context_data(self, db, current_user) -> str:
        """构建实时上下文数据"""
        from app.models.device import Device, Room
        from app.models.scene import Scene
        from app.models.sensor_data import SensorData, AlertLog

        # 1. 获取设备状态
        devices = db.query(Device).filter(Device.house_id == current_user.house_id).all()
        device_list = []
        for device in devices:
            room_name = "未分配房间"
            if device.room_id:
                room = db.query(Room).filter(Room.id == device.room_id).first()
                if room:
                    room_name = room.name

            device_list.append({
                "id": device.id,
                "name": device.name,
                "type": device.device_type,
                "room": room_name,
                "online": device.is_online,
                "status": device.status or {"power": False}
            })

        # 2. 获取可用场景
        scenes = db.query(Scene).filter(Scene.house_id == current_user.house_id).all()
        scene_list = [
            {
                "id": scene.id,
                "name": scene.name,
                "description": scene.description or ""
            }
            for scene in scenes
        ]

        # 3. 获取传感器数据和警报
        latest_sensor = db.query(SensorData).filter(
            SensorData.house_id == current_user.house_id
        ).order_by(SensorData.timestamp.desc()).first()

        active_alerts = db.query(AlertLog).filter(
            AlertLog.house_id == current_user.house_id,
            AlertLog.is_resolved == False
        ).all()

        sensor_summary = {
            "current_conditions": {
                "temperature": f"{latest_sensor.temperature}°C" if latest_sensor else "无数据",
                "humidity": f"{latest_sensor.humidity}%" if latest_sensor else "无数据",
                "air_quality": "良好",  # 可根据实际传感器扩展
                "last_update": latest_sensor.timestamp.strftime("%H:%M") if latest_sensor else "无"
            },
            "alerts": [
                {
                    "id": alert.id,
                    "message": alert.message,
                    "severity": alert.severity,
                    "time": alert.created_at.strftime("%H:%M")
                }
                for alert in active_alerts
            ]
        }

        # 4. 构建完整上下文
        context = f"""
## 📍 当前状态信息

**时间**: {datetime.now().strftime("%Y年%m月%d日 %H:%M")} ({self._get_time_period()})
**用户**: {current_user.username} (权限: {current_user.role.value})

## 🏠 房屋设备状态

{json.dumps(device_list, ensure_ascii=False, indent=2)}

## 🎬 可用场景

{json.dumps(scene_list, ensure_ascii=False, indent=2)}

## 🌡️ 环境监测

{json.dumps(sensor_summary, ensure_ascii=False, indent=2)}

## ⚠️ 重要提醒

- 如有未解决警报，优先处理安全问题
- 访客用户只能控制基础照明设备
- 设备离线时无法执行控制操作
- 场景执行会同时控制多个设备

请基于以上信息，理解用户意图并生成合适的JSON响应。
"""
        return context

    def build_full_prompt(self, context_data: str, conversation_history: List[Dict] = None) -> str:
        """构建包含对话历史的完整提示词"""
        # 构建对话历史部分
        history_text = ""
        if conversation_history:
            recent_history = conversation_history[-10:]  # 只保留最近10轮对话
            history_text = "\n## 💬 最近对话历史\n\n"
            for msg in recent_history:
                role = "用户" if msg["role"] == "user" else "助手"
                history_text += f"**{role}**: {msg['content']}\n"

        return f"{self.base_prompt}\n{context_data}{history_text}"

    def _get_time_period(self) -> str:
        """获取当前时间段描述"""
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return "上午"
        elif 12 <= hour < 18:
            return "下午"
        elif 18 <= hour < 22:
            return "晚上"
        else:
            return "深夜"

    def get_response_template(self, intent: str) -> Dict[str, Any]:
        """获取不同意图的响应模板"""
        templates = {
            "device_control": {
                "intent": "device_control",
                "reply": "好的，正在为您控制设备",
                "actions": [],
                "confidence": 0.8,
                "suggestions": ["查看所有设备状态", "创建快捷场景", "设置自动化规则"]
            },
            "scene_management": {
                "intent": "scene_management",
                "reply": "正在为您处理场景相关操作",
                "actions": [],
                "confidence": 0.85,
                "suggestions": ["查看所有场景", "编辑现有场景", "创建新场景"]
            },
            "query": {
                "intent": "query",
                "reply": "正在为您查询相关信息",
                "actions": [],
                "confidence": 0.9,
                "suggestions": ["查看历史数据", "设置监控提醒", "导出数据报告"]
            },
            "chat": {
                "intent": "chat",
                "reply": "我在这里为您服务，有什么需要帮助的吗？",
                "actions": [],
                "confidence": 0.7,
                "suggestions": ["查看设备状态", "执行常用场景", "环境数据概览"]
            }
        }
        return templates.get(intent, templates["chat"])


# 全局提示词管理器实例
prompt_manager = PromptManager()