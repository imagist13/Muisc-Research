"""测试配置加载"""
from config.settings_loader import load_and_setup_settings
from llms.siliconflow_llm import get_chat_model
import os

try:
    # 先显示加载前的状态
    print("=" * 60)
    print("加载前:")
    print(f"  API Key: {os.getenv('SILICONFLOW_API_KEY', '未设置')[:20] if os.getenv('SILICONFLOW_API_KEY') else '未设置'}...")
    print(f"  模型: {os.getenv('SILICONFLOW_MODEL', '未设置')}")
    print()
    
    # 加载配置
    settings = load_and_setup_settings()
    print("✅ 配置加载成功！")
    print(f"从 JSON 读取的模型: {settings.get('SILICONFLOW_CHAT_MODEL', '未设置')}")
    print()
    
    print("加载后环境变量:")
    print(f"  API Key: {os.getenv('SILICONFLOW_API_KEY', '未设置')[:20] if os.getenv('SILICONFLOW_API_KEY') else '未设置'}...")
    print(f"  模型: {os.getenv('SILICONFLOW_MODEL', '未设置')}")
    print()
    
    # 测试 get_chat_model 是否正确使用配置
    print("测试 get_chat_model():")
    chat_model = get_chat_model()
    print(f"  ✅ 成功创建 ChatOpenAI 实例")
    print(f"  使用的模型: {chat_model.model_name}")
    print()
    
    if chat_model.model_name == settings.get('SILICONFLOW_CHAT_MODEL'):
        print("✅ 模型配置正确！使用的是 setting.json 中的模型")
    else:
        print(f"⚠️  模型不匹配！期望: {settings.get('SILICONFLOW_CHAT_MODEL')}, 实际: {chat_model.model_name}")
    
    print("=" * 60)
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    import traceback
    traceback.print_exc()

