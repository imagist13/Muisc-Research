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
from tools.music_tools import music_search_tool, music_recommender
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
            results = await music_search_tool.search_songs(
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
            recommendations = []
            
            if intent_type == "recommend_by_mood":
                mood = parameters.get("mood", "开心")
                recs = await music_recommender.recommend_by_mood(mood, limit=5)
                recommendations = [rec.to_dict() for rec in recs]
                
            elif intent_type == "recommend_by_activity":
                activity = parameters.get("activity", "放松")
                recs = await music_recommender.recommend_by_activity(activity, limit=5)
                recommendations = [rec.to_dict() for rec in recs]
                
            elif intent_type == "recommend_by_genre":
                genre = parameters.get("genre", "流行")
                songs = await music_search_tool.get_songs_by_genre(genre, limit=5)
                # 转换为推荐格式
                recommendations = [{
                    "song": song.to_dict(),
                    "reason": f"这是一首优秀的{genre}作品",
                    "similarity_score": 0.85
                } for song in songs]
                
            elif intent_type == "recommend_by_artist":
                artist = parameters.get("artist", "")
                songs = await music_search_tool.get_songs_by_artist(artist, limit=5)
                recommendations = [{
                    "song": song.to_dict(),
                    "reason": f"{artist}的经典作品",
                    "similarity_score": 0.9
                } for song in songs]
                
            elif intent_type == "recommend_by_favorites":
                favorite_songs = parameters.get("favorite_songs", [])
                if favorite_songs:
                    recs = await music_recommender.recommend_by_favorites(favorite_songs, limit=5)
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
            
            # 构建完整的最终回复
            final_response = f"{explanation}\n\n推荐歌曲：\n{songs_text}"
            
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
    
    def _build_graph(self) -> CompiledStateGraph:
        """构建工作流图"""
        logger.info("开始构建音乐推荐工作流图...")
        
        workflow = StateGraph(MusicAgentState)
        
        # 添加节点
        workflow.add_node("analyze_intent", self.analyze_intent)
        workflow.add_node("search_songs", self.search_songs_node)
        workflow.add_node("generate_recommendations", self.generate_recommendations_node)
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
                "general_chat": "general_chat"
            }
        )
        
        # 搜索和推荐后生成解释
        workflow.add_edge("search_songs", "generate_explanation")
        workflow.add_edge("generate_recommendations", "generate_explanation")
        
        # 聊天和解释后结束
        workflow.add_edge("general_chat", END)
        workflow.add_edge("generate_explanation", END)
        
        # 编译图
        app = workflow.compile()
        logger.info("音乐推荐工作流图构建完成")
        
        return app

