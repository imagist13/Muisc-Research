"""
启动FastAPI服务器
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 在导入其他模块之前加载配置
try:
    from config.settings_loader import load_and_setup_settings
    load_and_setup_settings()
    print("✅ 已从 setting.json 加载配置")
except Exception as e:
    print(f"⚠️  无法从 setting.json 加载配置: {e}")
    print("   将使用环境变量中的配置")

import uvicorn

def main():
    """主函数"""
    print("=" * 60)
    print("🎵 音乐推荐API服务器 - 启动中...")
    print("=" * 60)
    print()
    
    # 检查环境变量
    if not os.getenv("SILICONFLOW_API_KEY"):
        print("❌ 警告: 未设置 SILICONFLOW_API_KEY 环境变量")
        print("   某些功能可能无法正常工作")
        print()
    
    port = int(os.getenv("API_PORT", "8501"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"📡 服务器地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print("按 Ctrl+C 停止服务")
    print("-" * 60)
    print()
    
    # 启动服务器
    try:
        # 确保在项目根目录运行
        os.chdir(project_root)
        
        # 使用字符串导入，uvicorn会自动处理
        uvicorn.run(
            "api.server:app",
            host=host,
            port=port,
            reload=True,
            reload_dirs=[str(project_root)],  # 指定reload的目录
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 API服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

