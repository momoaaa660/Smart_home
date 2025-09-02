from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.device import Device, Room
from app.models.scene import Scene
from app.models.sensor_data import SensorData, AlertLog
from app.models.user import User, UserRole
from datetime import datetime, timedelta
import json

def init_demo_data():
    """初始化演示数据"""
    db = SessionLocal()
    try:
        print("🚀 开始初始化演示数据...")
        
        # 清空现有数据（可选）
        print("📝 清理现有数据...")
        db.query(AlertLog).delete()
        db.query(SensorData).delete()
        db.query(Scene).delete()
        db.query(Device).delete()
        db.query(Room).delete()
        db.query(User).delete()
        db.commit()
        
        # 1. 创建用户数据
        print("👤 创建用户数据...")
        users = [
            User(
                id=1,
                phone="13812345678",
                username="张先生",
                hashed_password="$2b$12$hash_password_here",
                role=UserRole.OWNER,
                house_id=1,
                is_active=True
            ),
            User(
                id=2,
                phone="13987654321", 
                username="李女士",
                hashed_password="$2b$12$hash_password_here",
                role=UserRole.MEMBER,
                house_id=1,
                is_active=True
            )
        ]
        db.add_all(users)
        db.commit()
        
        # 2. 创建房间数据
        print("🏠 创建房间数据...")
        rooms = [
            Room(id=1, name="客厅", house_id=1),
            Room(id=2, name="卧室", house_id=1),
            Room(id=3, name="厨房", house_id=1),
            Room(id=4, name="书房", house_id=1),
            Room(id=5, name="卫生间", house_id=1),
            Room(id=6, name="阳台", house_id=1)
        ]
        db.add_all(rooms)
        db.commit()
        
        # 3. 创建设备数据
        print("💡 创建设备数据...")
        devices = [
            # 客厅设备
            Device(
                id=1, name="客厅主灯", device_type="light",
                device_id="light_living_main", room_id=1, house_id=1,
                status={"power": True, "brightness": 80, "color": "#FFFFFF"},
                is_online=True
            ),
            Device(
                id=2, name="客厅电视", device_type="tv",
                device_id="tv_living_001", room_id=1, house_id=1,
                status={"power": False, "volume": 25, "channel": "CCTV1"},
                is_online=True
            ),
            Device(
                id=3, name="客厅空调", device_type="airconditioner",
                device_id="ac_living_001", room_id=1, house_id=1,
                status={"power": True, "temperature": 26, "mode": "cool", "fan_speed": 2},
                is_online=True
            ),
            Device(
                id=4, name="客厅窗帘", device_type="curtain",
                device_id="curtain_living_001", room_id=1, house_id=1,
                status={"position": 60, "auto_mode": False},
                is_online=True
            ),
            
            # 卧室设备
            Device(
                id=5, name="卧室主灯", device_type="light",
                device_id="light_bedroom_main", room_id=2, house_id=1,
                status={"power": False, "brightness": 100, "color": "#FFFFFF"},
                is_online=True
            ),
            Device(
                id=6, name="卧室台灯", device_type="light",
                device_id="light_bedroom_desk", room_id=2, house_id=1,
                status={"power": True, "brightness": 40, "color": "#FFE4B5"},
                is_online=True
            ),
            Device(
                id=7, name="卧室空调", device_type="airconditioner",
                device_id="ac_bedroom_001", room_id=2, house_id=1,
                status={"power": False, "temperature": 24, "mode": "cool", "fan_speed": 1},
                is_online=True
            ),
            Device(
                id=8, name="卧室音箱", device_type="speaker",
                device_id="speaker_bedroom_001", room_id=2, house_id=1,
                status={"power": False, "volume": 30, "playing": ""},
                is_online=True
            ),
            
            # 厨房设备
            Device(
                id=9, name="厨房灯", device_type="light",
                device_id="light_kitchen_001", room_id=3, house_id=1,
                status={"power": False, "brightness": 90},
                is_online=True
            ),
            Device(
                id=10, name="厨房排气扇", device_type="fan",
                device_id="fan_kitchen_001", room_id=3, house_id=1,
                status={"power": False, "speed": 0},
                is_online=True
            ),
            
            # 书房设备
            Device(
                id=12, name="书房灯", device_type="light",
                device_id="light_study_001", room_id=4, house_id=1,
                status={"power": True, "brightness": 85, "color": "#F0F8FF"},
                is_online=True
            ),
            Device(
                id=13, name="书房加湿器", device_type="humidifier",
                device_id="humidifier_study_001", room_id=4, house_id=1,
                status={"power": True, "humidity_target": 55, "water_level": 80},
                is_online=True
            ),
            
            # 传感器设备
            Device(
                id=16, name="客厅环境传感器", device_type="sensor",
                device_id="sensor_living_env", room_id=1, house_id=1,
                status={"temperature": 25.5, "humidity": 45, "light": 300},
                is_online=True
            ),
            Device(
                id=17, name="厨房安全传感器", device_type="sensor",
                device_id="sensor_kitchen_safety", room_id=3, house_id=1,
                status={"gas_level": 15, "flame_detected": False, "smoke_level": 5},
                is_online=True
            )
        ]
        db.add_all(devices)
        db.commit()
        
        # 4. 创建场景数据
        print("🎬 创建场景数据...")
        scenes = [
            Scene(
                id=1, name="回家模式", description="下班回家时自动执行的场景",
                house_id=1, created_by=1, icon="🏠", color="#4CAF50",
                actions=[
                    {"device_id": 1, "action": "turn_on", "parameters": {"power": True, "brightness": 70}},
                    {"device_id": 3, "action": "turn_on", "parameters": {"power": True, "temperature": 26}},
                    {"device_id": 4, "action": "set_position", "parameters": {"position": 30}},
                    {"device_id": 2, "action": "turn_on", "parameters": {"power": True, "channel": "新闻频道"}}
                ]
            ),
            Scene(
                id=2, name="睡眠模式", description="准备睡觉时的环境设置",
                house_id=1, created_by=1, icon="🌙", color="#9C27B0",
                actions=[
                    {"device_id": 1, "action": "turn_off", "parameters": {"power": False}},
                    {"device_id": 6, "action": "turn_on", "parameters": {"power": True, "brightness": 20, "color": "#FFB6C1"}},
                    {"device_id": 7, "action": "set_temperature", "parameters": {"power": True, "temperature": 24, "mode": "sleep"}},
                    {"device_id": 2, "action": "turn_off", "parameters": {"power": False}}
                ]
            ),
            Scene(
                id=3, name="电影模式", description="观影时的最佳环境",
                house_id=1, created_by=1, icon="🎬", color="#FF5722",
                actions=[
                    {"device_id": 1, "action": "turn_off", "parameters": {"power": False}},
                    {"device_id": 2, "action": "turn_on", "parameters": {"power": True, "volume": 35}},
                    {"device_id": 4, "action": "set_position", "parameters": {"position": 100}},
                    {"device_id": 3, "action": "set_temperature", "parameters": {"temperature": 22}}
                ]
            )
        ]
        db.add_all(scenes)
        db.commit()
        
        # 5. 创建传感器历史数据
        print("📊 创建传感器数据...")
        now = datetime.now()
        sensor_data = []
        
        # 生成过去24小时的数据
        for i in range(24):
            timestamp = now - timedelta(hours=i)
            
            # 客厅环境数据
            sensor_data.append(SensorData(
                device_id="sensor_living_env",
                house_id=1,
                temperature=25.0 + (i % 5) * 0.5,  # 变化的温度
                humidity=45.0 + (i % 10),
                light_intensity=300.0 - i * 10,
                timestamp=timestamp
            ))
            
            # 厨房安全数据
            sensor_data.append(SensorData(
                device_id="sensor_kitchen_safety", 
                house_id=1,
                temperature=23.0 + (i % 3) * 0.3,
                humidity=50.0 + (i % 8),
                gas_level=10.0 + (i % 4) * 2,
                flame_detected=False,
                timestamp=timestamp
            ))
        
        db.add_all(sensor_data)
        db.commit()
        
        # 6. 创建一些警报日志
        print("⚠️ 创建警报数据...")
        alerts = [
            AlertLog(
                house_id=1,
                device_id="sensor_kitchen_safety",
                alert_type="gas",
                message="厨房检测到可燃气体浓度轻微超标",
                severity="medium",
                is_resolved=True,
                created_at=now - timedelta(hours=2)
            )
        ]
        db.add_all(alerts)
        db.commit()
        
        print("✅ 演示数据初始化完成！")
        print(f"📝 创建了 {len(users)} 个用户")
        print(f"🏠 创建了 {len(rooms)} 个房间") 
        print(f"💡 创建了 {len(devices)} 个设备")
        print(f"🎬 创建了 {len(scenes)} 个场景")
        print(f"📊 创建了 {len(sensor_data)} 条传感器数据")
        print(f"⚠️ 创建了 {len(alerts)} 条警报记录")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_demo_data()
