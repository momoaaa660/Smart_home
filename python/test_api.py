"""测试API功能"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """测试健康检查"""
    print("🔍 测试服务健康状态...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 服务运行正常")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ 服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


def test_user_login():
    """测试用户登录"""
    print("\n🔍 测试用户登录...")
    try:
        # 使用初始化的测试账号
        login_data = {
            "username": "13800138000",  # 房主账号
            "password": "123456"
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data=login_data  # OAuth2PasswordRequestForm使用form格式
        )

        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            print("✅ 登录成功")
            print(f"   Token: {token[:50]}...")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None


def test_get_devices(token):
    """测试获取设备列表"""
    print("\n🔍 测试获取设备列表...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/devices/", headers=headers)

        if response.status_code == 200:
            devices = response.json()
            print(f"✅ 获取设备成功，共 {len(devices)} 个设备")
            for device in devices[:3]:  # 显示前3个设备
                print(f"   - {device['name']} ({device['device_type']}) - {'在线' if device['is_online'] else '离线'}")
            return devices
        else:
            print(f"❌ 获取设备失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 获取设备异常: {e}")
        return []


def test_device_control(token, devices):
    """测试设备控制"""
    if not devices:
        print("\n⏭️ 跳过设备控制测试（无可用设备）")
        return

    print("\n🔍 测试设备控制...")
    try:
        # 找一个灯光设备进行测试
        light_device = None
        for device in devices:
            if device['device_type'] == 'light':
                light_device = device
                break

        if not light_device:
            print("⏭️ 跳过控制测试（无灯光设备）")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        control_data = {
            "action": "turn_on",
            "status": {
                "power": True,
                "brightness": 80
            }
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/devices/{light_device['id']}/control",
            headers=headers,
            json=control_data
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 设备控制成功: {light_device['name']}")
            print(f"   响应: {result['message']}")
        else:
            print(f"❌ 设备控制失败: {response.status_code}")
            print(f"   错误: {response.text}")

    except Exception as e:
        print(f"❌ 设备控制异常: {e}")


def test_sensor_data(token):
    """测试获取传感器数据"""
    print("\n🔍 测试获取传感器数据...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/sensors/latest", headers=headers)

        if response.status_code == 200:
            data = response.json()
            print("✅ 获取传感器数据成功")
            print(f"   温度: {data.get('temperature', '未知')}°C")
            print(f"   湿度: {data.get('humidity', '未知')}%")
            print(f"   安全状态: {data.get('safety_status', '未知')}")
        else:
            print(f"⚠️ 传感器数据: {response.status_code} (正常，暂无数据)")
    except Exception as e:
        print(f"❌ 获取传感器数据异常: {e}")


def main():
    """主测试函数"""
    print("🧪 鸿蒙智能家居API测试")
    print("=" * 50)

    # 测试服务健康状态
    if not test_health():
        print("\n💡 请确保服务已启动:")
        print("   python app/main.py")
        return

    # 测试用户登录
    token = test_user_login()
    if not token:
        print("\n💡 登录失败，请检查:")
        print("   1. 是否运行了 python init_data.py")
        print("   2. 数据库是否正确初始化")
        return

    # 测试设备功能
    devices = test_get_devices(token)
    test_device_control(token, devices)

    # 测试传感器数据
    test_sensor_data(token)

    print("\n" + "=" * 50)
    print("🎉 API测试完成!")
    print("\n📚 下一步可以:")
    print("   1. 访问 http://localhost:8000/docs 查看完整API文档")
    print("   2. 测试WebSocket连接（AI对话功能）")
    print("   3. 开发UniApp前端应用")


if __name__ == "__main__":
    main()