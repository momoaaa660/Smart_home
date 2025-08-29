from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, devices, sensors, scenes, mqtt_devices  # 添加mqtt_devices
from app.config import settings
from app.database import init_db
from app.services.mqtt_service import mqtt_service  # 添加mqtt_service
import uvicorn

init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["用户认证"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["设备管理"])
app.include_router(sensors.router, prefix="/api/v1/sensors", tags=["传感器数据"])
app.include_router(scenes.router, prefix="/api/v1/scenes", tags=["场景管理"])
app.include_router(mqtt_devices.router, prefix="/api/v1/mqtt", tags=["MQTT设备"])  # 新增

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("Starting Hongmeng Smart Home API")
    mqtt_service.start()  # 启动MQTT服务
    print(f"API docs: http://{settings.HOST}:{settings.PORT}/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("Stopping Hongmeng Smart Home API")
    mqtt_service.stop()  # 停止MQTT服务

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "mqtt_connected": mqtt_service.connected,
        "features": [
            "用户认证管理",
            "设备远程控制",
            "传感器数据监控",
            "智能场景管理",
            "MQTT硬件通信"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "database": "sqlite",
        "mqtt_status": "connected" if mqtt_service.connected else "disconnected",
        "version": settings.VERSION
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )