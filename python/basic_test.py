"""测试基础配置是否正确"""


def test_config():
    try:
        from app.config import settings
        print("✅ 配置文件加载成功")
        print(f"   数据库: {settings.DATABASE_URL}")
        print(f"   项目名: {settings.PROJECT_NAME}")
        return True
    except Exception as e:
        print(f"❌ 配置文件错误: {e}")
        return False


def test_database():
    try:
        from app.database import init_db
        init_db()
        print("✅ 数据库初始化成功")
        return True
    except Exception as e:
        print(f"❌ 数据库错误: {e}")
        return False


def test_user_model():
    try:
        from app.models.user import User, UserRole
        print("✅ 用户模型导入成功")
        return True
    except Exception as e:
        print(f"❌ 用户模型错误: {e}")
        return False


if __name__ == "__main__":
    print("🧪 测试基础配置...")
    print("=" * 40)

    test_config()
    test_database()
    test_user_model()

    print("=" * 40)
    print("🎉 基础测试完成！")