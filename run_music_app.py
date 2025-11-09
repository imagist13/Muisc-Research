"""
音乐推荐Agent快速启动脚本
"""

import os
import sys
import subprocess

# 尝试从 setting.json 加载配置
try:
    from config.settings_loader import load_and_setup_settings
    load_and_setup_settings()
    print("✅ 已从 setting.json 加载配置")
except Exception as e:
    print(f"⚠️  无法从 setting.json 加载配置: {e}")
    print("   将使用环境变量中的配置")


def check_env():
    """检查环境变量"""
    required_keys = ["SILICONFLOW_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print("❌ 缺少以下环境变量:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\n请先设置环境变量或在 setting.json 中配置:")
        print("   export SILICONFLOW_API_KEY='your-api-key'")
        print("   或在 setting.json 文件中设置 SILICONFLOW_API_KEY")
        return False
    
    print("✅ 环境变量检查通过")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("🎵 音乐推荐Agent - 启动中...")
    print("=" * 60)
    print()
    
    # 检查环境变量
    if not check_env():
        sys.exit(1)
    
    print("\n正在启动Streamlit应用...")
    print("访问地址: http://localhost:8501")
    print("按 Ctrl+C 停止服务")
    print("-" * 60)
    print()
    
    # 启动Streamlit应用
    try:
        subprocess.run([
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            "music_app.py",
            "--server.headless=true"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 音乐推荐Agent已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n你也可以手动运行:")
        print("   streamlit run music_app.py")
        sys.exit(1)


if __name__ == "__main__":
    main()

