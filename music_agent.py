"""
音乐推荐Agent主入口
提供完整的音乐推荐功能
"""

import asyncio
import os
from typing import Dict, Any, Optional, List

# 在导入其他模块之前加载配置
try:
    from config.settings_loader import load_and_setup_settings
    load_and_setup_settings()
except Exception as e:
    print(f"警告: 无法从 setting.json 加载配置: {e}")

from config.logging_config import get_logger
from graphs.music_graph import MusicRecommendationGraph
from schemas.music_state import MusicAgentState

logger = get_logger(__name__)


class MusicRecommendationAgent:
    """音乐推荐智能体主类"""
    
    def __init__(self):
        """初始化智能体"""
        self.graph = MusicRecommendationGraph()
        self.app = self.graph.get_app()
        logger.info("MusicRecommendationAgent 初始化完成")
    
    async def get_recommendations(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        获取音乐推荐
        
        Args:
            query: 用户查询/需求
            chat_history: 对话历史
            user_preferences: 用户偏好数据
            
        Returns:
            包含推荐结果的字典
        """
        try:
            logger.info(f"开始处理音乐推荐请求: {query}")
            
            # 构建初始状态
            initial_state: MusicAgentState = {
                "input": query,
                "chat_history": chat_history or [],
                "user_preferences": user_preferences or {},
                "favorite_songs": [],
                "intent_type": "",
                "intent_parameters": {},
                "intent_context": "",
                "search_results": [],
                "recommendations": [],
                "explanation": "",
                "final_response": "",
                "playlist": None,
                "step_count": 0,
                "error_log": [],
                "metadata": {}
            }
            
            # 执行工作流
            config = {
                "recursion_limit": 50
            }
            result = await self.app.ainvoke(initial_state, config=config)
            
            logger.info("音乐推荐完成")
            
            return {
                "success": True,
                "response": result.get("final_response", ""),
                "recommendations": result.get("recommendations", []),
                "search_results": result.get("search_results", []),
                "intent_type": result.get("intent_type", ""),
                "explanation": result.get("explanation", ""),
                "playlist": result.get("playlist"),
                "errors": result.get("error_log", [])
            }
            
        except Exception as e:
            logger.error(f"处理音乐推荐请求时发生错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "response": "抱歉，处理你的请求时遇到了问题。请稍后重试。",
                "recommendations": [],
                "search_results": [],
                "errors": [{"node": "main", "error": str(e)}]
            }
    
    async def search_music(
        self,
        query: str,
        genre: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        搜索音乐
        
        Args:
            query: 搜索关键词
            genre: 流派过滤
            limit: 返回结果数量
            
        Returns:
            搜索结果
        """
        try:
            from tools.music_tools import music_search_tool
            
            logger.info(f"搜索音乐: query='{query}', genre='{genre}'")
            
            songs = await music_search_tool.search_songs(query, genre, limit)
            
            return {
                "success": True,
                "results": [song.to_dict() for song in songs],
                "count": len(songs)
            }
            
        except Exception as e:
            logger.error(f"搜索音乐失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "count": 0
            }
    
    async def get_recommendations_by_mood(
        self,
        mood: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        根据心情推荐音乐
        
        Args:
            mood: 心情描述
            limit: 推荐数量
            
        Returns:
            推荐结果
        """
        try:
            from tools.music_tools import music_recommender
            
            logger.info(f"根据心情推荐: mood='{mood}'")
            
            recommendations = await music_recommender.recommend_by_mood(mood, limit)
            
            return {
                "success": True,
                "recommendations": [rec.to_dict() for rec in recommendations],
                "count": len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"根据心情推荐失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": [],
                "count": 0
            }
    
    async def get_recommendations_by_activity(
        self,
        activity: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        根据活动场景推荐音乐
        
        Args:
            activity: 活动描述
            limit: 推荐数量
            
        Returns:
            推荐结果
        """
        try:
            from tools.music_tools import music_recommender
            
            logger.info(f"根据活动推荐: activity='{activity}'")
            
            recommendations = await music_recommender.recommend_by_activity(activity, limit)
            
            return {
                "success": True,
                "recommendations": [rec.to_dict() for rec in recommendations],
                "count": len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"根据活动推荐失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": [],
                "count": 0
            }
    
    async def get_similar_songs(
        self,
        song_title: str,
        artist: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        获取相似歌曲
        
        Args:
            song_title: 歌曲名
            artist: 艺术家
            limit: 推荐数量
            
        Returns:
            相似歌曲列表
        """
        try:
            from tools.music_tools import music_search_tool
            
            logger.info(f"获取相似歌曲: song='{song_title}', artist='{artist}'")
            
            similar = await music_search_tool.get_similar_songs(song_title, artist, limit)
            
            return {
                "success": True,
                "similar_songs": [song.to_dict() for song in similar],
                "count": len(similar)
            }
            
        except Exception as e:
            logger.error(f"获取相似歌曲失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "similar_songs": [],
                "count": 0
            }
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态信息"""
        return {
            "status": "ready",
            "agent_type": "music_recommendation",
            "features": [
                "音乐搜索",
                "心情推荐",
                "场景推荐",
                "相似歌曲推荐",
                "艺术家推荐",
                "流派推荐",
                "智能对话"
            ],
            "supported_genres": [
                "流行", "摇滚", "民谣", "电子", 
                "说唱", "抒情", "古风", "爵士"
            ]
        }


async def main():
    """主函数，用于测试"""
    # 检查环境变量
    if not os.getenv("SILICONFLOW_API_KEY"):
        print("错误: 请设置SILICONFLOW_API_KEY环境变量")
        return
    
    # 创建智能体
    agent = MusicRecommendationAgent()
    
    print("🎵 音乐推荐Agent测试")
    print("=" * 50)
    
    # 测试1: 根据心情推荐
    print("\n测试1: 根据心情推荐")
    print("-" * 30)
    result1 = await agent.get_recommendations("我现在心情很好，想听点开心的音乐")
    if result1["success"]:
        print(f"回复: {result1['response']}")
        print(f"推荐了 {len(result1['recommendations'])} 首歌")
    else:
        print(f"错误: {result1['error']}")
    
    # 测试2: 搜索音乐
    print("\n\n测试2: 搜索音乐")
    print("-" * 30)
    result2 = await agent.search_music("周杰伦")
    if result2["success"]:
        print(f"找到 {result2['count']} 首歌:")
        for song in result2['results'][:3]:
            print(f"  - {song['title']} ({song['artist']})")
    else:
        print(f"错误: {result2['error']}")
    
    # 测试3: 根据活动推荐
    print("\n\n测试3: 根据活动推荐")
    print("-" * 30)
    result3 = await agent.get_recommendations_by_activity("运动")
    if result3["success"]:
        print(f"推荐了 {result3['count']} 首适合运动的歌:")
        for rec in result3['recommendations'][:3]:
            song = rec['song']
            print(f"  - {song['title']} ({song['artist']})")
            print(f"    理由: {rec['reason']}")
    else:
        print(f"错误: {result3['error']}")
    
    # 测试4: 获取相似歌曲
    print("\n\n测试4: 获取相似歌曲")
    print("-" * 30)
    result4 = await agent.get_similar_songs("晴天", "周杰伦")
    if result4["success"]:
        print(f"找到 {result4['count']} 首相似歌曲:")
        for song in result4['similar_songs']:
            print(f"  - {song['title']} ({song['artist']})")
    else:
        print(f"错误: {result4['error']}")
    
    print("\n" + "=" * 50)
    print("测试完成！")


if __name__ == "__main__":
    asyncio.run(main())

