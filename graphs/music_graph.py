"""
音乐推荐Agent的工作流图
"""

import json
import re
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from config.logging_config import get_logger
from llms.siliconflow_llm import get_chat_model
from schemas.music_state import MusicAgentState
from tools.music_tools import get_music_search_tool, get_music_recommender
from prompts.music_prompts import (
    MUSIC_INTENT_ANALYZER_PROMPT,
    MUSIC_RECOMMENDATION_EXPLAINER_PROMPT,
    MUSIC_CHAT_RESPONSE_PROMPT
)

logger = get_logger(__name__)

# 延迟初始化 llm，避免在模块导入时配置未加载
_llm = None

def get_llm():
    """获取LLM实例（延迟初始化）"""
    global _llm
    if _llm is None:
        _llm = get_chat_model()
    return _llm


def _clean_json_from_llm(llm_output: str) -> str:
    """从LLM的输出中提取并清理JSON字符串"""
    match = re.search(r"```(?:json)?(.*)```", llm_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return llm_output.strip()


class MusicRecommendationGraph:
    """音乐推荐工作流图"""
    
    def __init__(self):
        self.workflow = self._build_graph()
    
    def get_app(self) -> CompiledStateGraph:
        """获取编译后的应用"""
        return self.workflow
    
    async def analyze_intent(self, state: MusicAgentState) -> Dict[str, Any]:
        """
        节点1: 分析用户意图
        识别用户想要做什么（搜索、推荐、聊天等）
        """
        logger.info("--- [步骤 1] 分析用户意图 ---")
        
        user_input = state.get("input", "")
        
        try:
            # 调用LLM分析意图
            prompt = MUSIC_INTENT_ANALYZER_PROMPT.format(user_input=user_input)
            response = await get_llm().ainvoke(prompt)
            
            # 解析JSON响应
            cleaned_json = _clean_json_from_llm(response.content)
            intent_data = json.loads(cleaned_json)
            
            logger.info(f"识别到意图类型: {intent_data.get('intent_type')}")
            
            return {
                "intent_type": intent_data.get("intent_type", "general_chat"),
                "intent_parameters": intent_data.get("parameters", {}),
                "intent_context": intent_data.get("context", ""),
                "step_count": state.get("step_count", 0) + 1
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"解析意图JSON失败: {str(e)}")
            # 如果解析失败，默认为通用聊天
            return {
                "intent_type": "general_chat",
                "intent_parameters": {},
                "intent_context": user_input,
                "step_count": state.get("step_count", 0) + 1,
                "error_log": state.get("error_log", []) + [
                    {"node": "analyze_intent", "error": "JSON解析失败"}
                ]
            }
        except Exception as e:
            logger.error(f"意图分析失败: {str(e)}")
            return {
                "intent_type": "general_chat",
                "intent_parameters": {},
                "intent_context": user_input,
                "step_count": state.get("step_count", 0) + 1,
                "error_log": state.get("error_log", []) + [
                    {"node": "analyze_intent", "error": str(e)}
                ]
            }
    
    def route_by_intent(self, state: MusicAgentState) -> str:
        """
        路由函数: 根据意图类型决定下一步
        """
        intent_type = state.get("intent_type", "general_chat")
        logger.info(f"根据意图 '{intent_type}' 进行路由")
        
        if intent_type == "search":
            return "search_songs"
        elif intent_type.startswith("create_playlist"):
            # 创建歌单意图，先分析用户偏好
            return "analyze_user_preferences"
        elif intent_type in ["recommend_by_mood", "recommend_by_activity", 
                            "recommend_by_genre", "recommend_by_artist", 
                            "recommend_by_favorites"]:
            return "generate_recommendations"
        else:
            return "general_chat"
    
    async def search_songs_node(self, state: MusicAgentState) -> Dict[str, Any]:
        """
        节点2a: 搜索歌曲
        """
        logger.info("--- [步骤 2a] 搜索歌曲 ---")
        
        parameters = state.get("intent_parameters", {})
        query = parameters.get("query", "")
        genre = parameters.get("genre")
        
        try:
            # 执行搜索
            search_tool = get_music_search_tool()
            results = await search_tool.search_songs(
                query=query,
                genre=genre,
                limit=10
            )
            
            # 转换为字典格式
            search_results = [song.to_dict() for song in results]
            
            logger.info(f"搜索到 {len(search_results)} 首歌曲")
            
            return {
                "search_results": search_results,
                "recommendations": search_results[:5],  # 取前5首作为推荐
                "step_count": state.get("step_count", 0) + 1
            }
            
        except Exception as e:
            logger.error(f"搜索歌曲失败: {str(e)}")
            return {
                "search_results": [],
                "recommendations": [],
                "step_count": state.get("step_count", 0) + 1,
                "error_log": state.get("error_log", []) + [
                    {"node": "search_songs", "error": str(e)}
                ]
            }
    
    async def generate_recommendations_node(self, state: MusicAgentState) -> Dict[str, Any]:
        """
        节点2b: 生成推荐
        根据不同的意图类型调用不同的推荐方法
        """
        logger.info("--- [步骤 2b] 生成音乐推荐 ---")
        
        intent_type = state.get("intent_type")
        parameters = state.get("intent_parameters", {})
        
        try:
            recommender = get_music_recommender()
            search_tool = get_music_search_tool()
            recommendations = []
            
            if intent_type == "recommend_by_mood":
                mood = parameters.get("mood", "开心")
                recs = await recommender.recommend_by_mood(mood, limit=5)
                recommendations = [rec.to_dict() for rec in recs]
                
            elif intent_type == "recommend_by_activity":
                activity = parameters.get("activity", "放松")
                recs = await recommender.recommend_by_activity(activity, limit=5)
                recommendations = [rec.to_dict() for rec in recs]
                
            elif intent_type == "recommend_by_genre":
                genre = parameters.get("genre", "流行")
                songs = await search_tool.get_songs_by_genre(genre, limit=5)
                # 转换为推荐格式
                recommendations = [{
                    "song": song.to_dict(),
                    "reason": f"这是一首优秀的{genre}作品",
                    "similarity_score": 0.85
                } for song in songs]
                
            elif intent_type == "recommend_by_artist":
                artist = parameters.get("artist", "")
                songs = await search_tool.get_songs_by_artist(artist, limit=5)
                recommendations = [{
                    "song": song.to_dict(),
                    "reason": f"{artist}的经典作品",
                    "similarity_score": 0.9
                } for song in songs]
                
            elif intent_type == "recommend_by_favorites":
                favorite_songs = parameters.get("favorite_songs", [])
                if favorite_songs:
                    recs = await recommender.recommend_by_favorites(favorite_songs, limit=5)
                    recommendations = [rec.to_dict() for rec in recs]
            
            logger.info(f"生成了 {len(recommendations)} 条推荐")
            
            return {
                "recommendations": recommendations,
                "step_count": state.get("step_count", 0) + 1
            }
            
        except Exception as e:
            logger.error(f"生成推荐失败: {str(e)}")
            return {
                "recommendations": [],
                "step_count": state.get("step_count", 0) + 1,
                "error_log": state.get("error_log", []) + [
                    {"node": "generate_recommendations", "error": str(e)}
                ]
            }
    
    async def general_chat_node(self, state: MusicAgentState) -> Dict[str, Any]:
        """
        节点2c: 通用聊天
        处理一般性的音乐话题聊天
        """
        logger.info("--- [步骤 2c] 通用音乐聊天 ---")
        
        user_message = state.get("input", "")
        chat_history = state.get("chat_history", [])
        
        try:
            # 格式化对话历史
            history_text = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in chat_history[-5:]  # 只取最近5条
            ])
            
            # 调用LLM生成回复
            prompt = MUSIC_CHAT_RESPONSE_PROMPT.format(
                chat_history=history_text,
                user_message=user_message
            )
            response = await get_llm().ainvoke(prompt)
            
            logger.info("生成聊天回复")
            
            return {
                "final_response": response.content,
                "step_count": state.get("step_count", 0) + 1
            }
            
        except Exception as e:
            logger.error(f"生成聊天回复失败: {str(e)}")
            return {
                "final_response": "抱歉，我现在遇到了一些问题。不过我很乐意和你聊音乐！你可以告诉我你喜欢什么类型的音乐吗？",
                "step_count": state.get("step_count", 0) + 1,
                "error_log": state.get("error_log", []) + [
                    {"node": "general_chat", "error": str(e)}
                ]
            }
    
    async def generate_explanation(self, state: MusicAgentState) -> Dict[str, Any]:
        """
        节点3: 生成推荐解释
        为搜索结果或推荐结果生成友好的解释文本
        """
        logger.info("--- [步骤 3] 生成推荐解释 ---")
        
        recommendations = state.get("recommendations", [])
        user_query = state.get("input", "")
        
        if not recommendations:
            logger.warning("没有推荐结果，跳过解释生成")
            return {
                "explanation": "抱歉，没有找到合适的音乐推荐。",
                "final_response": "抱歉，没有找到符合你要求的音乐。你可以换个方式描述你的需求，或者告诉我你喜欢的歌手和风格？",
                "step_count": state.get("step_count", 0) + 1
            }
        
        try:
            # 格式化推荐结果
            songs_text = ""
            for i, rec in enumerate(recommendations, 1):
                song = rec.get("song", rec)  # 可能是搜索结果或推荐结果
                title = song.get("title", "未知")
                artist = song.get("artist", "未知")
                genre = song.get("genre", "未知")
                reason = rec.get("reason", "")
                
                songs_text += f"{i}. 《{title}》 - {artist} ({genre})\n"
                if reason:
                    songs_text += f"   推荐理由: {reason}\n"
            
            # 调用LLM生成解释
            prompt = MUSIC_RECOMMENDATION_EXPLAINER_PROMPT.format(
                user_query=user_query,
                recommended_songs=songs_text
            )
            response = await get_llm().ainvoke(prompt)
            
            explanation = response.content
            
            # 检查是否有播放列表
            playlist = state.get("playlist")
            playlist_text = ""
            if playlist:
                playlist_text = f"\n\n🎵 已为你创建 Spotify 播放列表：\n{playlist.get('url', '')}\n播放列表名称：{playlist.get('name', '')}"
            
            # 构建完整的最终回复
            final_response = f"{explanation}\n\n推荐歌曲：\n{songs_text}{playlist_text}"
            
            logger.info("成功生成推荐解释")
            
            return {
                "explanation": explanation,
                "final_response": final_response,
                "step_count": state.get("step_count", 0) + 1
            }
            
        except Exception as e:
            logger.error(f"生成解释失败: {str(e)}")
            
            # 生成简单的备用回复
            songs_list = "\n".join([
                f"{i}. 《{rec.get('song', rec).get('title', '未知')}》 - {rec.get('song', rec).get('artist', '未知')}"
                for i, rec in enumerate(recommendations, 1)
            ])
            
            return {
                "explanation": "为你找到了以下歌曲：",
                "final_response": f"为你找到了以下歌曲：\n\n{songs_list}",
                "step_count": state.get("step_count", 0) + 1,
                "error_log": state.get("error_log", []) + [
                    {"node": "generate_explanation", "error": str(e)}
                ]
            }
    
    async def analyze_user_preferences_node(self, state: MusicAgentState) -> Dict[str, Any]:
        """
        节点: 分析用户偏好 ⭐ NEW
        从 Spotify 获取用户数据并分析偏好
        """
        logger.info("--- [步骤] 分析用户偏好 ---")
        
        try:
            from tools.mcp_adapter import get_mcp_adapter
            from schemas.music_state import UserPreferences
            
            adapter = get_mcp_adapter()
            
            # 获取用户数据
            top_tracks = await adapter.get_user_top_tracks(limit=20)
            top_artists = await adapter.get_user_top_artists(limit=20)
            
            # 分析偏好（简单实现）
            favorite_artists = [artist.name for artist in top_artists[:10]]
            
            # 提取流派（从艺术家）
            genres = []
            for artist in top_artists:
                if artist.genres:
                    genres.extend(artist.genres)
            
            # 统计流派频率
            from collections import Counter
            genre_counter = Counter(genres)
            favorite_genres = [genre for genre, _ in genre_counter.most_common(5)]
            
            # 提取年代（从歌曲年份）
            decades = []
            for song in top_tracks:
                if song.year:
                    decade = (song.year // 10) * 10
                    decades.append(f"{decade}s")
            
            decade_counter = Counter(decades)
            favorite_decades = [decade for decade, _ in decade_counter.most_common(3)]
            
            preferences: UserPreferences = {
                "favorite_genres": favorite_genres,
                "favorite_artists": favorite_artists,
                "favorite_decades": favorite_decades,
                "avoid_genres": [],
                "mood_preferences": [],
                "activity_contexts": [],
                "language_preference": "mixed"
            }
            
            logger.info(f"分析完成: 偏好流派={favorite_genres}, 偏好艺术家={favorite_artists[:3]}")
            
            return {
                "user_preferences": preferences,
                "favorite_songs": [song.to_dict() for song in top_tracks[:10]],
                "step_count": state.get("step_count", 0) + 1
            }
            
        except Exception as e:
            logger.error(f"分析用户偏好失败: {str(e)}", exc_info=True)
            # 如果失败，返回空偏好，继续执行
            return {
                "user_preferences": {},
                "favorite_songs": [],
                "step_count": state.get("step_count", 0) + 1,
                "error_log": state.get("error_log", []) + [
                    {"node": "analyze_user_preferences", "error": str(e)}
                ]
            }
    
    async def enhanced_recommendations_node(self, state: MusicAgentState) -> Dict[str, Any]:
        """
        节点: 增强推荐 ⭐ NEW
        结合用户偏好生成推荐
        """
        logger.info("--- [步骤] 生成增强推荐 ---")
        
        try:
            from tools.mcp_adapter import get_mcp_adapter
            
            adapter = get_mcp_adapter()
            user_preferences = state.get("user_preferences", {})
            intent_type = state.get("intent_type", "")
            parameters = state.get("intent_parameters", {})
            
            recommendations = []
            
            # 根据意图类型生成推荐
            if intent_type.startswith("create_playlist"):
                # 创建歌单：结合用户偏好和意图参数
                activity = parameters.get("activity", "")
                mood = parameters.get("mood", "")
                
                # 使用用户 top tracks 作为种子
                favorite_songs = state.get("favorite_songs", [])
                seed_tracks = []
                if favorite_songs:
                    for song in favorite_songs[:5]:
                        if isinstance(song, dict) and song.get("spotify_id"):
                            seed_tracks.append(song["spotify_id"])
                
                # 使用用户偏好流派
                favorite_genres = user_preferences.get("favorite_genres", [])
                seed_genres = favorite_genres[:3] if favorite_genres else ["pop"]
                
                # 如果指定了活动或心情，调整流派
                if activity:
                    activity_genre_map = {
                        "运动": ["electronic", "rock"],
                        "健身": ["electronic", "rock"],
                        "学习": ["acoustic", "jazz"],
                        "工作": ["acoustic", "jazz"],
                    }
                    for key, genres in activity_genre_map.items():
                        if key in activity:
                            seed_genres = genres[:3]
                            break
                
                # 获取推荐
                songs = await adapter.get_recommendations(
                    seed_tracks=seed_tracks if seed_tracks else None,
                    seed_genres=seed_genres,
                    limit=30  # 创建歌单需要更多歌曲
                )
                
                # 转换为推荐格式
                for song in songs:
                    recommendations.append({
                        "song": song.to_dict(),
                        "reason": f"结合你的音乐偏好推荐",
                        "similarity_score": 0.9
                    })
            else:
                # 其他推荐类型，使用原有逻辑
                recommender = get_music_recommender()
                if intent_type == "recommend_by_mood":
                    mood = parameters.get("mood", "开心")
                    recs = await recommender.recommend_by_mood(mood, limit=5)
                    recommendations = [rec.to_dict() for rec in recs]
                elif intent_type == "recommend_by_activity":
                    activity = parameters.get("activity", "放松")
                    recs = await recommender.recommend_by_activity(activity, limit=5)
                    recommendations = [rec.to_dict() for rec in recs]
            
            logger.info(f"生成了 {len(recommendations)} 条增强推荐")
            
            return {
                "recommendations": recommendations,
                "step_count": state.get("step_count", 0) + 1
            }
            
        except Exception as e:
            logger.error(f"生成增强推荐失败: {str(e)}", exc_info=True)
            return {
                "recommendations": [],
                "step_count": state.get("step_count", 0) + 1,
                "error_log": state.get("error_log", []) + [
                    {"node": "enhanced_recommendations", "error": str(e)}
                ]
            }
    
    def route_after_preferences(self, state: MusicAgentState) -> str:
        """
        路由函数: 分析用户偏好后的路由
        """
        intent_type = state.get("intent_type", "")
        if intent_type.startswith("create_playlist"):
            return "enhanced_recommendations"
        else:
            return "generate_recommendations"
    
    async def create_playlist_node(self, state: MusicAgentState) -> Dict[str, Any]:
        """
        节点: 创建播放列表 ⭐ NEW
        """
        logger.info("--- [步骤] 创建播放列表 ---")
        
        try:
            from tools.mcp_adapter import get_mcp_adapter
            from tools.music_tools import Song
            
            adapter = get_mcp_adapter()
            
            # 获取推荐结果
            recommendations = state.get("recommendations", [])
            if not recommendations:
                logger.warning("没有推荐结果，无法创建播放列表")
                return {
                    "playlist": None,
                    "step_count": state.get("step_count", 0) + 1,
                    "error_log": state.get("error_log", []) + [
                        {"node": "create_playlist", "error": "没有推荐结果"}
                    ]
                }
            
            # 提取歌曲
            songs = []
            for rec in recommendations:
                song_data = rec.get("song", rec)
                if isinstance(song_data, dict):
                    # 从字典创建 Song 对象
                    song = Song(
                        title=song_data.get("title", "未知"),
                        artist=song_data.get("artist", "未知"),
                        album=song_data.get("album"),
                        genre=song_data.get("genre"),
                        year=song_data.get("year"),
                        duration=song_data.get("duration"),
                        popularity=song_data.get("popularity"),
                        preview_url=song_data.get("preview_url"),
                        spotify_id=song_data.get("spotify_id"),
                        external_url=song_data.get("external_url")
                    )
                    songs.append(song)
            
            if not songs:
                logger.warning("无法提取歌曲信息")
                return {
                    "playlist": None,
                    "step_count": state.get("step_count", 0) + 1
                }
            
            # 生成播放列表名称和描述
            intent_type = state.get("intent_type", "")
            parameters = state.get("intent_parameters", {})
            
            if "activity" in parameters:
                playlist_name = f"适合{parameters['activity']}的歌单"
                description = f"AI 为你推荐的适合{parameters['activity']}时听的音乐"
            elif "mood" in parameters:
                playlist_name = f"{parameters['mood']}心情歌单"
                description = f"AI 为你推荐的适合{parameters['mood']}心情的音乐"
            else:
                playlist_name = "AI 推荐歌单"
                description = "AI 为你推荐的个性化音乐歌单"
            
            # 创建播放列表
            playlist = await adapter.create_playlist(
                name=playlist_name,
                songs=songs,
                description=description,
                public=False
            )
            
            if playlist:
                logger.info(f"播放列表创建成功: {playlist.url}")
                return {
                    "playlist": playlist.to_dict(),
                    "step_count": state.get("step_count", 0) + 1
                }
            else:
                return {
                    "playlist": None,
                    "step_count": state.get("step_count", 0) + 1,
                    "error_log": state.get("error_log", []) + [
                        {"node": "create_playlist", "error": "创建播放列表失败"}
                    ]
                }
                
        except Exception as e:
            logger.error(f"创建播放列表失败: {str(e)}", exc_info=True)
            return {
                "playlist": None,
                "step_count": state.get("step_count", 0) + 1,
                "error_log": state.get("error_log", []) + [
                    {"node": "create_playlist", "error": str(e)}
                ]
            }
    
    def route_after_recommendations(self, state: MusicAgentState) -> str:
        """
        路由函数: 生成推荐后的路由
        """
        intent_type = state.get("intent_type", "")
        if intent_type.startswith("create_playlist"):
            return "create_playlist"
        else:
            return "generate_explanation"
    
    def _build_graph(self) -> CompiledStateGraph:
        """构建工作流图"""
        logger.info("开始构建音乐推荐工作流图...")
        
        workflow = StateGraph(MusicAgentState)
        
        # 添加节点
        workflow.add_node("analyze_intent", self.analyze_intent)
        workflow.add_node("search_songs", self.search_songs_node)
        workflow.add_node("generate_recommendations", self.generate_recommendations_node)
        workflow.add_node("analyze_user_preferences", self.analyze_user_preferences_node)  # ⭐ NEW
        workflow.add_node("enhanced_recommendations", self.enhanced_recommendations_node)  # ⭐ NEW
        workflow.add_node("create_playlist", self.create_playlist_node)  # ⭐ NEW
        workflow.add_node("general_chat", self.general_chat_node)
        workflow.add_node("generate_explanation", self.generate_explanation)
        
        # 设置入口点
        workflow.set_entry_point("analyze_intent")
        
        # 添加条件边：根据意图路由
        workflow.add_conditional_edges(
            "analyze_intent",
            self.route_by_intent,
            {
                "search_songs": "search_songs",
                "generate_recommendations": "generate_recommendations",
                "analyze_user_preferences": "analyze_user_preferences",  # ⭐ NEW
                "general_chat": "general_chat"
            }
        )
        
        # 用户偏好分析后的路由
        workflow.add_conditional_edges(
            "analyze_user_preferences",
            self.route_after_preferences,
            {
                "enhanced_recommendations": "enhanced_recommendations",
                "generate_recommendations": "generate_recommendations"
            }
        )
        
        # 增强推荐后的路由
        workflow.add_conditional_edges(
            "enhanced_recommendations",
            self.route_after_recommendations,
            {
                "create_playlist": "create_playlist",
                "generate_explanation": "generate_explanation"
            }
        )
        
        # 搜索和推荐后生成解释
        workflow.add_edge("search_songs", "generate_explanation")
        workflow.add_edge("generate_recommendations", "generate_explanation")
        
        # 创建播放列表后生成解释
        workflow.add_edge("create_playlist", "generate_explanation")
        
        # 聊天和解释后结束
        workflow.add_edge("general_chat", END)
        workflow.add_edge("generate_explanation", END)
        
        # 编译图
        app = workflow.compile()
        logger.info("音乐推荐工作流图构建完成")
        
        return app

