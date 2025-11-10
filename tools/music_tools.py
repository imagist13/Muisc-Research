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

# 在导入其他模块之前加载配置
try:
    from config.settings_loader import load_and_setup_settings
    load_and_setup_settings()
except Exception as e:
    print(f"警告: 无法从 setting.json 加载配置: {e}")

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
    """音乐搜索工具 - 使用 MCP 适配器"""
    
    def __init__(self, mcp_adapter=None):
        """
        初始化音乐搜索工具
        
        Args:
            mcp_adapter: MCP 客户端适配器，如果为 None 则自动创建
        """
        self.session = None
        # 使用 MCP 适配器
        if mcp_adapter is None:
            from tools.mcp_adapter import get_mcp_adapter
            mcp_adapter = get_mcp_adapter()
        self.mcp_adapter = mcp_adapter
        
        # 保留本地数据库作为后备（可选）
        self.music_db = self._initialize_music_db()
        # 加载 tailyapi 配置（作为后备）
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
        搜索歌曲（使用 Spotify API via MCP）
        
        Args:
            query: 搜索关键词（歌曲名或艺术家）
            genre: 音乐流派过滤（注意：Spotify 搜索不支持流派过滤，会在结果中过滤）
            limit: 返回结果数量
            
        Returns:
            歌曲列表
        """
        try:
            logger.info(f"搜索音乐: query='{query}', genre='{genre}', limit={limit}")
            
            # 使用 Spotify API 搜索（通过 MCP）
            spotify_results = await self.mcp_adapter.search_tracks(query, limit=limit * 2)
            
            if spotify_results:
                # 如果指定了流派，进行过滤（注意：Spotify 不直接提供流派，这里先不过滤，返回所有结果）
                # 未来可以通过艺术家信息获取流派
                logger.info(f"从 Spotify 找到 {len(spotify_results)} 首歌曲")
                return spotify_results[:limit]
            else:
                logger.warning(f"Spotify 搜索未返回结果，请检查 MCP 配置")
                return []
            
        except Exception as e:
            logger.error(f"搜索歌曲失败: {str(e)}", exc_info=True)
            raise  # 抛出异常，不使用本地数据库
    
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
    """音乐推荐引擎 - 增强版，支持 Spotify 推荐"""
    
    def __init__(self, search_tool: MusicSearchTool, mcp_adapter=None):
        """
        初始化推荐引擎
        
        Args:
            search_tool: 音乐搜索工具
            mcp_adapter: MCP 客户端适配器，如果为 None 则从 search_tool 获取
        """
        self.search_tool = search_tool
        if mcp_adapter is None:
            mcp_adapter = search_tool.mcp_adapter
        self.mcp_adapter = mcp_adapter
    
    async def recommend_by_mood(
        self, 
        mood: str, 
        limit: int = 5
    ) -> List[MusicRecommendation]:
        """
        根据心情推荐音乐（使用 Spotify 推荐 API）
        
        Args:
            mood: 心情描述（如：开心、悲伤、放松、激动等）
            limit: 推荐数量
            
        Returns:
            音乐推荐列表
        """
        try:
            logger.info(f"根据心情推荐音乐: mood='{mood}'")
            
            # 心情到 Spotify 流派的映射（扩充中文同义词）
            mood_genre_map = {
                "开心": ["pop", "dance", "electronic"],
                "快乐": ["pop", "dance", "electronic"],
                "高兴": ["pop", "dance", "electronic"],
                "兴奋": ["rock", "electronic", "dance"],
                "激动": ["rock", "electronic", "dance"],
                "悲伤": ["acoustic", "sad", "indie", "mellow"],
                "伤心": ["acoustic", "sad", "indie", "mellow"],
                "难过": ["acoustic", "sad", "indie", "piano"],
                "丧": ["acoustic", "sad", "indie"],
                "疗愈": ["acoustic", "mellow", "indie"],
                "放松": ["chill", "acoustic", "jazz", "ambient"],
                "舒缓": ["chill", "acoustic", "jazz", "ambient"],
                "平静": ["ambient", "acoustic", "chill"],
                "安静": ["ambient", "acoustic", "chill"],
                "怀旧": ["classic", "pop", "rock", "indie"],
                "浪漫": ["acoustic", "pop", "r-n-b", "soul"],
                "甜蜜": ["pop", "r-n-b", "soul"],
                "表白": ["r-n-b", "soul", "pop"],
                "学习": ["lo-fi", "chill", "ambient", "acoustic"],
                "专注": ["lo-fi", "ambient", "acoustic"],
                "运动": ["electronic", "rock", "dance"],
            }

            # 心情到音频特征目标（0-1范围，tempo单位 BPM）
            mood_target_features = {
                "开心": {"valence": 0.7, "energy": 0.7, "danceability": 0.6, "tempo": 120},
                "快乐": {"valence": 0.7, "energy": 0.7, "danceability": 0.6, "tempo": 120},
                "高兴": {"valence": 0.7, "energy": 0.7, "danceability": 0.6, "tempo": 120},
                "兴奋": {"valence": 0.6, "energy": 0.85, "danceability": 0.7, "tempo": 130},
                "激动": {"valence": 0.6, "energy": 0.85, "danceability": 0.7, "tempo": 130},
                "悲伤": {"valence": 0.25, "energy": 0.3, "danceability": 0.3, "tempo": 80},
                "伤心": {"valence": 0.25, "energy": 0.3, "danceability": 0.3, "tempo": 80},
                "难过": {"valence": 0.2, "energy": 0.25, "danceability": 0.3, "tempo": 75},
                "丧": {"valence": 0.2, "energy": 0.25, "danceability": 0.3, "tempo": 75},
                "疗愈": {"valence": 0.4, "energy": 0.3, "danceability": 0.35, "tempo": 85},
                "放松": {"valence": 0.5, "energy": 0.35, "danceability": 0.4, "tempo": 90},
                "舒缓": {"valence": 0.5, "energy": 0.35, "danceability": 0.4, "tempo": 90},
                "平静": {"valence": 0.45, "energy": 0.25, "danceability": 0.35, "tempo": 80},
                "安静": {"valence": 0.45, "energy": 0.25, "danceability": 0.35, "tempo": 80},
                "怀旧": {"valence": 0.5, "energy": 0.45, "danceability": 0.45, "tempo": 100},
                "浪漫": {"valence": 0.65, "energy": 0.45, "danceability": 0.5, "tempo": 95},
                "甜蜜": {"valence": 0.7, "energy": 0.5, "danceability": 0.55, "tempo": 100},
                "表白": {"valence": 0.65, "energy": 0.45, "danceability": 0.5, "tempo": 95},
                "学习": {"valence": 0.45, "energy": 0.3, "danceability": 0.35, "tempo": 85},
                "专注": {"valence": 0.4, "energy": 0.25, "danceability": 0.3, "tempo": 80},
                "运动": {"valence": 0.6, "energy": 0.85, "danceability": 0.75, "tempo": 130},
            }
            
            # 匹配流派
            spotify_genres = []
            for key, value in mood_genre_map.items():
                if key in mood or mood in key:
                    spotify_genres.extend(value)
            
            if not spotify_genres:
                spotify_genres = ["pop"]  # 默认流派
            
            # 使用 Spotify 推荐 API
            songs = await self.mcp_adapter.get_recommendations(
                seed_genres=spotify_genres[:5],
                limit=limit
            )
            
            if not songs:
                logger.warning(f"Spotify 推荐未返回结果，请检查 MCP 配置")
                return []
            
            # 获取音频特征并基于心情做重排
            try:
                target = None
                for k, v in mood_target_features.items():
                    if k in mood or mood in k:
                        target = v
                        break
                features_by_id = {}
                if target:
                    track_ids = [s.spotify_id for s in songs if s.spotify_id]
                    features_by_id = await self.mcp_adapter.get_audio_features(track_ids)

                    def _score(song: Song) -> float:
                        feat = features_by_id.get(song.spotify_id or "", {})
                        if not feat:
                            # 回退使用流行度
                            return 0.3 + (song.popularity or 0) / 200.0
                        # 计算与目标的距离分数（越小越好，这里转为分数越大越好）
                        w = {"valence": 0.4, "energy": 0.3, "danceability": 0.2, "tempo": 0.1}
                        score = 0.0
                        for kf, weight in w.items():
                            if kf == "tempo":
                                v = feat.get(kf)
                                if v is None:
                                    continue
                                diff = abs(v - target.get(kf, v)) / 60.0  # 60 BPM 归一
                            else:
                                v = feat.get(kf)
                                if v is None:
                                    continue
                                diff = abs(v - target.get(kf, v))
                            score += weight * max(0.0, 1.0 - diff)
                        # 结合流行度做轻微加权
                        score += 0.1 * ((song.popularity or 0) / 100.0)
                        return score

                    songs = sorted(songs, key=_score, reverse=True)
            except Exception as e:
                logger.debug(f"按音频特征重排失败: {e}")

            # 艺人多样性：避免同一艺人重复
            unique_by_artist = []
            seen_artists = set()
            for s in songs:
                artist_key = (s.artist or "").lower()
                if artist_key and artist_key in seen_artists:
                    continue
                seen_artists.add(artist_key)
                unique_by_artist.append(s)
                if len(unique_by_artist) >= limit:
                    break
            final_songs = unique_by_artist or songs[:limit]

            recommendations = []
            for song in final_songs:
                reason = f"这首歌曲很适合你现在的{mood}心情"
                recommendations.append(MusicRecommendation(
                    song=song,
                    reason=reason,
                    similarity_score=0.9
                ))
            
            logger.info(f"使用 Spotify 推荐生成了 {len(recommendations)} 条推荐")
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
        根据喜欢的歌曲推荐（使用 Spotify 推荐 API）
        
        Args:
            favorite_songs: 喜欢的歌曲列表 [{"title": "歌名", "artist": "歌手"}, ...]
            limit: 推荐数量
            
        Returns:
            音乐推荐列表
        """
        try:
            logger.info(f"根据喜欢的歌曲推荐: {len(favorite_songs)} 首歌")
            
            # 使用 Spotify 推荐 API
            # 将喜欢的歌曲转换为 Spotify 推荐格式
            seed_tracks = [
                {"song_name": fav.get("title", ""), "artist_name": fav.get("artist", "")}
                for fav in favorite_songs[:5]  # Spotify 最多支持5个种子
            ]
            
            songs = await self.mcp_adapter.get_recommendations_by_names(
                seed_track_names=seed_tracks,
                limit=limit
            )
            
            if not songs:
                logger.warning(f"Spotify 推荐未返回结果，请检查 MCP 配置")
                return []
            
            recommendations = []
            for song in songs:
                reason = f"因为你喜欢类似风格的歌曲，这首{song.artist}的作品可能也会打动你"
                recommendations.append(MusicRecommendation(
                    song=song,
                    reason=reason,
                    similarity_score=0.9
                ))
            
            logger.info(f"使用 Spotify 推荐生成了 {len(recommendations)} 条推荐")
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
        根据活动场景推荐音乐（使用 Spotify 推荐 API）
        
        Args:
            activity: 活动描述（如：运动、学习、开车、睡觉等）
            limit: 推荐数量
            
        Returns:
            音乐推荐列表
        """
        try:
            logger.info(f"根据活动场景推荐: activity='{activity}'")
            
            # 活动到 Spotify 流派的映射
            activity_genre_map = {
                "运动": ["electronic", "rock", "dance"],
                "健身": ["electronic", "rock", "dance"],
                "学习": ["acoustic", "jazz", "chill"],
                "工作": ["acoustic", "jazz", "chill"],
                "开车": ["pop", "rock", "country"],
                "睡觉": ["ambient", "acoustic", "chill"],
                "休息": ["acoustic", "chill", "jazz"],
                "派对": ["dance", "pop", "electronic"],
                "聚会": ["pop", "dance", "electronic"],
            }
            
            # 匹配流派
            spotify_genres = []
            for key, value in activity_genre_map.items():
                if key in activity.lower() or activity.lower() in key:
                    spotify_genres.extend(value)
            
            if not spotify_genres:
                spotify_genres = ["pop"]
            
            # 使用 Spotify 推荐 API
            songs = await self.mcp_adapter.get_recommendations(
                seed_genres=spotify_genres[:5],
                limit=limit
            )
            
            if not songs:
                logger.warning(f"Spotify 推荐未返回结果，请检查 MCP 配置")
                return []
            
            recommendations = []
            for song in songs:
                reason = f"这首歌很适合{activity}时听，节奏和氛围都很搭"
                recommendations.append(MusicRecommendation(
                    song=song,
                    reason=reason,
                    similarity_score=0.88
                ))
            
            logger.info(f"使用 Spotify 推荐生成了 {len(recommendations)} 条推荐")
            return recommendations
            
        except Exception as e:
            logger.error(f"根据活动场景推荐失败: {str(e)}")
            return []


# 创建全局实例（延迟初始化，避免在导入时连接 Spotify）
_music_search_tool = None
_music_recommender = None

def get_music_search_tool() -> MusicSearchTool:
    """获取音乐搜索工具单例"""
    global _music_search_tool
    if _music_search_tool is None:
        _music_search_tool = MusicSearchTool()
    return _music_search_tool

def get_music_recommender() -> MusicRecommenderEngine:
    """获取音乐推荐引擎单例"""
    global _music_recommender
    if _music_recommender is None:
        _music_recommender = MusicRecommenderEngine(get_music_search_tool())
    return _music_recommender

# 为了向后兼容，创建延迟初始化的属性访问器
class _LazyMusicTools:
    """延迟初始化的音乐工具访问器"""
    @property
    def music_search_tool(self):
        return get_music_search_tool()
    
    @property
    def music_recommender(self):
        return get_music_recommender()

_lazy_tools = _LazyMusicTools()

# 导出全局变量（向后兼容）
def __getattr__(name):
    if name == "music_search_tool":
        return get_music_search_tool()
    elif name == "music_recommender":
        return get_music_recommender()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# 直接创建实例（向后兼容，但会在导入时初始化）
try:
    music_search_tool = MusicSearchTool()
    music_recommender = MusicRecommenderEngine(music_search_tool)
except Exception as e:
    logger.warning(f"初始化全局音乐工具失败，将在首次使用时初始化: {str(e)}")
    # 如果初始化失败，设置为 None，将在首次使用时通过 get_music_search_tool() 初始化
    music_search_tool = None
    music_recommender = None

