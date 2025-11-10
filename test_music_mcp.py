"""
测试音乐推荐功能 - 确保使用 MCP/Spotify
"""

import asyncio
import os
import sys
from pathlib import Path

# 在导入其他模块之前加载配置
try:
    from config.settings_loader import load_and_setup_settings
    load_and_setup_settings()
    print("✅ 已从 setting.json 加载配置")
except Exception as e:
    print(f"⚠️  无法从 setting.json 加载配置: {e}")
    sys.exit(1)

# 检查环境变量
print("\n📋 检查环境变量:")
print(f"  SILICONFLOW_API_KEY: {'已设置' if os.getenv('SILICONFLOW_API_KEY') else '❌ 未设置'}")
print(f"  SPOTIFY_CLIENT_ID: {'已设置' if os.getenv('SPOTIFY_CLIENT_ID') else '❌ 未设置'}")
print(f"  SPOTIFY_CLIENT_SECRET: {'已设置' if os.getenv('SPOTIFY_CLIENT_SECRET') else '❌ 未设置'}")

if not os.getenv('SPOTIFY_CLIENT_ID') or not os.getenv('SPOTIFY_CLIENT_SECRET'):
    print("\n❌ Spotify 凭证未设置，请检查 setting.json 文件")
    sys.exit(1)

from music_agent import MusicRecommendationAgent
from config.logging_config import get_logger

logger = get_logger(__name__)


async def test_search():
    """测试搜索功能"""
    print("\n" + "=" * 60)
    print("🔍 测试1: 搜索音乐")
    print("=" * 60)
    
    agent = MusicRecommendationAgent()
    
    try:
        result = await agent.search_music("周杰伦", limit=5)
        
        if result["success"]:
            print(f"✅ 搜索成功，找到 {result['count']} 首歌曲")
            for i, song in enumerate(result['results'][:3], 1):
                print(f"\n  {i}. {song['title']} - {song['artist']}")
                if song.get('album'):
                    print(f"     专辑: {song['album']}")
                if song.get('spotify_id'):
                    print(f"     Spotify ID: {song['spotify_id']}")
                if song.get('external_url'):
                    print(f"     链接: {song['external_url']}")
        else:
            print(f"❌ 搜索失败: {result.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 搜索异常: {str(e)}")
        return False
    
    return True


async def test_mood_recommendation():
    """测试心情推荐"""
    print("\n" + "=" * 60)
    print("😊 测试2: 根据心情推荐")
    print("=" * 60)
    
    agent = MusicRecommendationAgent()
    
    try:
        result = await agent.get_recommendations_by_mood("开心", limit=5)
        
        if result["success"]:
            print(f"✅ 推荐成功，生成了 {result['count']} 条推荐")
            for i, rec in enumerate(result['recommendations'][:3], 1):
                song = rec['song']
                print(f"\n  {i}. {song['title']} - {song['artist']}")
                print(f"     理由: {rec['reason']}")
                if song.get('spotify_id'):
                    print(f"     Spotify ID: {song['spotify_id']}")
        else:
            print(f"❌ 推荐失败: {result.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 推荐异常: {str(e)}")
        return False
    
    return True


async def test_activity_recommendation():
    """测试活动推荐"""
    print("\n" + "=" * 60)
    print("🏃 测试3: 根据活动推荐")
    print("=" * 60)
    
    agent = MusicRecommendationAgent()
    
    try:
        result = await agent.get_recommendations_by_activity("运动", limit=5)
        
        if result["success"]:
            print(f"✅ 推荐成功，生成了 {result['count']} 条推荐")
            for i, rec in enumerate(result['recommendations'][:3], 1):
                song = rec['song']
                print(f"\n  {i}. {song['title']} - {song['artist']}")
                print(f"     理由: {rec['reason']}")
                if song.get('spotify_id'):
                    print(f"     Spotify ID: {song['spotify_id']}")
        else:
            print(f"❌ 推荐失败: {result.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 推荐异常: {str(e)}")
        return False
    
    return True


async def test_smart_recommendation():
    """测试智能推荐"""
    print("\n" + "=" * 60)
    print("🤖 测试4: 智能推荐（自然语言）")
    print("=" * 60)
    
    agent = MusicRecommendationAgent()
    
    try:
        result = await agent.get_recommendations("我现在心情很好，想听点开心的音乐")
        
        if result["success"]:
            print(f"✅ 智能推荐成功")
            print(f"\n回复: {result['response'][:200]}...")
            print(f"\n推荐了 {len(result['recommendations'])} 首歌曲")
            for i, rec in enumerate(result['recommendations'][:3], 1):
                song = rec.get('song', rec)
                if isinstance(song, dict):
                    print(f"\n  {i}. {song.get('title', '未知')} - {song.get('artist', '未知')}")
        else:
            print(f"❌ 智能推荐失败: {result.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 智能推荐异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("🎵 音乐推荐功能测试 - MCP/Spotify 模式")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("搜索音乐", await test_search()))
    results.append(("心情推荐", await test_mood_recommendation()))
    results.append(("活动推荐", await test_activity_recommendation()))
    results.append(("智能推荐", await test_smart_recommendation()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！MCP/Spotify 功能正常工作")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查配置和网络连接")


if __name__ == "__main__":
    asyncio.run(main())

