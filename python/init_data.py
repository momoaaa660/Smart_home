"""初始化示例数据"""
import sys
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models.user import User, UserRole
from app.models.device import Device, Room
from app.utils.security import get_password_hash


def init_sample_data():
    """初始化示例数据"""
    print("🚀 开始初始化数据库...")

    try:
        # 确保数据库表已创建
        init_db()

        db = SessionLocal()

        # 检查是否已有数据
        if db.query(User).first():
            print("⚠️ 数据已存在，跳过初始化")
            print("\n现有用户账号：")
            users = db.query(User).all()
            for user in users:
                print(f"  📱 {user.phone} ({user.username}) - {user.role.value}")
            return

        print("👥 创建示例用户...")
        # 创建示例用户
        users = [
            User(
                phone="13800138000",
                username="房主张三",
                hashed_password=get_password_hash("123456"),
                role=UserRole.OWNER,
                house_id=1
            ),
            User(
                phone="13800138001",
                username="家庭成员李四",
                hashed_password=get_password_hash("123456"),
                role=UserRole.MEMBER,
                house_id=1
            ),
            User(
                phone="13800138002",
                username="访客王五",
                hashed_password=get_password_hash("123456"),
                role=UserRole.GUEST,
                house_id=1
            )
        ]
        db.add_all(users)

        print("🏠 创建示例房间...")
        # 创建示例房间
        rooms = [
            Room(name="客厅", house_id=1),
            Room(name="卧室", house_id=1),
            Room(name="厨房", house_id=1),
            Room(name="阳台", house_id=1),
            Room(name="书房", house_id=1)
        ]
        db.add_all(rooms)
        db.commit()

        # 获取房间ID
        room_map = {}
        for room in db.query(Room).filter(Room.house_id == 1).all():
            room_map[room.name] = room.id

        print("💡 创建示例设备...")
        # 创建示例设备
        devices = [
            # 灯光设备
            Device(
                name="客厅主灯",
                device_type="light",
                device_id="light_001",
                room_id=room_map["客厅"],
                house_id=1,
                status={"power": False, "brightness": 100, "color": "#FFFFFF"},
                is_online=True
            ),
            Device(
                name="卧室台灯",
                device_type="light",
                device_id="light_002",
                room_id=room_map["卧室"],
                house_id=1,
                status={"power": False, "brightness": 80, "color": "#FFEEAA"},
                is_online=True
            ),
            Device(
                name="厨房照明",
                device_type="light",
                device_id="light_003",
                room_id=room_map["厨房"],
                house_id=1,
                status={"power": False, "brightness": 90},
                is_online=True
            ),

            # 家电设备
            Device(
                name="客厅空调",
                device_type="airconditioner",
                device_id="ac_001",
                room_id=room_map["客厅"],
                house_id=1,
                status={"power": False, "temperature": 25, "mode": "cool", "fan_speed": 2},
                is_online=False
            ),
            Device(
                name="厨房油烟机",
                device_type="fan",
                device_id="fan_001",
                room_id=room_map["厨房"],
                house_id=1,
                status={"power": False, "speed": 1},
                is_online=True
            ),
            Device(
                name="阳台自动浇水器",
                device_type="pump",
                device_id="pump_001",
                room_id=room_map["阳台"],
                house_id=1,
                status={"power": False, "flow_rate": 50},
                is_online=True
            ),

            # 传感器设备
            Device(
                name="客厅环境传感器",
                device_type="sensor",
                device_id="sensor_001",
                room_id=room_map["客厅"],
                house_id=1,
                status={"online": True, "battery": 85},
                is_online=True
            ),
            Device(
                name="厨房烟雾传感器",
                device_type="sensor",
                device_id="sensor_002",
                room_id=room_map["厨房"],
                house_id=1,
                status={"online": True, "battery": 92},
                is_online=True
            ),
            Device(
                name="阳台植物传感器",
                device_type="sensor",
                device_id="sensor_003",
                room_id=room_map["阳台"],
                house_id=1,
                status={"online": True, "battery": 78},
                is_online=True
            )
        ]

        db.add_all(devices)
        db.commit()

        print("\n🎉 示例数据初始化完成！")
        print("=" * 60)
        print("📱 测试账号：")
        print("  房主账号: 13800138000 / 123456")
        print("  成员账号: 13800138001 / 123456")
        print("  访客账号: 13800138002 / 123456")
        print("=" * 60)
        print("🏠 房间列表：客厅、卧室、厨房、阳台、书房")
        print("💡 设备类型：灯光、空调、风扇、水泵、传感器")
        print("=" * 60)
        print(f"📁 数据库文件: {os.path.abspath('data/hongmeng.db')}")

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    print(f"📂 当前工作目录: {os.getcwd()}")
    print(f"🐍 Python版本: {sys.version}")
    print("-" * 60)

    init_sample_data()