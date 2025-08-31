# app/api/ai_chat.py
"""
AI对话API路由 - 完全适配你的最新前端代码
"""

import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Body, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import datetime
import logging

# 核心依赖导入
from app.database import get_db
from app.models.user import User, UserRole
from app.api.auth import get_current_user
from app.services.ai_service import ai_service

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API路由
router = APIRouter()


# ==================== WebSocket 聊天端点 - 适配新的前端消息格式 ====================

@router.websocket("/ws/chat")
async def websocket_ai_chat(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    🚀 WebSocket AI聊天端点 - 完全适配你的最新前端

    前端连接: ws://127.0.0.1:8000/ws/chat

    前端消息格式:
    {
        "message": "用户输入的文本",
        "history": [{"role": "user", "content": "..."}, ...]
    }

    后端响应格式 (匹配你的前端处理):
    {
        "token": "流式文本片段"  // 用于追加到 lastMessage.content
    }
    或
    {
        "event": "DONE"  // 表示一轮对话结束
    }
    """
    await websocket.accept()
    logger.info("🔌 WebSocket AI聊天连接建立")

    # 发送连接成功的初始token
    await websocket.send_text(json.dumps({
        "token": "🏠 鸿蒙智能管家已连接，随时为您服务！"
    }, ensure_ascii=False))

    # 发送完成信号
    await websocket.send_text(json.dumps({
        "event": "DONE"
    }))

    try:
        while True:
            # 接收前端消息
            message_text = await websocket.receive_text()
            logger.info(f"📩 收到前端消息: {message_text}")

            try:
                # 解析前端发送的JSON消息
                message_data = json.loads(message_text)
                user_input = message_data.get("message", "")
                conversation_history = message_data.get("history", [])

                logger.info(f"👤 用户输入: {user_input}")
                logger.info(f"💬 对话历史长度: {len(conversation_history)}")

                if not user_input.strip():
                    await websocket.send_text(json.dumps({
                        "token": "请输入您的问题。"
                    }, ensure_ascii=False))
                    await websocket.send_text(json.dumps({"event": "DONE"}))
                    continue

                # 🤖 调用AI服务处理消息（适配新的流式格式）
                await ai_service.process_message_stream_for_frontend(
                    query=user_input,
                    history=conversation_history,
                    websocket=websocket,
                    db=db
                )

            except json.JSONDecodeError:
                # 如果不是JSON格式，作为纯文本处理
                await websocket.send_text(json.dumps({
                    "token": f"收到消息: {message_text}"
                }, ensure_ascii=False))
                await websocket.send_text(json.dumps({"event": "DONE"}))

            except Exception as e:
                logger.error(f"处理消息时发生错误: {e}")
                await websocket.send_text(json.dumps({
                    "token": f"❌ 处理失败: {str(e)}"
                }, ensure_ascii=False))
                await websocket.send_text(json.dumps({"event": "DONE"}))

    except WebSocketDisconnect:
        logger.info("🔌 WebSocket连接断开")
    except Exception as e:
        logger.error(f"WebSocket异常: {e}")


# ==================== HTTP API 接口 (保持兼容) ====================

@router.post("/chat")
async def handle_chat(
        query: str = Body(..., embed=True),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """HTTP方式的AI对话接口 - 保持兼容"""
    # 访客权限检查
    if current_user.role == UserRole.GUEST:
        allowed_keywords = ['灯', '开', '关', '你好', '状态', '温度', '湿度']
        if not any(keyword in query.lower() for keyword in allowed_keywords):
            raise HTTPException(
                status_code=403,
                detail="访客只能使用基础设备控制和查询功能"
            )

    try:
        result = await ai_service.process_message(query, current_user, db)
        return {
            "reply": result.get("reply", "我理解了您的需求"),
            "actions": result.get("actions", []),
            "suggestions": result.get("suggestions", []),
            "intent": result.get("intent", "chat"),
            "timestamp": datetime.now().isoformat(),
            "user": current_user.username
        }
    except Exception as e:
        logger.error(f"处理AI对话时发生错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="处理您的请求时发生内部错误，请稍后重试。")


# ==================== 管理接口 ====================

@router.get("/status")
async def get_ai_status():
    """获取AI服务状态"""
    return {
        "ai_service": "active",
        "model": "鸿蒙智能管家",
        "communication": ["HTTP", "WebSocket"],
        "features": {
            "模糊意图理解": True,  # 灯太亮了 → 自动调暗
            "上下文长对话": True,  # 空调多少度？低一点？
            "一键创建场景": True,  # 设置电影模式
            "实时数据分析": True,  # 可燃气体报警、设备故障
            "习惯学习": True,  # 每日七点起床任务
            "动态调整": True,  # 下雨不浇花
            "streaming_response": True  # 流式响应
        },
        "supported_languages": ["中文"],
        "websocket_format": {
            "input": {"message": "用户输入", "history": "对话历史"},
            "output": {"token": "流式文本"},
            "complete": {"event": "DONE"}
        },
        "status": "运行中",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/conversation-history")
async def get_conversation_history(current_user: User = Depends(get_current_user)):
    """获取对话历史"""
    if current_user.role == UserRole.GUEST:
        raise HTTPException(status_code=403, detail="访客无法查看对话历史")

    try:
        return {
            "conversation_history": ai_service.conversation_history[-20:],
            "user": current_user.username,
            "total_messages": len(ai_service.conversation_history),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}")


@router.delete("/conversation-history")
async def clear_conversation_history(current_user: User = Depends(get_current_user)):
    """清空对话历史"""
    if current_user.role == UserRole.GUEST:
        raise HTTPException(status_code=403, detail="访客无法清空对话历史")

    try:
        ai_service.conversation_history = []
        return {
            "message": "🗑️ 对话历史已清空",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"清空对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空对话历史失败: {str(e)}")


@router.post("/test")
async def test_ai_function(
        test_query: str = Body(..., embed=True),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """AI功能测试接口"""
    logger.info(f"🧪 测试AI功能，查询: {test_query}")

    try:
        result = await ai_service.process_message(test_query, current_user, db)
        return {
            "test_query": test_query,
            "ai_response": result,
            "test_time": datetime.now().isoformat(),
            "status": "✅ 测试完成"
        }
    except Exception as e:
        logger.error(f"AI功能测试失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")