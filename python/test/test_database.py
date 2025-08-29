#!/usr/bin/env python3
"""
数据库功能测试脚本
验证所有数据库操作是否正常工作
"""

from database import (
    DatabaseManager,
    save_environment_data,
    get_latest_environment_data,
    get_environment_history,
    get_recent_alerts,
    get_all_devices,
    SessionLocal,
    EnvironmentData,
    Device,
    House,
    User,
    AlertLog
)
from datetime import datetime, timedelta
import random


def test_basic_operations():
    """测试基础数据库操作"""
    print("🧪 测试基础数据库操作...")

    # 1. 测试保存环境数据
    print("\n1️⃣ 测试保存环境数据")
    test_data = {
        "temperature": 25.8,
        "humidity": 58.5,
        "smoke_detected": False,
        "flame_detected": False,
        "gas_level": 45.2,
        "light_intensity": 650.0,
        "air_quality": 78.0,
        "soil_moisture": 55.3
    }

    result = save_environment_data(house_id=1, sensor_data=test_data)
    if result:
        print(f"   ✅ 保存成功: 温度 {result['temperature']}°C, 状态 {result['safety_status']}")
    else:
        print("   ❌ 保存失败")
        return False

    # 2. 测试获取最新数据
    print("\n2️⃣ 测试获取最新数据")
    latest = get_latest_environment_data(house_id=1)
    if latest:
        print(f"   ✅ 获取成功: {latest['timestamp']} 温度 {latest['temperature']}°C")
    else:
        print("   ❌ 获取失败")
        return False

    # 3. 测试历史数据
    print("\n3️⃣ 测试历史数据查询")
    history = get_environment_history(house_id=1, hours=6)
    print(f"   ✅ 获取到 {len(history)} 条历史记录")

    # 4. 测试设备查询
    print("\n4️⃣ 测试设备查询")
    devices = get_all_devices(house_id=1)
    print(f"   ✅ 找到 {len(devices)} 个设备:")
    for device in devices[:3]:  # 显示前3个设备
        print(f"      - {device['name']} ({device['device_type']})")

    # 5. 测试警报查询
    print("\n5️⃣ 测试警报查询")
    alerts = get_recent_alerts(house_id=1, limit=5)
    print(f"   ✅ 找到 {len(alerts)} 条警报记录")

    return True


def test_data_analysis():
    """测试数据分析功能"""
    print("\n📊 数据分析测试...")

    # 获取24小时历史数据
    history = get_environment_history(house_id=1, hours=24)

    if len(history) == 0:
        print("   ⚠️ 没有历史数据")
        return

    # 温度分析
    temps = [d['temperature'] for d in history if d['temperature']]
    if temps:
        avg_temp = sum(temps) / len(temps)
        max_temp = max(temps)
        min_temp = min(temps)

        print(f"📈 温度统计 (24小时):")
        print(f"   平均: {avg_temp:.1f}°C")
        print(f"   最高: {max_temp:.1f}°C")
        print(f"   最低: {min_temp:.1f}°C")

    # 安全状态统计
    safety_counts = {}
    for data in history:
        status = data['safety_status']
        safety_counts[status] = safety_counts.get(status, 0) + 1

    print(f"🛡️ 安全状态分布:")
    for status, count in safety_counts.items():
        print(f"   {status}: {count} 次")


def test_emergency_scenarios():
    """测试紧急情况场景"""
    print("\n🚨 测试紧急情况处理...")

    # 测试烟雾警报
    print("1️⃣ 模拟烟雾检测")
    smoke_data = {
        "temperature": 28.0,
        "humidity": 45.0,
        "smoke_detected": True,  # 烟雾警报
        "flame_detected": False,
        "gas_level": 60.0
    }

    result = save_environment_data(house_id=1, sensor_data=smoke_data)
    if result and result['safety_status'] == 'warning':
        print("   ✅ 烟雾警报触发成功")

    # 测试高温警报
    print("2️⃣ 模拟高温检测")
    heat_data = {
        "temperature": 45.0,  # 高温
        "humidity": 30.0,
        "smoke_detected": False,
        "flame_detected": False,
        "gas_level": 40.0
    }

    result = save_environment_data(house_id=1, sensor_data=heat_data)
    if result:
        print("   ✅ 高温数据记录成功")

    # 检查警报是否创建
    recent_alerts = get_recent_alerts(house_id=1, limit=5)
    emergency_alerts = [a for a in recent_alerts if a['severity'] in ['critical', 'warning']]
    print(f"   ✅ 创建了 {len(emergency_alerts)} 个紧急警报")


