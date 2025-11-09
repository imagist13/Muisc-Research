"""
音乐推荐Agent的状态定义
"""

from typing import TypedDict, List, Dict, Any, Optional


class MusicAgentState(TypedDict, total=False):
    """音乐推荐Agent的状态"""
    
    # 用户输入
    input: str  # 用户查询/请求
    chat_history: List[Dict[str, str]]  # 对话历史
    
    # 意图分析结果
    intent_type: str  # 意图类型
    intent_parameters: Dict[str, Any]  # 意图参数
    intent_context: str  # 意图上下文
    
    # 搜索和推荐结果
    search_results: List[Dict[str, Any]]  # 搜索到的歌曲
    recommendations: List[Dict[str, Any]]  # 推荐结果
    
    # 用户偏好数据
    user_preferences: Dict[str, Any]  # 用户偏好
    favorite_songs: List[Dict[str, str]]  # 用户喜欢的歌曲
    
    # 生成的内容
    explanation: str  # 推荐解释
    final_response: str  # 最终回复
    playlist: Optional[Dict[str, Any]]  # 生成的播放列表
    
    # 执行状态
    step_count: int  # 执行步数
    error_log: List[Dict[str, Any]]  # 错误日志
    
    # 额外信息
    metadata: Dict[str, Any]  # 元数据


class UserPreferences(TypedDict, total=False):
    """用户音乐偏好"""
    
    favorite_genres: List[str]  # 喜欢的流派
    favorite_artists: List[str]  # 喜欢的艺术家
    favorite_decades: List[str]  # 喜欢的年代
    avoid_genres: List[str]  # 不喜欢的流派
    mood_preferences: List[str]  # 心情偏好
    activity_contexts: List[str]  # 活动场景偏好
    language_preference: str  # 语言偏好（中文/英文等）


class PlaylistInfo(TypedDict, total=False):
    """播放列表信息"""
    
    playlist_name: str  # 播放列表名称
    description: str  # 描述
    songs: List[Dict[str, Any]]  # 歌曲列表
    total_duration: int  # 总时长（秒）
    mood_progression: str  # 情绪变化描述
    created_at: str  # 创建时间
    theme: str  # 主题

