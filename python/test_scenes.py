"""场景功能完整测试"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def login_and_get_token():
    """登录获取token"""
    print("🔐 用户登录...")
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
        "username": "13800138000",
        "password": "123456"
    })
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ 登录成功")
        return token
    else:
        print(f"❌ 登录失败: {response.text}")
        return None


def test_create_scene(token):
    """测试创建场景"""
    print("\n🎭 测试创建场景...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 创建"回家模式"场景
    scene_data = {
        "name": "回家模式",
        "description": "回家时自动开启客厅灯和空调，营造舒适环境",
        "icon": "🏡",
        "color": "#e74c3c",
        "actions": [
            {
                "device_id": 1,  # 客厅主灯
                "action": "turn_on",
                "parameters": {
                    "power": True,
                    "brightness": 80,
                    "color": "#FFFFFF"
                }
            },
            {
                "device_id": 4,  # 客厅空调
                "action": "turn_on",
                "parameters": {
                    "power": True,
                    "temperature": 25,
                    "mode": "cool"
                }
            }
        ]
    }

    response = requests.post(f"{BASE_URL}/api/v1/scenes/", headers=headers, json=scene_data)

    if response.status_code == 200:
        scene = response.json()
        print(f"✅ 场景创建成功: {scene['name']}")
        print(f"   场景ID: {scene['id']}")
        print(f"   包含设备: {scene['device_count']}个")
        print(f"   图标: {scene['icon']} 颜色: {scene['color']}")
        return scene["id"]
    else:
        print(f"❌ 场景创建失败: {response.text}")
        return None


def test_create_sleep_scene(token):
    """创建睡眠模式场景"""
    print("\n🌙 测试创建睡眠场景...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    scene_data = {
        "name": "睡眠模式",
        "description": "睡前关闭所有灯光，调节空调到睡眠温度",
        "icon": "🌙",
        "color": "#2c3e50",
        "actions": [
            {
                "device_id": 1,  # 客厅主灯
                "action": "turn_off",
                "parameters": {"power": False}
            },
            {
                "device_id": 2,  # 卧室台灯
                "action": "turn_off",
                "parameters": {"power": False}
            },
            {
                "device_id": 4,  # 客厅空调
                "action": "sleep_mode",
                "parameters": {
                    "power": True,
                    "temperature": 26,
                    "mode": "sleep"
                }
            }
        ]
    }

    response = requests.post(f"{BASE_URL}/api/v1/scenes/", headers=headers, json=scene_data)

    if response.status_code == 200:
        scene = response.json()
        print(f"✅ 睡眠场景创建成功: {scene['name']}")
        return scene["id"]
    else:
        print(f"❌ 睡眠场景创建失败: {response.text}")
        return None


def test_get_scenes(token):
    """测试获取场景列表"""
    print("\n📋 测试获取场景列表...")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/scenes/", headers=headers)

    if response.status_code == 200:
        scenes = response.json()
        print(f"✅ 获取场景列表成功，共 {len(scenes)} 个场景:")
        for scene in scenes:
            print(f"   {scene['icon']} {scene['name']} - {scene['device_count']}个设备")
            print(f"      描述: {scene.get('description', '无')}")
        return scenes
    else:
        print(f"❌ 获取场景列表失败: {response.text}")
        return []


def test_execute_scene(token, scene_id, scene_name):
    """测试执行场景 - 核心功能"""
    print(f"\n🚀 测试执行场景: {scene_name}")

    headers = {"Authorization": f"Bearer {token}"}

    print("   执行中...")
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/scenes/{scene_id}/execute", headers=headers)
    end_time = time.time()

    if response.status_code == 200:
        result = response.json()
        print("✅ 场景执行成功！")
        print(f"   场景名称: {result['scene_name']}")
        print(f"   执行状态: {'成功' if result['success'] else '部分失败'}")
        print(f"   总设备数: {result['total_devices']}")
        print(f"   成功数: {result['success_count']}")
        print(f"   失败数: {result['failed_count']}")
        print(f"   服务器执行时间: {result['execution_time']}秒")
        print(f"   网络总时间: {end_time - start_time:.2f}秒")

        print("\n📊 执行详情:")
        for action in result['executed_actions']:
            print(f"   ✅ {action['device_name']} ({action['device_type']})")
            print(f"      动作: {action['action']}")
            print(f"      状态变化: {action['old_status']} → {action['new_status']}")

        if result['failed_actions']:
            print("\n❌ 失败动作:")
            for failed in result['failed_actions']:
                print(f"   ❌ 设备ID {failed['device_id']}: {failed['error']}")

        return True
    else:
        print(f"❌ 场景执行失败: {response.text}")
        return False


def test_scene_history(token, scene_id):
    """测试查看场景执行历史"""
    print(f"\n📈 测试查看场景执行历史...")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/scenes/{scene_id}/history", headers=headers)

    if response.status_code == 200:
        history = response.json()
        print(f"✅ 获取执行历史成功: {history['scene_name']}")
        print(f"   历史记录数: {history['total_executions']}")

        for i, log in enumerate(history['execution_history'][:3], 1):  # 显示最近3次
            success_status = "✅ 成功" if log['success'] else "❌ 失败"
            print(f"   {i}. {success_status} - {log['execution_time']}")
            if log['execution_result']:
                result = log['execution_result']
                print(f"      执行时间: {result.get('execution_time', 0):.2f}秒")
                print(f"      成功动作: {len(result.get('executed_actions', []))}")

        return True
    else:
        print(f"❌ 获取执行历史失败: {response.text}")
        return False


def test_scene_performance(token, scene_id):
    """测试场景执行性能"""
    print(f"\n⚡ 测试场景执行性能（连续执行3次）...")

    execution_times = []
    for i in range(3):
        print(f"   第 {i + 1} 次执行...")
        headers = {"Authorization": f"Bearer {token}"}

        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/v1/scenes/{scene_id}/execute", headers=headers)
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            execution_times.append({
                'server_time': result['execution_time'],
                'network_time': end_time - start_time,
                'success': result['success']
            })
            print(f"      服务器: {result['execution_time']:.2f}s, 网络总时间: {end_time - start_time:.2f}s")
        else:
            print(f"      ❌ 执行失败")

        time.sleep(1)  # 间隔1秒

    if execution_times:
        avg_server = sum(t['server_time'] for t in execution_times) / len(execution_times)
        avg_network = sum(t['network_time'] for t in execution_times) / len(execution_times)
        success_rate = sum(1 for t in execution_times if t['success']) / len(execution_times) * 100

        print(f"\n📊 性能统计:")
        print(f"   平均服务器执行时间: {avg_server:.2f}秒")
        print(f"   平均网络总时间: {avg_network:.2f}秒")
        print(f"   成功率: {success_rate:.1f}%")


def main():
    """主测试流程"""
    print("🎭 鸿蒙智能家居 - 场景功能完整测试")
    print("=" * 60)

    # 登录获取token
    token = login_and_get_token()
    if not token:
        return

    # 创建测试场景
    home_scene_id = test_create_scene(token)
    sleep_scene_id = test_create_sleep_scene(token)

    # 获取场景列表
    scenes = test_get_scenes(token)

    # 执行场景测试
    if home_scene_id:
        test_execute_scene(token, home_scene_id, "回家模式")
        time.sleep(2)  # 等待2秒

        # 执行睡眠场景
        if sleep_scene_id:
            test_execute_scene(token, sleep_scene_id, "睡眠模式")

        # 查看执行历史
        test_scene_history(token, home_scene_id)

        # 性能测试
        test_scene_performance(token, home_scene_id)

    print("\n" + "=" * 60)
    print("🎉 场景功能测试完成！")
    print("\n💡 接下来您可以:")
    print("   1. 在API文档中手动测试更多功能")
    print("   2. 开发前端界面来使用这些API")
    print("   3. 扩展其他后端功能（MQTT、实时推送等）")


if __name__ == "__main__":
    main()