def simulate_real_day():
    """模拟真实一天的数据变化"""
    print("\n🌅 模拟真实一天的数据...")

    choice = input("是否生成模拟数据？(y/n): ").lower().strip()
    if choice != 'y':
        print("跳过数据生成")
        return

    print("正在生成24小时模拟数据...")

    for hour in range(24):
        # 模拟真实的环境变化规律

        # 温度：白天高，夜间低
        if 6 <= hour <= 18:  # 白天
            base_temp = 22 + (hour - 12) * 0.8 + random.uniform(-2, 4)
        else:  # 夜间
            base_temp = 18 + random.uniform(-2, 3)

        # 湿度：与温度相反变化
        base_humidity = max(30, min(80, 70 - (base_temp - 20) * 1.5 + random.uniform(-5, 5)))

        # 光照：白天强，夜间弱
        if 6 <= hour <= 20:
            light = 200 + (1000 - 200) * (1 - abs(hour - 13) / 7) + random.uniform(-100, 200)
        else:
            light = random.uniform(0, 50)

        data = {
            "temperature": round(base_temp, 1),
            "humidity": round(base_humidity, 1),
            "smoke_detected": random.choice([False] * 99 + [True]),  # 1%概率
            "flame_detected": False,
            "gas_level": round(random.uniform(20, 80), 1),
            "light_intensity": round(max(0, light), 1),
            "air_quality": round(random.uniform(50, 120), 1),
            "soil_moisture": round(random.uniform(40, 70), 1)
        }

        save_environment_data(house_id=1, sensor_data=data)

        if hour % 6 == 0:  # 每6小时显示一次
            print(f"   {hour:02d}:00 - 温度: {data['temperature']}°C, 湿度: {data['humidity']}%")

    print("✅ 24小时模拟数据生成完成")


def main():
    """主测试函数"""
    print("🏠 智能家居数据库功能测试")
    print("=" * 60)

    # 确保数据库已初始化
    db_manager = DatabaseManager()
    db_manager.create_tables()
    db_manager.create_table()
    # 检查是否有示例数据
    db = SessionLocal()
    house_count = db.query(House).count()
    db.close()

    if house_count == 0:
        print("📂 没有找到示例数据，正在初始化...")
        db_manager.init_sample_data()

    # 运行测试
    print("\n🧪 开始功能测试...")

    # 1. 基础操作测试
    if not test_basic_operations():
        print("❌ 基础测试失败，停止测试")
        return

    # 2. 数据分析测试
    test_data_analysis()

    # 3. 紧急情况测试
    test_emergency_scenarios()

    # 4. 模拟真实数据
    simulate_real_day()

    # 5. 最终统计
    print("\n" + "=" * 60)
    print("📊 最终数据统计:")

    db = SessionLocal()
    try:
        env_count = db.query(EnvironmentData).count()
        device_count = db.query(Device).count()
        alert_count = db.query(AlertLog).count()

        print(f"   📈 环境数据记录: {env_count} 条")
        print(f"   🔌 智能设备: {device_count} 个")
        print(f"   🚨 警报记录: {alert_count} 条")

        # 显示最新数据
        latest = get_latest_environment_data(house_id=1)
        if latest:
            print(f"   🌡️ 当前温度: {latest['temperature']}°C")
            print(f"   💧 当前湿度: {latest['humidity']}%")
            print(f"   🛡️ 安全状态: {latest['safety_status']}")

    finally:
        db.close()

    print("\n🎉 所有测试完成！")
    print("💡 接下来可以:")
    print("   1. 用 'DB Browser for SQLite' 查看数据库")
    print("   2. 开发 FastAPI 接口")
    print("   3. 连接真实的传感器设备")


if __name__ == "__main__":
    main()