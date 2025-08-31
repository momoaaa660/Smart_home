#!/usr/bin/env python3
"""
AI对话功能测试脚本
快速测试智能家居AI助手的核心功能
"""
import requests
import json
import time
import sys

# 配置
BASE_URL = "http://localhost:8000"
TEST_USER = "13800138000"
TEST_PASSWORD = "123456"


class AITester:
    def __init__(self):
        self.token = None
        self.session = requests.Session()

    def login(self):
        """登录获取token"""
        print("🔐 正在登录测试账号...")
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/auth/login",
                data={
                    "username": TEST_USER,
                    "password": TEST_PASSWORD
                }
            )

            if response.status_code == 200:
                self.token = response.json()["access_token"]
                print("✅ 登录成功")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code}")
                print(f"响应: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False

    def test_ai_chat(self, message):
        """测试AI对话"""
        if not self.token:
            print("❌ 未登录，无法测试")
            return None

        print(f"\n👤 用户输入: {message}")
        print("🤖 AI处理中...")

        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }

            response = self.session.post(
                f"{BASE_URL}/api/v1/ai/chat",
                headers=headers,
                json={"query": message}
            )

            if response.status_code == 200:
                result = response.json()

                # 显示AI回复
                reply = result.get('reply', '无回复')
                print(f"🤖 AI回复: {reply}")

                # 显示识别的意图
                intent = result.get('intent', 'unknown')
                print(f"🎯 识别意图: {intent}")

                # 显示执行的操作
                actions = result.get('actions', [])
                if actions:
                    print("⚙️ 执行操作:")
                    for action in actions:
                        success_icon = "✅" if action.get('success', False) else "❌"
                        action_desc = action.get('action', '未知操作')
                        print(f"   {success_icon} {action_desc}")
                else:
                    print("ℹ️ 无需执行具体操作")

                # 显示建议
                suggestions = result.get('suggestions', [])
                if suggestions:
                    print("💡 AI建议:")
                    for suggestion in suggestions:
                        print(f"   • {suggestion}")

                return result

            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                return None

        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None

    def run_basic_tests(self):
        """运行基础测试用例"""
        print("\n" + "=" * 60)
        print("🧪 开始AI对话功能基础测试")
        print("=" * 60)

        # 测试用例列表
        test_cases = [
            {
                "message": "你好",
                "description": "基础问候测试"
            },
            {
                "message": "可以介绍一下自己吗？",
                "description": "自我介绍测试"
            },
            {
                "message": "客厅的灯太亮了",
                "description": "模糊意图理解 - 灯光控制"
            },
            {
                "message": "开客厅的灯",
                "description": "明确设备控制指令"
            },
            {
                "message": "空调现在多少度？",
                "description": "设备状态查询"
            },
            {
                "message": "调低一点",
                "description": "上下文对话测试"
            },
            {
                "message": "创建一个电影模式",
                "description": "场景创建功能"
            },
            {
                "message": "执行回家模式",
                "description": "场景执行功能"
            },
            {
                "message": "检查家里的安全状况",
                "description": "数据查询功能"
            }
        ]

        success_count = 0
        total_count = len(test_cases)

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 测试 {i}/{total_count}: {test_case['description']}")
            print("-" * 40)

            result = self.test_ai_chat(test_case['message'])

            if result:
                success_count += 1
                print("✅ 测试通过")
            else:
                print("❌ 测试失败")

            # 测试间隔
            if i < total_count:
                time.sleep(1)

        # 测试结果汇总
        print("\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        print(f"总测试数: {total_count}")
        print(f"成功数量: {success_count}")
        print(f"失败数量: {total_count - success_count}")
        print(f"成功率: {success_count / total_count * 100:.1f}%")

        if success_count == total_count:
            print("🎉 所有测试通过！AI对话功能正常")
        else:
            print("⚠️ 部分测试失败，请检查服务状态")

    def interactive_test(self):
        """交互式测试模式"""
        print("\n" + "=" * 60)
        print("💬 进入交互式测试模式")
        print("输入消息与AI对话，输入 'quit' 或 'exit' 退出")
        print("=" * 60)

        while True:
            try:
                message = input("\n👤 您说: ").strip()

                if not message:
                    continue

                if message.lower() in ['quit', 'exit', '退出', 'q']:
                    print("👋 再见！测试结束")
                    break

                self.test_ai_chat(message)

            except KeyboardInterrupt:
                print("\n👋 测试被中断，再见！")
                break
            except Exception as e:
                print(f"❌ 输入错误: {e}")

    def test_quick_commands(self):
        """测试快捷指令功能"""
        print("\n" + "=" * 60)
        print("⚡ 测试快捷指令功能")
        print("=" * 60)

        if not self.token:
            print("❌ 未登录，无法测试")
            return

        commands = [
            "全部开灯",
            "全部关灯",
            "回家模式",
            "睡眠模式",
            "检查安全"
        ]

        headers = {"Authorization": f"Bearer {self.token}"}

        for command in commands:
            print(f"\n🎯 测试快捷指令: {command}")

            try:
                response = self.session.post(
                    f"{BASE_URL}/api/v1/ai/quick-command",
                    headers=headers,
                    params={"command": command}
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {result.get('reply', '执行完成')}")
                else:
                    print(f"❌ 执行失败: {response.text}")

            except Exception as e:
                print(f"❌ 请求异常: {e}")

            time.sleep(0.5)

    def check_service_status(self):
        """检查服务状态"""
        print("🔍 检查服务状态...")

        try:
            # 检查基础服务
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                health = response.json()
                print("✅ 基础服务正常")
                print(f"   数据库: {health.get('database', '未知')}")
                print(f"   MQTT: {health.get('mqtt_status', '未知')}")
                print(f"   AI助手: {health.get('ai_assistant', '未知')}")
            else:
                print(f"❌ 服务异常: {response.status_code}")
                return False

            # 检查AI服务状态
            response = self.session.get(f"{BASE_URL}/api/v1/ai/status")
            if response.status_code == 200:
                ai_status = response.json()
                print("✅ AI服务正常")
                print(f"   模型: {ai_status.get('model', '未知')}")
                print(f"   对话记忆: {'开启' if ai_status.get('conversation_memory') else '关闭'}")
            else:
                print(f"⚠️ AI服务状态未知: {response.status_code}")

            return True

        except Exception as e:
            print(f"❌ 服务检查失败: {e}")
            return False


def main():
    """主函数"""
    print("🤖 鸿蒙智能家居 - AI对话功能测试工具")
    print("=" * 60)

    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            mode = "interactive"
        elif sys.argv[1] == "--quick":
            mode = "quick"
        else:
            mode = "basic"
    else:
        mode = "basic"

    tester = AITester()

    # 检查服务状态
    if not tester.check_service_status():
        print("\n❌ 服务状态异常，请确保后端服务已启动")
        print("启动命令: python app/main.py")
        return

    # 登录
    if not tester.login():
        print("\n❌ 登录失败，请检查:")
        print("1. 是否运行了 python init_data.py 初始化数据")
        print("2. 数据库是否正常")
        return

    # 根据模式运行测试
    if mode == "interactive":
        tester.interactive_test()
    elif mode == "quick":
        tester.test_quick_commands()
    else:
        tester.run_basic_tests()

        # 询问是否继续交互测试
        choice = input("\n是否进入交互模式继续测试？(y/n): ").lower().strip()
        if choice == 'y':
            tester.interactive_test()


if __name__ == "__main__":
    print("使用说明:")
    print("python test_ai_chat.py           # 运行基础测试")
    print("python test_ai_chat.py --interactive  # 交互式测试")
    print("python test_ai_chat.py --quick       # 快捷指令测试")
    print()

    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 测试被中断，再见！")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()