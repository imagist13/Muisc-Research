"""
MCP 客户端适配器
封装 MCP 工具调用，提供统一的接口
"""

import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from config.logging_config import get_logger
from tools.music_tools import Song

logger = get_logger(__name__)


@dataclass
class PlaylistInfo:
    """播放列表信息"""
    id: str
    name: str
    url: str
    description: str
    track_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "track_count": self.track_count
        }


@dataclass
class Artist:
    """艺术家信息"""
    name: str
    id: Optional[str] = None
    genres: Optional[List[str]] = None
    popularity: Optional[int] = None
    external_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "id": self.id,
            "genres": self.genres or [],
            "popularity": self.popularity,
            "external_url": self.external_url
        }


class MCPClientAdapter:
    """MCP 客户端适配器 - 直接调用 MCP 服务器函数"""
    
    def __init__(self):
        """初始化适配器"""
        self._spotify_client = None
        self._mcp_server = None
        self._spotify_initialized = False
        self._spotify_init_failed = False
        logger.info("MCPClientAdapter 初始化")
    
    def _get_spotify_client(self):
        """获取 Spotify 客户端（延迟初始化）"""
        # 如果之前初始化失败，直接返回 None，避免重复尝试和日志
        if self._spotify_init_failed:
            return None
            
        if self._spotify_client is None and not self._spotify_initialized:
            try:
                # 直接导入 MCP 服务器的 Spotify 客户端
                import sys
                mcp_path = Path(__file__).parent.parent / "mcp"
                if str(mcp_path) not in sys.path:
                    sys.path.insert(0, str(mcp_path))
                
                # 将 mcp 目录添加到路径后，直接导入模块
                import music_server_updated_2025
                self._spotify_client = music_server_updated_2025.get_spotify_client()
                self._spotify_initialized = True
                logger.info("Spotify 客户端初始化成功")
            except Exception as e:
                self._spotify_init_failed = True
                self._spotify_initialized = True  # 标记为已尝试初始化，避免重复尝试
                error_msg = str(e)
                # 对于缺少凭证的情况，使用 WARNING 而不是 ERROR
                if "credentials not found" in error_msg.lower() or "spotify credentials" in error_msg.lower():
                    logger.warning("Spotify 凭证未配置，将使用本地数据库作为后备方案。")
                else:
                    logger.error(f"初始化 Spotify 客户端失败: {error_msg}")
                return None  # 返回 None 而不是 raise，让调用方优雅处理
        return self._spotify_client
    
    def _get_mcp_server(self):
        """获取 MCP 服务器模块（延迟初始化）"""
        if self._mcp_server is None:
            try:
                import sys
                mcp_path = Path(__file__).parent.parent / "mcp"
                if str(mcp_path) not in sys.path:
                    sys.path.insert(0, str(mcp_path))
                
                import music_server_updated_2025 as mcp_server
                self._mcp_server = mcp_server
                logger.info("MCP 服务器模块加载成功")
            except Exception as e:
                logger.error(f"加载 MCP 服务器模块失败: {str(e)}")
                raise
        return self._mcp_server
    
    def _spotify_track_to_song(self, track: Dict[str, Any]) -> Song:
        """将 Spotify track 数据转换为内部 Song 格式"""
        artists = track.get("artists", [])
        artist_names = [a.get("name", "") if isinstance(a, dict) else str(a) for a in artists]
        artist_str = ", ".join(artist_names) if artist_names else "未知"
        
        # 尝试从专辑获取年份
        album = track.get("album", {})
        release_date = album.get("release_date", "")
        year = None
        if release_date:
            try:
                year = int(release_date.split("-")[0])
            except:
                pass
        
        # 尝试从艺术家获取流派（需要额外 API 调用，这里先留空）
        genre = None
        
        return Song(
            title=track.get("name", "未知"),
            artist=artist_str,
            album=album.get("name") if isinstance(album, dict) else None,
            genre=genre,
            year=year,
            duration=track.get("duration_ms", 0) // 1000 if track.get("duration_ms") else None,
            popularity=track.get("popularity", 0),
            preview_url=track.get("preview_url"),
            spotify_id=track.get("id"),
            external_url=track.get("external_urls", {}).get("spotify") if isinstance(track.get("external_urls"), dict) else None
        )
    
    async def search_tracks(self, query: str, limit: int = 10) -> List[Song]:
        """
        搜索歌曲
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量
            
        Returns:
            歌曲列表
        """
        try:
            logger.info(f"搜索歌曲: query='{query}', limit={limit}")
            
            sp = self._get_spotify_client()
            results = sp.search(q=query, type="track", limit=limit)
            tracks = results["tracks"]["items"]
            
            songs = [self._spotify_track_to_song(track) for track in tracks]
            logger.info(f"搜索到 {len(songs)} 首歌曲")
            
            return songs
            
        except Exception as e:
            error_msg = str(e)
            # 对于缺少凭证的情况，使用 WARNING 而不是 ERROR
            if "credentials not found" in error_msg.lower() or "spotify credentials" in error_msg.lower():
                logger.warning(f"Spotify 未配置，无法搜索: {error_msg}。将使用本地数据库。")
            else:
                logger.error(f"搜索歌曲失败: {error_msg}", exc_info=True)
            return []
    
    async def get_recommendations(
        self,
        seed_tracks: Optional[List[str]] = None,
        seed_artists: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Song]:
        """
        获取 Spotify 推荐
        
        Args:
            seed_tracks: 种子歌曲 ID 列表（最多5个）
            seed_artists: 种子艺术家 ID 列表（最多5个）
            seed_genres: 种子流派列表（最多5个）
            limit: 推荐数量（1-100）
            
        Returns:
            推荐歌曲列表
        """
        try:
            logger.info(f"获取推荐: seed_tracks={len(seed_tracks) if seed_tracks else 0}, "
                       f"seed_artists={len(seed_artists) if seed_artists else 0}, "
                       f"seed_genres={len(seed_genres) if seed_genres else 0}, limit={limit}")
            
            sp = self._get_spotify_client()
            
            # 如果 Spotify 客户端不可用，直接返回空列表
            if sp is None:
                return []
            
            # 限制种子数量（Spotify API 要求）
            seed_tracks = (seed_tracks or [])[:5]
            seed_artists = (seed_artists or [])[:5]
            seed_genres = (seed_genres or [])[:5]
            
            # 确保至少有一个种子
            if not seed_tracks and not seed_artists and not seed_genres:
                logger.warning("没有提供种子，无法获取推荐")
                return []
            
            recommendations = sp.recommendations(
                seed_tracks=seed_tracks if seed_tracks else None,
                seed_artists=seed_artists if seed_artists else None,
                seed_genres=seed_genres if seed_genres else None,
                limit=min(limit, 100)  # Spotify 限制最多100
            )
            
            tracks = recommendations["tracks"]
            songs = [self._spotify_track_to_song(track) for track in tracks]
            
            logger.info(f"获取到 {len(songs)} 首推荐歌曲")
            return songs
            
        except Exception as e:
            error_msg = str(e)
            # 记录其他类型的错误（非凭证问题）
            logger.error(f"获取推荐失败: {error_msg}", exc_info=True)
            return []
    
    async def get_recommendations_by_names(
        self,
        seed_track_names: Optional[List[Dict[str, str]]] = None,
        seed_artist_names: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Song]:
        """
        通过歌曲名和艺术家名获取推荐（自动查找 ID）
        
        Args:
            seed_track_names: 种子歌曲列表 [{"song_name": "...", "artist_name": "..."}]
            seed_artist_names: 种子艺术家名称列表
            seed_genres: 种子流派列表
            limit: 推荐数量
            
        Returns:
            推荐歌曲列表
        """
        try:
            sp = self._get_spotify_client()
            
            # 查找歌曲 ID
            track_ids = []
            if seed_track_names:
                for track_data in seed_track_names[:5]:
                    song_name = track_data.get("song_name", "")
                    artist_name = track_data.get("artist_name", "")
                    
                    query = song_name
                    if artist_name:
                        query += f" artist:{artist_name}"
                    
                    search_results = sp.search(q=query, type="track", limit=1)
                    tracks = search_results["tracks"]["items"]
                    if tracks:
                        track_ids.append(tracks[0]["id"])
            
            # 查找艺术家 ID
            artist_ids = []
            if seed_artist_names:
                for artist_name in seed_artist_names[:5]:
                    search_results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
                    artists = search_results["artists"]["items"]
                    if artists:
                        artist_ids.append(artists[0]["id"])
            
            # 使用找到的 ID 获取推荐
            return await self.get_recommendations(
                seed_tracks=track_ids if track_ids else None,
                seed_artists=artist_ids if artist_ids else None,
                seed_genres=seed_genres,
                limit=limit
            )
            
        except Exception as e:
            error_msg = str(e)
            # 对于缺少凭证的情况，使用 WARNING 而不是 ERROR
            if "credentials not found" in error_msg.lower() or "spotify credentials" in error_msg.lower():
                logger.warning(f"Spotify 未配置，无法获取推荐: {error_msg}。将使用本地数据库。")
            else:
                logger.error(f"通过名称获取推荐失败: {error_msg}", exc_info=True)
            return []
    
    async def get_user_top_tracks(self, limit: int = 20, time_range: str = "medium_term") -> List[Song]:
        """
        获取用户热门歌曲
        
        Args:
            limit: 返回数量（1-50）
            time_range: 时间范围 ("short_term", "medium_term", "long_term")
            
        Returns:
            用户热门歌曲列表
        """
        try:
            logger.info(f"获取用户热门歌曲: limit={limit}, time_range={time_range}")
            
            sp = self._get_spotify_client()
            results = sp.current_user_top_tracks(limit=min(limit, 50), time_range=time_range)
            tracks = results["items"]
            
            songs = [self._spotify_track_to_song(track) for track in tracks]
            logger.info(f"获取到 {len(songs)} 首用户热门歌曲")
            
            return songs
            
        except Exception as e:
            error_msg = str(e)
            # 对于缺少凭证的情况，使用 WARNING 而不是 ERROR
            if "credentials not found" in error_msg.lower() or "spotify credentials" in error_msg.lower():
                logger.warning(f"Spotify 未配置，无法获取用户热门歌曲: {error_msg}。将使用本地数据库。")
            else:
                logger.error(f"获取用户热门歌曲失败: {error_msg}", exc_info=True)
            return []
    
    async def get_user_top_artists(self, limit: int = 20, time_range: str = "medium_term") -> List[Artist]:
        """
        获取用户热门艺术家
        
        Args:
            limit: 返回数量（1-50）
            time_range: 时间范围 ("short_term", "medium_term", "long_term")
            
        Returns:
            用户热门艺术家列表
        """
        try:
            logger.info(f"获取用户热门艺术家: limit={limit}, time_range={time_range}")
            
            sp = self._get_spotify_client()
            results = sp.current_user_top_artists(limit=min(limit, 50), time_range=time_range)
            artists = results["items"]
            
            artist_list = []
            for artist in artists:
                artist_list.append(Artist(
                    name=artist.get("name", "未知"),
                    id=artist.get("id"),
                    genres=artist.get("genres", []),
                    popularity=artist.get("popularity", 0),
                    external_url=artist.get("external_urls", {}).get("spotify") if isinstance(artist.get("external_urls"), dict) else None
                ))
            
            logger.info(f"获取到 {len(artist_list)} 个用户热门艺术家")
            return artist_list
            
        except Exception as e:
            error_msg = str(e)
            # 对于缺少凭证的情况，使用 WARNING 而不是 ERROR
            if "credentials not found" in error_msg.lower() or "spotify credentials" in error_msg.lower():
                logger.warning(f"Spotify 未配置，无法获取用户热门艺术家: {error_msg}。将使用本地数据库。")
            else:
                logger.error(f"获取用户热门艺术家失败: {error_msg}", exc_info=True)
            return []
    
    async def create_playlist(
        self,
        name: str,
        songs: List[Song],
        description: Optional[str] = None,
        public: bool = False
    ) -> Optional[PlaylistInfo]:
        """
        创建 Spotify 播放列表
        
        Args:
            name: 播放列表名称
            songs: 歌曲列表
            description: 描述
            public: 是否公开
            
        Returns:
            播放列表信息
        """
        try:
            logger.info(f"创建播放列表: name='{name}', songs={len(songs)}, public={public}")
            
            sp = self._get_spotify_client()
            
            # 获取当前用户 ID
            user = sp.current_user()
            user_id = user["id"]
            
            # 创建播放列表
            playlist = sp.user_playlist_create(
                user=user_id,
                name=name,
                public=public,
                description=description or ""
            )
            
            playlist_id = playlist["id"]
            
            # 获取歌曲 URI
            track_uris = []
            for song in songs:
                if song.spotify_id:
                    track_uris.append(f"spotify:track:{song.spotify_id}")
                else:
                    # 如果没有 ID，尝试搜索
                    search_results = sp.search(
                        q=f"track:{song.title} artist:{song.artist}",
                        type="track",
                        limit=1
                    )
                    tracks = search_results["tracks"]["items"]
                    if tracks:
                        track_uris.append(tracks[0]["uri"])
            
            # 添加歌曲到播放列表（分批添加，每批最多100首）
            if track_uris:
                for i in range(0, len(track_uris), 100):
                    batch = track_uris[i:i+100]
                    sp.playlist_add_items(playlist_id, batch)
            
            playlist_info = PlaylistInfo(
                id=playlist_id,
                name=playlist["name"],
                url=playlist["external_urls"]["spotify"],
                description=playlist.get("description", ""),
                track_count=len(track_uris)
            )
            
            logger.info(f"播放列表创建成功: {playlist_info.url}")
            return playlist_info
            
        except Exception as e:
            error_msg = str(e)
            # 对于缺少凭证的情况，使用 WARNING 而不是 ERROR
            if "credentials not found" in error_msg.lower() or "spotify credentials" in error_msg.lower():
                logger.warning(f"Spotify 未配置，无法创建播放列表: {error_msg}。")
            else:
                logger.error(f"创建播放列表失败: {error_msg}", exc_info=True)
            return None
    
    async def analyze_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """
        分析播放列表
        
        Args:
            playlist_id: 播放列表 ID
            
        Returns:
            分析结果
        """
        try:
            logger.info(f"分析播放列表: playlist_id={playlist_id}")
            
            mcp_server = self._get_mcp_server()
            
            # 调用 MCP 服务器的 analyze_playlist 工具
            arguments = {"playlist_id": playlist_id}
            result = await mcp_server.call_tool("analyze_playlist", arguments)
            
            # 解析结果
            if result and len(result) > 0:
                text_content = result[0].text
                analysis = json.loads(text_content)
                return analysis
            else:
                return {}
                
        except Exception as e:
            logger.error(f"分析播放列表失败: {str(e)}", exc_info=True)
            return {}


# 创建全局实例
_mcp_adapter = None

def get_mcp_adapter() -> MCPClientAdapter:
    """获取 MCP 适配器单例"""
    global _mcp_adapter
    if _mcp_adapter is None:
        _mcp_adapter = MCPClientAdapter()
    return _mcp_adapter

