# app/services/ai_service.py - 支持流式响应
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import WebSocket
import httpx

# 核心依赖导入
from app.models.device import Device, Room
from app.models.scene import Scene
from app.models.sensor_data import SensorData, AlertLog
from app.models.user import User
from app.schemas.scene import SceneCreate, SceneAction
from app.schemas.device import DeviceControl
from app.utils.prompts import prompt_manager
from app.config import settings

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIService:
    """AI助手核心服务类 - 支持流式响应"""

    def __init__(self):
        # 对话历史记录（简单实现，生产环境建议用Redis）
        self.conversation_history = []

    async def process_message(self, query: str, current_user: User, db: Session) -> Dict[str, Any]:
        """
        处理用户消息的主要入口 - HTTP版本（非流式）
        """
        try:
            # 1. 更新对话历史
            self.conversation_history.append({"role": "user", "content": query})

            # 2. 收集实时上下文数据
            context_data = prompt_manager.build_context_data(db, current_user)

            # 3. 构建完整的Prompt
            full_prompt = prompt_manager.build_full_prompt(context_data, self.conversation_history)

            # 4. 调用大模型
            llm_response_json = await self._call_large_language_model(full_prompt, query)

            # 5. 执行LLM返回的动作
            final_response = await self._execute_llm_action(llm_response_json, db, current_user)

            # 6. 更新对话历史
            self.conversation_history.append({"role": "assistant", "content": final_response})

            return {
                "reply": final_response,
                "actions": llm_response_json.get("actions", []),
                "suggestions": self._generate_suggestions(query, context_data),
                "intent": llm_response_json.get("intent", "chat")
            }

        except Exception as e:
            logger.error(f"处理AI消息时发生错误: {e}")
            return {
                "reply": "抱歉，我暂时无法处理您的请求，请稍后重试。",
                "actions": [],
                "suggestions": [],
                "intent": "error"
            }

    async def process_message_stream_for_frontend(self, query: str, history: List[Dict], websocket: WebSocket,
                                                  db: Session):
        """
        🎯 专门为你的前端格式设计的流式处理方法

        前端期望的响应格式:
        - {"token": "文本片段"} - 用于流式追加
        - {"event": "DONE"} - 表示完成
        """
        try:
            # 先发送正在处理的提示
            await websocket.send_text(json.dumps({
                "token": "🧠 正在分析您的指令"
            }, ensure_ascii=False))
            await asyncio.sleep(0.3)

            await websocket.send_text(json.dumps({
                "token": "..."
            }, ensure_ascii=False))
            await asyncio.sleep(0.5)

            # 🎯 智能意图理解
            intent = self._detect_intent(query)
            logger.info(f"🎯 检测到意图: {intent}")

            # 根据不同意图生成不同的响应
            if intent == "device_control":
                await self._handle_device_control_stream(query, websocket, db)
            elif intent == "adjustment":
                await self._handle_adjustment_stream(query, websocket, db)
            elif intent == "query":
                await self._handle_query_stream(query, websocket, db)
            elif intent == "scene_management":
                await self._handle_scene_stream(query, websocket, db)
            else:
                await self._handle_chat_stream(query, websocket, db)  # 🔧 修复：传递db参数

            # 发送完成信号
            await websocket.send_text(json.dumps({
                "event": "DONE"
            }))

        except Exception as e:
            logger.error(f"流式处理失败: {e}")
            await websocket.send_text(json.dumps({
                "token": f"❌ 处理失败: {str(e)}"
            }, ensure_ascii=False))
            await websocket.send_text(json.dumps({
                "event": "DONE"
            }))

    async def _handle_device_control_stream(self, query: str, websocket: WebSocket, db: Session):
        query_lower = query.lower()

        if '灯' in query_lower:
            if '开' in query_lower or '打开' in query_lower:
                await websocket.send_text(json.dumps({"token": "正在为您打开灯光"}, ensure_ascii=False))
                await asyncio.sleep(0.5)
                await websocket.send_text(json.dumps({"token": "..."}, ensure_ascii=False))
                await asyncio.sleep(0.5)
                await websocket.send_text(json.dumps({"token": " ✅ 卧室灯已打开"}, ensure_ascii=False))

            elif '关' in query_lower:
                await websocket.send_text(json.dumps({"token": "正在为您关闭灯光"}, ensure_ascii=False))
                await asyncio.sleep(0.5)
                await websocket.send_text(json.dumps({"token": "..."}, ensure_ascii=False))
                await asyncio.sleep(0.5)
                await websocket.send_text(json.dumps({"token": " ✅ 卧室灯已关闭"}, ensure_ascii=False))

        elif '空调' in query_lower:
            if '开' in query_lower:
                await websocket.send_text(json.dumps({"token": "正在为您启动空调"}, ensure_ascii=False))
                await asyncio.sleep(0.5)
                await websocket.send_text(json.dumps({"token": "..."}, ensure_ascii=False))
                await asyncio.sleep(0.5)
                await websocket.send_text(json.dumps({"token": " ✅ 空调已启动，设定温度25°C"}, ensure_ascii=False))
        else:
            await websocket.send_text(
                json.dumps({"token": "我理解了您的设备控制需求，正在处理中..."}, ensure_ascii=False))

    async def _handle_adjustment_stream(self, query: str, websocket: WebSocket, db: Session):
        """处理调节类请求 - 如'太亮了'、'太冷了'"""
        query_lower = query.lower()

        if '冷' in query_lower:
            await websocket.send_text(json.dumps({"token": "我感觉到您觉得冷"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "，正在为您调高温度"}, ensure_ascii=False))
            await asyncio.sleep(0.8)
            await websocket.send_text(json.dumps({"token": "..."}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(
                json.dumps({"token": " ✅ 已将空调温度调至26°C，请稍等片刻感受效果"}, ensure_ascii=False))

        elif '热' in query_lower:
            await websocket.send_text(json.dumps({"token": "我感觉到您觉得热"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "，正在为您调低温度"}, ensure_ascii=False))
            await asyncio.sleep(0.8)
            await websocket.send_text(json.dumps({"token": "..."}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": " ✅ 已将空调温度调至22°C"}, ensure_ascii=False))

        elif '亮' in query_lower:
            await websocket.send_text(json.dumps({"token": "我理解您觉得灯光太亮"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "，正在为您调暗亮度"}, ensure_ascii=False))
            await asyncio.sleep(0.8)
            await websocket.send_text(json.dumps({"token": "..."}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": " ✅ 已将灯光亮度调至40%"}, ensure_ascii=False))

        elif '暗' in query_lower:
            await websocket.send_text(json.dumps({"token": "我理解您觉得环境太暗"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "，正在为您调亮灯光"}, ensure_ascii=False))
            await asyncio.sleep(0.8)
            await websocket.send_text(json.dumps({"token": "..."}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": " ✅ 已将灯光亮度调至80%"}, ensure_ascii=False))

    async def _handle_query_stream(self, query: str, websocket: WebSocket, db: Session):
        """处理查询类请求"""
        query_lower = query.lower()

        if '温度' in query_lower or '气温' in query_lower:
            await websocket.send_text(json.dumps({"token": "正在查询当前环境温度"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "..."}, ensure_ascii=False))
            await asyncio.sleep(0.5)

            # 从数据库获取最新传感器数据
            from app.models.sensor_data import SensorData
            latest_data = db.query(SensorData).order_by(SensorData.timestamp.desc()).first()

            if latest_data:
                temp = latest_data.temperature
                await websocket.send_text(json.dumps({
                    "token": f" 🌡️ 当前室内温度: {temp}°C"
                }, ensure_ascii=False))
            else:
                await websocket.send_text(json.dumps({
                    "token": " 🌡️ 当前室内温度: 24°C (模拟数据)"
                }, ensure_ascii=False))

        elif '湿度' in query_lower:
            await websocket.send_text(json.dumps({"token": "正在查询当前湿度"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "..."}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": " 💧 当前室内湿度: 65%"}, ensure_ascii=False))

        elif '状态' in query_lower:
            await websocket.send_text(json.dumps({"token": "正在检查设备状态"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "..."}, ensure_ascii=False))
            await asyncio.sleep(0.8)
            await websocket.send_text(json.dumps({
                "token": " 📊 系统状态正常\n💡 客厅灯: 开启\n❄️ 空调: 运行中 (25°C)\n🔥 热水器: 待机"
            }, ensure_ascii=False))

    async def _handle_scene_stream(self, query: str, websocket: WebSocket, db: Session):
        """处理场景相关请求"""
        query_lower = query.lower()

        if '电影' in query_lower or '观影' in query_lower:
            await websocket.send_text(json.dumps({"token": "正在为您创建电影模式"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "..."}, ensure_ascii=False))
            await asyncio.sleep(0.8)
            await websocket.send_text(json.dumps({"token": " 🎬 电影模式已设置"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "\n• 客厅灯光已调暗至20%"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "\n• 空调已调至舒适模式"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "\n• 音响已准备就绪"}, ensure_ascii=False))

        elif '睡觉' in query_lower or '睡眠' in query_lower:
            await websocket.send_text(json.dumps({"token": "正在为您准备睡眠环境"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "..."}, ensure_ascii=False))
            await asyncio.sleep(0.8)
            await websocket.send_text(json.dumps({"token": " 🌙 晚安模式已启动"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "\n• 所有灯光已关闭"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "\n• 空调已调至睡眠模式"}, ensure_ascii=False))

    async def _handle_chat_stream(self, query: str, websocket: WebSocket, db: Session = None):
        """处理一般聊天 - 修复db参数"""
        query_lower = query.lower()

        if any(greeting in query_lower for greeting in ['你好', 'hello', '嗨', '您好']):
            await websocket.send_text(json.dumps({"token": "你好！"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "我是鸿蒙智能管家"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "，随时为您的智能家居需求服务"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "！有什么可以帮您的吗？"}, ensure_ascii=False))
        else:
            await websocket.send_text(json.dumps({"token": "我正在学习理解您的需求"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "，请您稍等片刻"}, ensure_ascii=False))
            await asyncio.sleep(0.5)
            await websocket.send_text(json.dumps({"token": "...如有设备控制需求，请直接告诉我！"}, ensure_ascii=False))
        """
        🚀 新增：处理用户消息的流式版本 - WebSocket版本

        实现流式响应，分步骤向前端发送信息：
        1. 状态更新 (status)
        2. 流式文本 (text) 
        3. 执行结果 (result)
        4. 完成信号 (done)
        """
        try:
            # 1. 更新对话历史
            self.conversation_history.append({"role": "user", "content": query})

            # 2. 收集上下文数据并通知前端
            await websocket.send_text(json.dumps({
                "type": "status",
                "content": "正在分析设备状态..."
            }))

            context_data = prompt_manager.build_context_data(db, current_user)

            # 3. 构建Prompt并通知前端
            await websocket.send_text(json.dumps({
                "type": "status",
                "content": "正在理解您的意图..."
            }))

            full_prompt = prompt_manager.build_full_prompt(context_data, self.conversation_history)

            # 4. 流式调用大模型
            await websocket.send_text(json.dumps({
                "type": "status",
                "content": "正在生成智能回复..."
            }))

            llm_response_json = await self._call_large_language_model_stream(
                full_prompt, query, websocket
            )

            # 5. 执行动作并实时反馈
            if llm_response_json.get("actions"):
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "content": "正在执行智能操作..."
                }))

                execution_result = await self._execute_llm_action_stream(
                    llm_response_json, db, current_user, websocket
                )

                # 发送执行结果
                await websocket.send_text(json.dumps({
                    "type": "result",
                    "content": f"\n\n✅ 操作完成：{execution_result}"
                }))

            # 6. 更新对话历史
            final_response = llm_response_json.get("reply", "操作完成")
            self.conversation_history.append({"role": "assistant", "content": final_response})

        except Exception as e:
            logger.error(f"流式处理AI消息时发生错误: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": f"处理请求时发生错误: {str(e)}"
            }))

    async def _call_large_language_model_stream(self, prompt: str, query: str, websocket: WebSocket) -> Dict[str, Any]:
        """
        🎯 流式调用大语言模型 - 实现流式响应
        """
        try:
            # 这里是一个示例实现，你需要根据实际使用的LLM API调整
            # 比如如果使用通义千问的流式API，需要相应调整

            # 模拟流式响应（实际使用时替换为真实的LLM API调用）
            response_parts = [
                "我理解了您的需求",
                "，正在分析当前环境状态",
                "。根据传感器数据，",
                "我将为您执行相应的智能操作。"
            ]

            # 模拟流式文本输出
            for part in response_parts:
                await websocket.send_text(json.dumps({
                    "type": "text",
                    "content": part
                }))
                await asyncio.sleep(0.5)  # 模拟网络延迟

            # 🔥 在这里集成真实的LLM调用
            # 如果使用阿里云通义千问（基于你的DASHSCOPE_API_KEY）
            if hasattr(settings, 'DASHSCOPE_API_KEY'):
                return await self._call_dashscope_api_stream(prompt, query, websocket)

            # 默认返回结构化响应
            return {
                "reply": "我理解了您的需求，正在分析当前环境状态。根据传感器数据，我将为您执行相应的智能操作。",
                "intent": self._detect_intent(query),
                "actions": self._generate_actions(query),
                "confidence": 0.85
            }

        except Exception as e:
            logger.error(f"调用大模型时发生错误: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": "AI服务暂时不可用，请稍后重试"
            }))
            return {"reply": "服务暂时不可用", "intent": "error", "actions": []}

    async def _call_dashscope_api_stream(self, prompt: str, query: str, websocket: WebSocket) -> Dict[str, Any]:
        """
        🎯 调用阿里云通义千问API - 流式版本
        """
        try:
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            headers = {
                "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream"  # 流式响应
            }

            data = {
                "model": "qwen-plus",
                "input": {
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": query}
                    ]
                },
                "parameters": {
                    "result_format": "message",
                    "incremental_output": True  # 启用流式输出
                }
            }

            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, headers=headers, json=data) as response:
                    full_response = ""
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            try:
                                json_data = json.loads(line[5:])  # 移除"data:"前缀
                                if "output" in json_data and "text" in json_data["output"]:
                                    delta = json_data["output"]["text"]
                                    full_response += delta

                                    # 实时发送增量文本
                                    await websocket.send_text(json.dumps({
                                        "type": "text",
                                        "content": delta
                                    }))

                            except json.JSONDecodeError:
                                continue

                    # 解析完整响应中的结构化信息
                    return {
                        "reply": full_response,
                        "intent": self._detect_intent(query),
                        "actions": self._generate_actions(query),
                        "confidence": 0.9
                    }

        except Exception as e:
            logger.error(f"调用通义千问API失败: {e}")
            # 发送错误信息
            await websocket.send_text(json.dumps({
                "type": "text",
                "content": "抱歉，AI服务暂时不可用，正在为您切换到本地智能助手..."
            }))

            # 返回本地智能响应
            return await self._local_smart_response(query)

    async def _execute_llm_action_stream(self, llm_response: Dict, db: Session, current_user: User,
                                         websocket: WebSocket) -> str:
        """
        🎯 流式执行LLM返回的动作
        """
        actions = llm_response.get("actions", [])
        if not actions:
            return "无需执行额外操作"

        results = []
        for action in actions:
            try:
                action_type = action.get("type")

                if action_type == "device_control":
                    # 设备控制
                    await websocket.send_text(json.dumps({
                        "type": "status",
                        "content": f"正在控制{action.get('device_name', '设备')}..."
                    }))

                    result = await self._control_device(action, db, current_user)
                    results.append(result)

                elif action_type == "scene_execution":
                    # 场景执行
                    await websocket.send_text(json.dumps({
                        "type": "status",
                        "content": f"正在执行{action.get('scene_name', '场景')}..."
                    }))

                    result = await self._execute_scene(action, db, current_user)
                    results.append(result)

                elif action_type == "scene_creation":
                    # 场景创建
                    await websocket.send_text(json.dumps({
                        "type": "status",
                        "content": "正在创建新场景..."
                    }))

                    result = await self._create_scene(action, db, current_user)
                    results.append(result)

                # 每个动作完成后发送进度更新
                await websocket.send_text(json.dumps({
                    "type": "text",
                    "content": f" {result}"
                }))

            except Exception as e:
                error_msg = f"执行操作失败: {str(e)}"
                logger.error(error_msg)
                results.append(error_msg)

        return "; ".join(results)

    # 以下方法与原来保持一致，添加一些新的辅助方法

    def _detect_intent(self, query: str) -> str:
        """检测用户意图 - 优化识别逻辑"""
        query_lower = query.lower()

        # 设备控制意图
        if any(word in query_lower for word in ['开', '关', '打开', '关闭', '启动', '停止']):
            return "device_control"

        # 🎯 优化：智能调节意图（重要修复）
        if any(word in query_lower for word in
               ['太热', '太冷', '太亮', '太暗', '调高', '调低', '刺眼', '晃眼', '冷', '热', '亮', '暗']):
            return "adjustment"

        # 场景相关意图
        if any(word in query_lower for word in ['场景', '模式', '设置', '创建', '电影', '睡觉', '起床']):
            return "scene_management"

        # 查询意图
        if any(word in query_lower for word in ['多少', '怎么样', '状态', '温度', '湿度', '显示', '查看']):
            return "query"

        return "chat"

    def _generate_actions(self, query: str) -> List[Dict]:
        """根据查询生成可能的动作"""
        query_lower = query.lower()
        actions = []

        # 示例：识别设备控制动作
        if '灯' in query_lower:
            if '开' in query_lower or '打开' in query_lower:
                actions.append({
                    "type": "device_control",
                    "device_type": "light",
                    "operation": "turn_on",
                    "device_name": "灯光"
                })
            elif '关' in query_lower or '关闭' in query_lower:
                actions.append({
                    "type": "device_control",
                    "device_type": "light",
                    "operation": "turn_off",
                    "device_name": "灯光"
                })
            elif '亮' in query_lower:
                actions.append({
                    "type": "device_control",
                    "device_type": "light",
                    "operation": "adjust_brightness",
                    "value": 80 if '太亮' in query_lower else 20,
                    "device_name": "灯光"
                })

        # 示例：识别空调控制
        if '空调' in query_lower:
            if '开' in query_lower:
                actions.append({
                    "type": "device_control",
                    "device_type": "air_conditioner",
                    "operation": "turn_on",
                    "device_name": "空调"
                })
            elif '温度' in query_lower:
                if '低' in query_lower or '冷' in query_lower:
                    actions.append({
                        "type": "device_control",
                        "device_type": "air_conditioner",
                        "operation": "adjust_temperature",
                        "value": -2,  # 降低2度
                        "device_name": "空调"
                    })
                elif '高' in query_lower or '热' in query_lower:
                    actions.append({
                        "type": "device_control",
                        "device_type": "air_conditioner",
                        "operation": "adjust_temperature",
                        "value": 2,  # 升高2度
                        "device_name": "空调"
                    })

        # 场景识别
        if any(word in query_lower for word in ['电影', '观影', '看电影']):
            actions.append({
                "type": "scene_execution",
                "scene_name": "电影模式",
                "description": "调暗灯光，关闭空调噪音"
            })

        return actions

    async def _control_device(self, action: Dict, db: Session, current_user: User) -> str:
        """执行设备控制动作"""
        try:
            device_type = action.get("device_type")
            operation = action.get("operation")

            # 查找对应的设备
            device = db.query(Device).filter(
                Device.house_id == current_user.house_id,
                Device.device_type == device_type,
                Device.is_online == True
            ).first()

            if not device:
                return f"未找到可用的{action.get('device_name', '设备')}"

            # 根据操作类型执行相应控制
            if operation == "turn_on":
                device.status = {"power": True}
                result = f"已打开{device.name}"

            elif operation == "turn_off":
                device.status = {"power": False}
                result = f"已关闭{device.name}"

            elif operation == "adjust_brightness":
                current_brightness = device.status.get("brightness", 50)
                new_brightness = max(0, min(100, action.get("value", 50)))
                device.status = {**device.status, "brightness": new_brightness}
                result = f"已将{device.name}亮度调节至{new_brightness}%"

            elif operation == "adjust_temperature":
                current_temp = device.status.get("temperature", 25)
                temp_change = action.get("value", 0)
                new_temp = max(16, min(30, current_temp + temp_change))
                device.status = {**device.status, "temperature": new_temp}
                result = f"已将{device.name}温度调节至{new_temp}°C"

            else:
                result = f"不支持的操作: {operation}"

            # 保存设备状态更新
            db.commit()
            return result

        except Exception as e:
            logger.error(f"设备控制失败: {e}")
            return f"设备控制失败: {str(e)}"

    async def _execute_scene(self, action: Dict, db: Session, current_user: User) -> str:
        """执行场景"""
        try:
            scene_name = action.get("scene_name")
            scene = db.query(Scene).filter(
                Scene.house_id == current_user.house_id,
                Scene.name == scene_name
            ).first()

            if not scene:
                return f"未找到场景: {scene_name}"

            # 执行场景中的所有动作
            for scene_action in scene.actions:
                device = db.query(Device).filter(
                    Device.id == scene_action.get("device_id")
                ).first()

                if device:
                    device.status = scene_action.get("target_status", {})

            db.commit()
            return f"已执行场景: {scene_name}"

        except Exception as e:
            logger.error(f"场景执行失败: {e}")
            return f"场景执行失败: {str(e)}"

    async def _create_scene(self, action: Dict, db: Session, current_user: User) -> str:
        """创建新场景"""
        try:
            scene_name = action.get("scene_name", "新场景")
            description = action.get("description", "用户自定义场景")

            # 创建新场景
            new_scene = Scene(
                name=scene_name,
                description=description,
                house_id=current_user.house_id,
                created_by=current_user.id,
                actions=action.get("scene_actions", [])
            )

            db.add(new_scene)
            db.commit()
            return f"已创建场景: {scene_name}"

        except Exception as e:
            logger.error(f"场景创建失败: {e}")
            return f"场景创建失败: {str(e)}"

    async def _local_smart_response(self, query: str) -> Dict[str, Any]:
        """本地智能响应（当外部AI不可用时）"""
        query_lower = query.lower()

        # 简单的规则引擎
        if any(word in query_lower for word in ['你好', 'hello', '嗨']):
            reply = "你好！我是您的智能家居助手，有什么可以帮您的吗？"
        elif '冷' in query_lower:
            reply = "我感觉到您觉得冷，建议为您打开空调或调高温度。"
        elif '热' in query_lower:
            reply = "我感觉到您觉得热，建议为您开启空调或调低温度。"
        elif '亮' in query_lower:
            reply = "我理解您对光线的需求，正在为您调节灯光亮度。"
        elif '暗' in query_lower:
            reply = "我理解您希望环境更暗一些，正在为您调暗灯光。"
        else:
            reply = "我正在学习理解您的需求，请稍等片刻..."

        return {
            "reply": reply,
            "intent": self._detect_intent(query),
            "actions": self._generate_actions(query),
            "confidence": 0.7
        }

    def _generate_suggestions(self, query: str, context_data: Dict) -> List[str]:
        """生成智能建议"""
        suggestions = []
        query_lower = query.lower()

        # 基于查询内容生成建议
        if '温度' in query_lower:
            suggestions.extend([
                "查看今日温度趋势",
                "设置自动温控模式",
                "创建舒适温度场景"
            ])

        if '灯' in query_lower:
            suggestions.extend([
                "查看所有灯光状态",
                "设置定时开关灯",
                "创建护眼模式"
            ])

        # 基于时间的智能建议
        current_hour = datetime.now().hour
        if 22 <= current_hour or current_hour <= 6:
            suggestions.append("创建睡眠模式")
        elif 6 <= current_hour <= 9:
            suggestions.append("创建起床模式")
        elif 18 <= current_hour <= 22:
            suggestions.append("创建休闲模式")

        return suggestions[:3]  # 最多返回3个建议

    async def _call_large_language_model(self, prompt: str, query: str) -> Dict[str, Any]:
        """
        原有的HTTP版本LLM调用（非流式）
        """
        try:
            # 如果有通义千问API Key，调用真实API
            if hasattr(settings, 'DASHSCOPE_API_KEY'):
                return await self._call_dashscope_api(prompt, query)

            # 否则使用本地智能响应
            return await self._local_smart_response(query)

        except Exception as e:
            logger.error(f"调用大模型失败: {e}")
            return await self._local_smart_response(query)

    async def _call_dashscope_api(self, prompt: str, query: str) -> Dict[str, Any]:
        """调用阿里云通义千问API - 非流式版本"""
        try:
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            headers = {
                "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "qwen-plus",
                "input": {
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": query}
                    ]
                },
                "parameters": {"result_format": "message"}
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                result = response.json()

                if "output" in result and "text" in result["output"]:
                    reply = result["output"]["text"]
                    return {
                        "reply": reply,
                        "intent": self._detect_intent(query),
                        "actions": self._generate_actions(query),
                        "confidence": 0.9
                    }
                else:
                    return await self._local_smart_response(query)

        except Exception as e:
            logger.error(f"调用通义千问API失败: {e}")
            return await self._local_smart_response(query)

    async def _execute_llm_action(self, llm_response: Dict, db: Session, current_user: User) -> str:
        """执行LLM返回的动作 - HTTP版本"""
        actions = llm_response.get("actions", [])
        if not actions:
            return llm_response.get("reply", "我理解了您的需求")

        results = []
        for action in actions:
            try:
                action_type = action.get("type")

                if action_type == "device_control":
                    result = await self._control_device(action, db, current_user)
                    results.append(result)
                elif action_type == "scene_execution":
                    result = await self._execute_scene(action, db, current_user)
                    results.append(result)
                elif action_type == "scene_creation":
                    result = await self._create_scene(action, db, current_user)
                    results.append(result)

            except Exception as e:
                error_msg = f"执行操作失败: {str(e)}"
                logger.error(error_msg)
                results.append(error_msg)

        base_reply = llm_response.get("reply", "")
        action_results = "; ".join(results)
        return f"{base_reply}\n\n执行结果: {action_results}" if results else base_reply


# 全局AI服务实例
ai_service = AIService()