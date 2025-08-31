import os


class Settings:
    # 数据库配置
    DATABASE_URL = "sqlite:///./data/hongmeng.db"

    DASHSCOPE_API_KEY = "sk-3f01d90099574cf1a1d8977f38986561"
    # 安全配置
    SECRET_KEY = "hongmeng_super_secret_key_2025_project"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

    # MQTT配置
    MQTT_BROKER_HOST = "localhost"  # 本地MQTT broker地址
    MQTT_BROKER_PORT = 1883  # MQTT端口
    MQTT_USERNAME = ""  # MQTT用户名（可选）
    MQTT_PASSWORD = ""  # MQTT密码（可选）

    # 应用配置
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 8000

    # 项目信息
    PROJECT_NAME = "鸿蒙智能家居API"
    VERSION = "1.0.0"
    DESCRIPTION = "基于FastAPI的智能家居后端系统"

    # AI服务配置
    DASHSCOPE_API_KEY = "sk-3f01d90099574cf1a1d8977f38986561"  # 你的通义千问API Key
    AI_MODEL = "qwen-plus"
    AI_TIMEOUT = 30

    # WebSocket配置
    WEBSOCKET_HEARTBEAT_INTERVAL = 30  # 心跳间隔（秒）
    MAX_WEBSOCKET_CONNECTIONS = 100  # 最大连接数

settings = Settings()