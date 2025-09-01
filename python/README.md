# SmartHome后端
## 环境搭建
1. 创建虚拟环境
cd python && python -m venv .venv
2. 启动虚拟环境
.venv/Scripts/activate
3. 下载python依赖
pip install -r requirments.txt

> 依赖: MarkupSafe-3.0.2 aiosqlite-0.21.0 annotated-types-0.7.0 anyio-4.10.0 bcrypt-4.3.0 certifi-2025.8.3 cffi-1.17.1 click-8.2.1 colorama-0.4.6 cryptography-45.0.6 dnspython-2.7.0 ecdsa-0.19.1 email-validator-2.3.0 fastapi-0.116.1 fastapi-cli-0.0.8 fastapi-cloud-cli-0.1.5 greenlet-3.2.4 h11-0.16.0 httpcore-1.0.9 httptools-0.6.4 httpx-0.28.1 idna-3.10 jinja2-3.1.6 markdown-it-py-4.0.0 mdurl-0.1.2 paho-mqtt-2.1.0 passlib-1.7.4 pyasn1-0.6.1 pycparser-2.22 pydantic-2.11.7 pydantic-core-2.33.2 pygments-2.19.2 python-dateutil-2.9.0.post0 python-dotenv-1.1.1 python-jose-3.5.0 python-multipart-0.0.20 pyyaml-6.0.2 rich-14.1.0 rich-toolkit-0.15.0 rignore-0.6.4 rsa-4.9.1 sentry-sdk-2.35.1 shellingham-1.5.4 six-1.17.0 sniffio-1.3.1 sqlalchemy-2.0.43 starlette-0.47.3 typer-0.16.1 typing-extensions-4.15.0 typing-inspection-0.4.1 urllib3-2.5.0 uvicorn-0.35.0 watchfiles-1.1.0 websockets-15.0.1
> 
>模糊意图理解：灯太亮了
>上下文长对话：空调多少度？低一点？
>一键创建场景：我想设置一个电影模式......
>数据分析：实时分析（可燃气体报警、设备离线/传感器故障分析）、历史一览
> 习惯学习：每日七点起床，主动创建任务
> 动态调整：下雨不浇花
>
ai此时已经能够完成简单的通话，但是这些文件是不是只是简单定义了数据的传输结构，比如我现在告诉它我感觉有点冷，它能实现的业务逻辑是怎样的 
import json
from fastapi import APIRouter, Depends, HTTPException, Body,WebSocket, WebSocketDisconnect
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


