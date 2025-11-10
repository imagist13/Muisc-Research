"""
音乐推荐工具集
提供音乐搜索、歌曲信息获取、相似歌曲推荐等功能
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Song:
    """歌曲数据类"""
    title: str  # 歌曲名
    artist: str  # 艺术家
    album: Optional[str] = None  # 专辑
    genre: Optional[str] = None  # 流派
    year: Optional[int] = None  # 发行年份
    duration: Optional[int] = None  # 时长（秒）
    popularity: Optional[int] = None  # 流行度（0-100）
    preview_url: Optional[str] = None  # 试听链接
    spotify_id: Optional[str] = None  # Spotify ID
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class MusicRecommendation:
    """音乐推荐结果"""
    song: Song
    reason: str  # 推荐理由
    similarity_score: float  # 相似度分数（0-1）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "song": self.song.to_dict(),
            "reason": self.reason,
            "similarity_score": self.similarity_score
        }


class MusicSearchTool:
    """音乐搜索工具"""
    
    def __init__(self):
        self.session = None
        # 模拟音乐数据库（实际项目中应该对接真实的音乐API，如Spotify、网易云等）
        self.music_db = self._initialize_music_db()
        # 加载 tailyapi 配置
        self.tailyapi_config = self._load_tailyapi_config()
    
    def _load_tailyapi_config(self) -> Dict[str, str]:
        """加载 tailyapi 配置"""
        try:
            from config.settings_loader import load_settings_from_json
            settings = load_settings_from_json()
            api_key = settings.get("TAILYAPI_API_KEY") or os.getenv("TAILYAPI_API_KEY", "")
            base_url = settings.get("TAILYAPI_BASE_URL") or os.getenv("TAILYAPI_BASE_URL", "https://api.tavily.com")
            
            return {
                "api_key": api_key,
                "base_url": base_url
            }
        except Exception as e:
            logger.warning(f"加载 tailyapi 配置失败: {str(e)}")
            return {"api_key": "", "base_url": "https://api.tavily.com"}
    
    def _initialize_music_db(self) -> List[Song]:
        """从JSON文件初始化音乐数据库"""
        try:
            # 获取项目根目录
            current_dir = Path(__file__).parent
            project_root = current_dir.parent
            json_path = project_root / "data" / "music_database.json"
            
            # 如果文件不存在，尝试其他路径
            if not json_path.exists():
                # 尝试相对路径
                json_path = Path("data/music_database.json")
                if not json_path.exists():
                    json_path = Path("../data/music_database.json")
            
            if not json_path.exists():
                logger.warning(f"音乐数据库JSON文件未找到: {json_path}，使用空数据库")
                return []
            
            # 读取JSON文件
            with open(json_path, 'r', encoding='utf-8') as f:
                music_data = json.load(f)
            
            # 转换为Song对象
            songs = []
            for item in music_data:
                song = Song(
                    title=item.get("title", ""),
                    artist=item.get("artist", ""),
                    album=item.get("album"),
                    genre=item.get("genre"),
                    year=item.get("year"),
                    duration=item.get("duration"),
                    popularity=item.get("popularity")
                )
                songs.append(song)
            
            logger.info(f"成功从JSON文件加载 {len(songs)} 首歌曲")
            return songs
            
        except Exception as e:
            logger.error(f"加载音乐数据库失败: {str(e)}", exc_info=True)
            return []
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _search_songs_with_tailyapi(
        self,
        query: str,
        limit: int = 10
    ) -> List[Song]:
        """
        使用 tailyapi (Tavily API) 从网上搜索歌曲
        
        Args:
            query: 搜索关键词（歌曲名或艺术家）
            limit: 返回结果数量
            
        Returns:
            歌曲列表
        """
        try:
            api_key = self.tailyapi_config.get("api_key", "")
            base_url = self.tailyapi_config.get("base_url", "https://api.tavily.com")
            
            if not api_key:
                logger.warning("TailyAPI API Key 未配置，跳过在线搜索")
                return []
            
            # 构建搜索查询，添加音乐相关关键词
            search_query = f"{query} 歌曲 音乐 song music"
            
            session = await self._get_session()
            url = f"{base_url}/search"
            
            payload = {
                "api_key": api_key,
                "query": search_query,
                "search_depth": "advanced",
                "include_answer": True,
                "include_raw_content": False,
                "max_results": limit * 2,  # 获取更多结果以便筛选
                "include_domains": [],
                "exclude_domains": []
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            logger.info(f"使用 TailyAPI 搜索歌曲: query='{query}'")
            
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"TailyAPI 请求失败: {response.status} - {error_text}")
                    return []
                
                data = await response.json()
                
                # 解析搜索结果
                songs = []
                results = data.get("results", [])
                
                for result in results[:limit * 2]:
                    title = result.get("title", "")
                    content = result.get("content", "")
                    url_link = result.get("url", "")
                    
                    # 尝试从标题和内容中提取歌曲信息
                    # 这里使用简单的正则或字符串匹配来提取歌曲名和艺术家
                    song_info = self._extract_song_info_from_text(title + " " + content, query)
                    
                    if song_info:
                        song = Song(
                            title=song_info.get("title", query),
                            artist=song_info.get("artist", "未知"),
                            album=song_info.get("album"),
                            genre=song_info.get("genre"),
                            preview_url=url_link,
                            popularity=song_info.get("popularity", 50)
                        )
                        songs.append(song)
                
                # 去重（基于标题和艺术家）
                unique_songs = []
                seen = set()
                for song in songs:
                    key = (song.title.lower(), song.artist.lower())
                    if key not in seen:
                        seen.add(key)
                        unique_songs.append(song)
                
                logger.info(f"TailyAPI 搜索到 {len(unique_songs)} 首歌曲")
                return unique_songs[:limit]
                
        except Exception as e:
            logger.error(f"使用 TailyAPI 搜索歌曲失败: {str(e)}", exc_info=True)
            return []
    
    def _extract_song_info_from_text(self, text: str, query: str) -> Optional[Dict[str, Any]]:
        """
        从文本中提取歌曲信息
        
        Args:
            text: 包含歌曲信息的文本
            query: 原始搜索查询
            
        Returns:
            歌曲信息字典
        """
        import re
        
        try:
            # 尝试匹配常见的歌曲信息格式
            # 例如: "歌曲名 - 艺术家" 或 "艺术家 - 歌曲名"
            patterns = [
                r'(.+?)\s*[-–—]\s*(.+)',  # "歌曲 - 艺术家" 或 "艺术家 - 歌曲"
                r'(.+?)\s*《(.+?)》',  # "艺术家《歌曲》"
                r'《(.+?)》\s*(.+)',  # "《歌曲》艺术家"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    groups = match.groups()
                    if len(groups) >= 2:
                        # 判断哪个是歌曲名，哪个是艺术家
                        # 通常查询词更可能是歌曲名
                        title = groups[0].strip()
                        artist = groups[1].strip()
                        
                        # 如果查询词在第一个位置，可能是 "歌曲 - 艺术家"
                        if query.lower() in title.lower():
                            return {
                                "title": title,
                                "artist": artist,
                                "popularity": 60
                            }
                        # 否则可能是 "艺术家 - 歌曲"
                        elif query.lower() in artist.lower():
                            return {
                                "title": artist,
                                "artist": title,
                                "popularity": 60
                            }
            
            # 如果无法解析，使用查询词作为歌曲名
            return {
                "title": query,
                "artist": "未知",
                "popularity": 50
            }
            
        except Exception as e:
            logger.warning(f"提取歌曲信息失败: {str(e)}")
            return None
    
    async def search_songs(
        self, 
        query: str, 
        genre: Optional[str] = None,
        limit: int = 10
    ) -> List[Song]:
        """
        搜索歌曲（优先使用 tailyapi，失败则回退到本地数据库）
        
        Args:
            query: 搜索关键词（歌曲名或艺术家）
            genre: 音乐流派过滤
            limit: 返回结果数量
            
        Returns:
            歌曲列表
        """
        try:
            logger.info(f"搜索音乐: query='{query}', genre='{genre}', limit={limit}")
            
            # 优先使用 tailyapi 在线搜索
            online_results = await self._search_songs_with_tailyapi(query, limit=limit * 2)
            
            if online_results:
                # 如果指定了流派，进行过滤
                if genre:
                    filtered = [
                        song for song in online_results
                        if song.genre and genre.lower() in song.genre.lower()
                    ]
                    if filtered:
                        return filtered[:limit]
                
                logger.info(f"从 TailyAPI 找到 {len(online_results)} 首歌曲")
                return online_results[:limit]
            
            # 如果在线搜索失败，回退到本地数据库
            logger.info("TailyAPI 搜索无结果，使用本地数据库搜索")
            results = []
            query_lower = query.lower()
            
            for song in self.music_db:
                # 检查是否匹配搜索词
                if (query_lower in song.title.lower() or 
                    query_lower in song.artist.lower() or
                    (song.album and query_lower in song.album.lower())):
                    
                    # 如果指定了流派，进行过滤
                    if genre is None or (song.genre and genre.lower() in song.genre.lower()):
                        results.append(song)
            
            # 按流行度排序
            results.sort(key=lambda x: x.popularity or 0, reverse=True)
            
            logger.info(f"从本地数据库找到 {len(results)} 首歌曲")
            return results[:limit]
            
        except Exception as e:
            logger.error(f"搜索歌曲失败: {str(e)}")
            return []
    
    async def get_songs_by_genre(self, genre: str, limit: int = 10) -> List[Song]:
        """
        根据流派获取歌曲
        
        Args:
            genre: 音乐流派
            limit: 返回结果数量
            
        Returns:
            歌曲列表
        """
        try:
            logger.info(f"按流派获取歌曲: genre='{genre}'")
            
            results = [
                song for song in self.music_db 
                if song.genre and genre.lower() in song.genre.lower()
            ]
            
            # 按流行度排序
            results.sort(key=lambda x: x.popularity or 0, reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"按流派获取歌曲失败: {str(e)}")
            return []
    
    async def get_songs_by_artist(self, artist: str, limit: int = 10) -> List[Song]:
        """
        根据艺术家获取歌曲
        
        Args:
            artist: 艺术家名称
            limit: 返回结果数量
            
        Returns:
            歌曲列表
        """
        try:
            logger.info(f"按艺术家获取歌曲: artist='{artist}'")
            
            results = [
                song for song in self.music_db 
                if artist.lower() in song.artist.lower()
            ]
            
            # 按年份排序（最新的在前）
            results.sort(key=lambda x: x.year or 0, reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"按艺术家获取歌曲失败: {str(e)}")
            return []
    
    async def get_similar_songs(self, song_title: str, artist: str, limit: int = 5) -> List[Song]:
        """
        获取相似歌曲（基于流派和艺术家）
        
        Args:
            song_title: 歌曲名
            artist: 艺术家
            limit: 返回结果数量
            
        Returns:
            相似歌曲列表
        """
        try:
            logger.info(f"获取相似歌曲: song='{song_title}', artist='{artist}'")
            
            # 找到原始歌曲
            original_song = None
            for song in self.music_db:
                if song.title.lower() == song_title.lower() and song.artist.lower() == artist.lower():
                    original_song = song
                    break
            
            if not original_song:
                logger.warning(f"未找到原始歌曲: {song_title} - {artist}")
                return []
            
            # 查找相似歌曲
            similar_songs = []
            for song in self.music_db:
                if song.title == original_song.title and song.artist == original_song.artist:
                    continue  # 跳过自己
                
                # 计算相似度分数
                score = 0
                if song.genre == original_song.genre:
                    score += 50  # 流派相同
                if song.artist == original_song.artist:
                    score += 40  # 艺术家相同
                elif song.genre and original_song.genre and song.genre == original_song.genre:
                    score += 20  # 流派相同但艺术家不同
                
                # 年代相近加分
                if song.year and original_song.year:
                    year_diff = abs(song.year - original_song.year)
                    if year_diff <= 3:
                        score += 10
                
                if score > 0:
                    similar_songs.append((song, score))
            
            # 按分数排序
            similar_songs.sort(key=lambda x: x[1], reverse=True)
            
            # 只返回歌曲对象
            results = [song for song, score in similar_songs[:limit]]
            logger.info(f"找到 {len(results)} 首相似歌曲")
            
            return results
            
        except Exception as e:
            logger.error(f"获取相似歌曲失败: {str(e)}")
            return []
    
    async def get_popular_songs(self, limit: int = 10) -> List[Song]:
        """
        获取热门歌曲
        
        Args:
            limit: 返回结果数量
            
        Returns:
            热门歌曲列表
        """
        try:
            logger.info(f"获取热门歌曲")
            
            # 按流行度排序
            popular = sorted(
                self.music_db, 
                key=lambda x: x.popularity or 0, 
                reverse=True
            )
            
            return popular[:limit]
            
        except Exception as e:
            logger.error(f"获取热门歌曲失败: {str(e)}")
            return []
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()


class MusicRecommenderEngine:
    """音乐推荐引擎"""
    
    def __init__(self, search_tool: MusicSearchTool):
        self.search_tool = search_tool
    
    async def recommend_by_mood(
        self, 
        mood: str, 
        limit: int = 5
    ) -> List[MusicRecommendation]:
        """
        根据心情推荐音乐
        
        Args:
            mood: 心情描述（如：开心、悲伤、放松、激动等）
            limit: 推荐数量
            
        Returns:
            音乐推荐列表
        """
        try:
            logger.info(f"根据心情推荐音乐: mood='{mood}'")
            
            # 心情到流派的映射
            mood_genre_map = {
                "开心": ["流行", "电子"],
                "快乐": ["流行", "电子"],
                "悲伤": ["抒情", "民谣"],
                "伤心": ["抒情", "民谣"],
                "放松": ["民谣", "爵士"],
                "舒缓": ["民谣", "爵士"],
                "激动": ["摇滚", "电子"],
                "兴奋": ["摇滚", "电子"],
                "怀旧": ["经典", "流行"],
                "平静": ["古风", "民谣"],
                "浪漫": ["抒情", "流行"],
            }
            
            # 匹配流派
            genres = []
            for key, value in mood_genre_map.items():
                if key in mood.lower() or mood.lower() in key:
                    genres.extend(value)
            
            if not genres:
                genres = ["流行"]  # 默认流派
            
            # 获取对应流派的歌曲
            all_songs = []
            for genre in genres:
                songs = await self.search_tool.get_songs_by_genre(genre, limit=10)
                all_songs.extend(songs)
            
            # 去重并限制数量
            unique_songs = list({song.title: song for song in all_songs}.values())
            
            # 生成推荐
            recommendations = []
            for song in unique_songs[:limit]:
                reason = f"这首{song.genre}歌曲很适合你现在的{mood}心情"
                recommendations.append(MusicRecommendation(
                    song=song,
                    reason=reason,
                    similarity_score=0.85
                ))
            
            logger.info(f"生成了 {len(recommendations)} 条推荐")
            return recommendations
            
        except Exception as e:
            logger.error(f"根据心情推荐失败: {str(e)}")
            return []
    
    async def recommend_by_favorites(
        self, 
        favorite_songs: List[Dict[str, str]], 
        limit: int = 5
    ) -> List[MusicRecommendation]:
        """
        根据喜欢的歌曲推荐
        
        Args:
            favorite_songs: 喜欢的歌曲列表 [{"title": "歌名", "artist": "歌手"}, ...]
            limit: 推荐数量
            
        Returns:
            音乐推荐列表
        """
        try:
            logger.info(f"根据喜欢的歌曲推荐: {len(favorite_songs)} 首歌")
            
            all_similar = []
            for fav in favorite_songs:
                similar = await self.search_tool.get_similar_songs(
                    fav.get("title", ""),
                    fav.get("artist", ""),
                    limit=3
                )
                all_similar.extend(similar)
            
            # 去重
            unique_songs = list({song.title: song for song in all_similar}.values())
            
            # 生成推荐
            recommendations = []
            for song in unique_songs[:limit]:
                reason = f"因为你喜欢类似风格的歌曲，这首{song.artist}的作品可能也会打动你"
                recommendations.append(MusicRecommendation(
                    song=song,
                    reason=reason,
                    similarity_score=0.9
                ))
            
            logger.info(f"生成了 {len(recommendations)} 条推荐")
            return recommendations
            
        except Exception as e:
            logger.error(f"根据喜欢的歌曲推荐失败: {str(e)}")
            return []
    
    async def recommend_by_activity(
        self, 
        activity: str, 
        limit: int = 5
    ) -> List[MusicRecommendation]:
        """
        根据活动场景推荐音乐
        
        Args:
            activity: 活动描述（如：运动、学习、开车、睡觉等）
            limit: 推荐数量
            
        Returns:
            音乐推荐列表
        """
        try:
            logger.info(f"根据活动场景推荐: activity='{activity}'")
            
            # 活动到流派的映射
            activity_genre_map = {
                "运动": ["电子", "摇滚"],
                "健身": ["电子", "摇滚"],
                "学习": ["古风", "爵士", "民谣"],
                "工作": ["古风", "爵士"],
                "开车": ["流行", "摇滚"],
                "睡觉": ["民谣", "古风"],
                "休息": ["民谣", "抒情"],
                "派对": ["电子", "流行"],
                "聚会": ["流行", "电子"],
            }
            
            # 匹配流派
            genres = []
            for key, value in activity_genre_map.items():
                if key in activity.lower() or activity.lower() in key:
                    genres.extend(value)
            
            if not genres:
                genres = ["流行"]
            
            # 获取对应流派的歌曲
            all_songs = []
            for genre in genres:
                songs = await self.search_tool.get_songs_by_genre(genre, limit=10)
                all_songs.extend(songs)
            
            # 去重并限制数量
            unique_songs = list({song.title: song for song in all_songs}.values())
            
            # 生成推荐
            recommendations = []
            for song in unique_songs[:limit]:
                reason = f"这首歌很适合{activity}时听，节奏和氛围都很搭"
                recommendations.append(MusicRecommendation(
                    song=song,
                    reason=reason,
                    similarity_score=0.88
                ))
            
            logger.info(f"生成了 {len(recommendations)} 条推荐")
            return recommendations
            
        except Exception as e:
            logger.error(f"根据活动场景推荐失败: {str(e)}")
            return []


# 创建全局实例
music_search_tool = MusicSearchTool()
music_recommender = MusicRecommenderEngine(music_search_tool)

