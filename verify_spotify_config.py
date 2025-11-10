"""
验证 Spotify 配置是否正确加载
"""

import os
import sys

# 加载配置
try:
    from config.settings_loader import load_and_setup_settings, load_settings_from_json
    settings = load_settings_from_json()
    print("📋 从 setting.json 读取的配置:")
    print(f"  SPOTIFY_CLIENT_ID: {settings.get('SPOTIFY_CLIENT_ID', 'NOT FOUND')}")
    print(f"  SPOTIFY_CLIENT_SECRET: {settings.get('SPOTIFY_CLIENT_SECRET', 'NOT FOUND')[:20]}..." if settings.get('SPOTIFY_CLIENT_SECRET') else "  SPOTIFY_CLIENT_SECRET: NOT FOUND")
    
    # 设置环境变量
    from config.settings_loader import setup_environment_from_settings
    setup_environment_from_settings(settings)
    
    print("\n🔍 环境变量检查:")
    print(f"  SPOTIFY_CLIENT_ID: {os.getenv('SPOTIFY_CLIENT_ID', 'NOT SET')}")
    print(f"  SPOTIFY_CLIENT_SECRET: {os.getenv('SPOTIFY_CLIENT_SECRET', 'NOT SET')[:20]}..." if os.getenv('SPOTIFY_CLIENT_SECRET') else "  SPOTIFY_CLIENT_SECRET: NOT SET")
    
    # 手动设置（如果还没设置）
    if not os.getenv('SPOTIFY_CLIENT_ID') and settings.get('SPOTIFY_CLIENT_ID'):
        os.environ['SPOTIFY_CLIENT_ID'] = settings['SPOTIFY_CLIENT_ID']
        print("\n✅ 手动设置 SPOTIFY_CLIENT_ID")
    
    if not os.getenv('SPOTIFY_CLIENT_SECRET') and settings.get('SPOTIFY_CLIENT_SECRET'):
        os.environ['SPOTIFY_CLIENT_SECRET'] = settings['SPOTIFY_CLIENT_SECRET']
        print("✅ 手动设置 SPOTIFY_CLIENT_SECRET")
    
    print("\n🔍 最终环境变量检查:")
    print(f"  SPOTIFY_CLIENT_ID: {os.getenv('SPOTIFY_CLIENT_ID', 'NOT SET')}")
    print(f"  SPOTIFY_CLIENT_SECRET: {'已设置' if os.getenv('SPOTIFY_CLIENT_SECRET') else 'NOT SET'}")
    
    if os.getenv('SPOTIFY_CLIENT_ID') and os.getenv('SPOTIFY_CLIENT_SECRET'):
        print("\n✅ Spotify 配置验证成功！")
        sys.exit(0)
    else:
        print("\n❌ Spotify 配置验证失败！")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

