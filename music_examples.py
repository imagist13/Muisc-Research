"""
音乐推荐Agent使用示例
展示各种功能的调用方法
"""

import asyncio
import os
from music_agent import MusicRecommendationAgent


async def example_1_smart_recommendation():
    """示例1: 智能推荐 - 根据自然语言描述获取推荐"""
    print("\n" + "=" * 60)
    print("示例1: 智能推荐")
    print("=" * 60)
    
    agent = MusicRecommendationAgent()
    
    queries = [
        "我现在心情很好，想听点开心的音乐",
        "推荐一些适合运动的歌曲",
        "有没有类似《晴天》的歌曲",
    ]
    
    for query in queries:
        print(f"\n📝 用户: {query}")
        print("-" * 60)
        
        result = await agent.get_recommendations(query)
        
        if result["success"]:
            print(f"🤖 回复: {result['response']}\n")
            
            if result["recommendations"]:
                print(f"推荐了 {len(result['recommendations'])} 首歌曲:")
                for i, rec in enumerate(result["recommendations"][:3], 1):
                    song = rec.get("song", rec)
                    print(f"   {i}. {song['title']} - {song['artist']}")
                    if rec.get("reason"):
                        print(f"      💡 {rec['reason']}")
        else:
            print(f"❌ 错误: {result['error']}")
        
        print()


async def example_2_music_search():
    """示例2: 音乐搜索"""
    print("\n" + "=" * 60)
    print("示例2: 音乐搜索")
    print("=" * 60)
    
    agent = MusicRecommendationAgent()
    
    # 搜索艺术家
    print("\n🔍 搜索: 周杰伦")
    print("-" * 60)
    result = await agent.search_music("周杰伦", limit=5)
    
    if result["success"]:
        print(f"找到 {result['count']} 首歌曲:")
        for song in result["results"]:
            print(f"  - {song['title']} ({song['year']}) - {song['genre']}")
    
    # 按流派搜索
    print("\n🔍 搜索: 民谣")
    print("-" * 60)
    result = await agent.search_music("", genre="民谣", limit=5)
    
    if result["success"]:
        print(f"找到 {result['count']} 首民谣:")
        for song in result["results"]:
            print(f"  - {song['title']} - {song['artist']}")


async def example_3_mood_recommendation():
    """示例3: 根据心情推荐"""
    print("\n" + "=" * 60)
    print("示例3: 根据心情推荐")
    print("=" * 60)
    
    agent = MusicRecommendationAgent()
    
    moods = ["开心", "悲伤", "放松"]
    
    for mood in moods:
        print(f"\n😊 心情: {mood}")
        print("-" * 60)
        
        result = await agent.get_recommendations_by_mood(mood, limit=3)
        
        if result["success"]:
            for rec in result["recommendations"]:
                song = rec["song"]
                print(f"  🎵 {song['title']} - {song['artist']}")
                print(f"     {rec['reason']}")


async def example_4_activity_recommendation():
    """示例4: 根据活动场景推荐"""
    print("\n" + "=" * 60)
    print("示例4: 根据活动场景推荐")
    print("=" * 60)
    
    agent = MusicRecommendationAgent()
    
    activities = ["运动", "学习", "睡觉"]
    
    for activity in activities:
        print(f"\n🏃 活动: {activity}")
        print("-" * 60)
        
        result = await agent.get_recommendations_by_activity(activity, limit=3)
        
        if result["success"]:
            for rec in result["recommendations"]:
                song = rec["song"]
                print(f"  🎵 {song['title']} - {song['artist']} ({song['genre']})")


async def example_5_similar_songs():
    """示例5: 获取相似歌曲"""
    print("\n" + "=" * 60)
    print("示例5: 获取相似歌曲")
    print("=" * 60)
    
    agent = MusicRecommendationAgent()
    
    songs = [
        ("晴天", "周杰伦"),
        ("海阔天空", "Beyond"),
    ]
    
    for title, artist in songs:
        print(f"\n🎯 基于: {title} - {artist}")
        print("-" * 60)
        
        result = await agent.get_similar_songs(title, artist, limit=3)
        
        if result["success"]:
            print(f"找到 {result['count']} 首相似歌曲:")
            for song in result["similar_songs"]:
                print(f"  - {song['title']} - {song['artist']} ({song['genre']})")


async def example_6_agent_status():
    """示例6: 查看Agent状态"""
    print("\n" + "=" * 60)
    print("示例6: Agent状态信息")
    print("=" * 60)
    
    agent = MusicRecommendationAgent()
    status = agent.get_status()
    
    print(f"\n状态: {status['status']}")
    print(f"类型: {status['agent_type']}")
    print(f"\n功能列表:")
    for feature in status["features"]:
        print(f"  ✓ {feature}")
    
    print(f"\n支持的流派:")
    for genre in status["supported_genres"]:
        print(f"  ♪ {genre}")


async def run_all_examples():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("🎵 音乐推荐Agent - 完整示例演示")
    print("=" * 60)
    
    examples = [
        example_1_smart_recommendation,
        example_2_music_search,
        example_3_mood_recommendation,
        example_4_activity_recommendation,
        example_5_similar_songs,
        example_6_agent_status,
    ]
    
    for example in examples:
        try:
            await example()
            await asyncio.sleep(1)  # 避免请求过快
        except Exception as e:
            print(f"\n❌ 示例执行出错: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 所有示例演示完成！")
    print("=" * 60)


async def interactive_mode():
    """交互模式"""
    print("\n" + "=" * 60)
    print("🎵 音乐推荐Agent - 交互模式")
    print("=" * 60)
    print("\n输入你的需求，输入 'quit' 退出\n")
    
    agent = MusicRecommendationAgent()
    chat_history = []
    
    while True:
        try:
            query = input("你: ").strip()
            
            if query.lower() in ["quit", "exit", "退出"]:
                print("\n👋 再见！")
                break
            
            if not query:
                continue
            
            print("\n思考中...\n")
            result = await agent.get_recommendations(query, chat_history)
            
            if result["success"]:
                print(f"🤖 助手: {result['response']}\n")
                
                # 更新对话历史
                chat_history.append({"role": "user", "content": query})
                chat_history.append({"role": "assistant", "content": result["response"]})
            else:
                print(f"❌ 错误: {result['error']}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}\n")


async def main():
    """主函数"""
    # 检查环境变量
    if not os.getenv("SILICONFLOW_API_KEY"):
        print("❌ 错误: 请设置SILICONFLOW_API_KEY环境变量")
        return
    
    print("\n请选择运行模式:")
    print("1. 运行所有示例")
    print("2. 交互模式")
    print("3. 退出")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        await run_all_examples()
    elif choice == "2":
        await interactive_mode()
    else:
        print("👋 再见！")


if __name__ == "__main__":
    asyncio.run(main())