@router.post("/chat")
async def handle_chat(
        query: str = Body(..., embed=True),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    if current_user.role == UserRole.GUEST:
        # 访客只能使用基础对话功能
        allowed_keywords = ['灯', '开', '关', '你好', '状态']
        if not any(keyword in query.lower() for keyword in allowed_keywords):
            raise HTTPException(
                status_code=403,
                detail="访客只能使用基础设备控制和问候功能"
            )

    try:
        # 调用AI服务处理消息
        result = await ai_service.process_message(query, current_user, db)

        return {
            "reply": result.get("reply", "我理解了您的需求"),
            "actions": result.get("actions", []),
            "suggestions": result.get("suggestions", []),
            "intent": result.get("intent", "chat"),
            "timestamp": datetime.now(),
            "user": current_user.username
        }

    except Exception as e:
        logger.error(f"处理AI对话时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="处理您的请求时发生内部错误，请稍后重试。"
        )


@router.post("/quick-command")
async def quick_command(
        command: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    快捷指令接口 - 预定义的常用操作
    """
    if current_user.role == UserRole.GUEST:
        # 访客只能使用灯光相关的快捷指令
        allowed_commands = ["全部开灯", "全部关灯"]
        if command not in allowed_commands:
            raise HTTPException(
                status_code=403,
                detail="访客只能使用基础灯光控制指令"
            )

    try:
        # 预定义的快捷指令映射
        quick_commands = {
            "全部开灯": "帮我打开所有房间的灯",
            "全部关灯": "帮我关闭所有房间的灯",
            "回家模式": "执行回家场景，开启客厅灯和空调",
            "睡眠模式": "执行睡眠场景，关闭所有设备",
            "离家模式": "执行离家场景，关闭所有电器",
            "电影模式": "调暗灯光，设置合适的观影环境",
            "检查安全": "检查所有传感器状态和安全情况"
        }

        # 将快捷指令转换为详细指令
        detailed_command = quick_commands.get(command, command)

        # 调用AI服务处理
        result = await ai_service.process_message(detailed_command, current_user, db)

        return {
            "command": command,
            "reply": result.get("reply", "指令已执行"),
            "actions": result.get("actions", []),
            "success": len(result.get("actions", [])) > 0,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"快捷指令执行失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"快捷指令执行失败: {str(e)}"
        )


@router.get("/daily-summary")
async def get_daily_summary(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取每日数据摘要"""
    if current_user.role == UserRole.GUEST:
        raise HTTPException(status_code=403, detail="访客无法查看数据摘要")

    try:
        summary = await ai_service.get_daily_summary(current_user, db)

        return {
            "summary": summary,
            "timestamp": datetime.now(),
            "user": current_user.username
        }

    except Exception as e:
        logger.error(f"生成摘要失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"生成摘要失败: {str(e)}"
        )


@router.post("/smart-suggestions")
async def get_smart_suggestions(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取智能建议"""
    if current_user.role == UserRole.GUEST:
        raise HTTPException(status_code=403, detail="访客无法获取智能建议")

    try:
        suggestions = ai_service.get_smart_suggestions(current_user, db)

        return {
            "suggestions": suggestions,
            "timestamp": datetime.now(),
            "based_on": "时间、环境数据、设备状态"
        }

    except Exception as e:
        logger.error(f"生成建议失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"生成建议失败: {str(e)}"
        )


@router.get("/conversation-history")
async def get_conversation_history(
        limit: int = 10,
        current_user: User = Depends(get_current_user)
):
    """获取对话历史"""
    if current_user.role == UserRole.GUEST:
        raise HTTPException(status_code=403, detail="访客无法查看对话历史")

    try:
        history = ai_service.conversation_history

        # 只返回最近的对话记录
        recent_history = history[-limit:] if len(history) > limit else history

        return {
            "conversation_history": recent_history,
            "total_messages": len(history),
            "user": current_user.username,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"获取对话历史失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取对话历史失败: {str(e)}"
        )


@router.delete("/conversation-history")
async def clear_conversation_history(
        current_user: User = Depends(get_current_user)
):
    """清空对话历史"""
    if current_user.role == UserRole.GUEST:
        raise HTTPException(status_code=403, detail="访客无法清空对话历史")

    try:
        ai_service.conversation_history = []

        return {
            "message": "对话历史已清空",
            "user": current_user.username,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"清空对话历史失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"清空对话历史失败: {str(e)}"
        )


@router.get("/status")
async def get_ai_status():
    """获取AI服务状态"""
    return {
        "ai_service": "active",
        "model": "智能管家模型",
        "features": {
            "intent_understanding": True,
            "context_conversation": True,
            "scene_creation": True,
            "data_analysis": True,
            "habit_learning": True,
            "dynamic_adjustment": True
        },
        "supported_languages": ["中文"],
        "voice_support": False,  # 语音功能可后续添加
        "conversation_memory": True,
        "status": "运行中",
        "timestamp": datetime.now()
    }


# 用于测试的接口
@router.post("/test")
async def test_ai_function(
        test_query: str = Body(..., embed=True),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    AI功能测试接口
    用于测试不同的AI功能模块
    """
    logger.info(f"测试AI功能，查询: {test_query}")

    # 直接调用AI服务进行测试
    result = await ai_service.process_message(test_query, current_user, db)

    return {
        "test_query": test_query,
        "ai_response": result,
        "test_time": datetime.now(),
        "status": "测试完成"
    }
