"""
歌单推荐服务
结合 Spotify + 用户上下文生成智能歌单
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

from config.logging_config import get_logger
from schemas.music_state import UserPreferences
from tools.mcp_adapter import MCPClientAdapter, PlaylistInfo
from tools.music_tools import Song, get_music_search_tool

logger = get_logger(__name__)


# 关键词 → Spotify 流派映射（与 MusicRecommenderEngine 对齐，补充中文别名）
MOOD_TO_GENRES: Dict[str, Sequence[str]] = {
    "开心": ("pop", "dance", "electronic"),
    "快乐": ("pop", "dance", "electronic"),
    "高兴": ("pop", "dance", "electronic"),
    "兴奋": ("rock", "electronic", "dance"),
    "激动": ("rock", "electronic", "dance"),
    "悲伤": ("acoustic", "sad", "indie", "mellow"),
    "伤心": ("acoustic", "sad", "indie", "mellow"),
    "难过": ("acoustic", "sad", "indie", "piano"),
    "丧": ("acoustic", "sad", "indie"),
    "疗愈": ("acoustic", "mellow", "indie"),
    "放松": ("chill", "acoustic", "jazz", "ambient"),
    "舒缓": ("chill", "acoustic", "jazz", "ambient"),
    "平静": ("ambient", "acoustic", "chill"),
    "安静": ("ambient", "acoustic", "chill"),
    "怀旧": ("classic", "pop", "rock", "indie"),
    "浪漫": ("acoustic", "pop", "r-n-b", "soul"),
    "甜蜜": ("pop", "r-n-b", "soul"),
    "表白": ("r-n-b", "soul", "pop"),
    "学习": ("lo-fi", "chill", "ambient", "acoustic"),
    "专注": ("lo-fi", "ambient", "acoustic"),
    "运动": ("electronic", "rock", "dance"),
}

ACTIVITY_TO_GENRES: Dict[str, Sequence[str]] = {
    "运动": ("electronic", "rock", "dance"),
    "健身": ("electronic", "rock", "dance"),
    "跑步": ("electronic", "rock", "dance"),
    "学习": ("acoustic", "jazz", "chill"),
    "工作": ("acoustic", "jazz", "chill"),
    "写作": ("lo-fi", "ambient", "acoustic"),
    "开车": ("pop", "rock", "country"),
    "通勤": ("pop", "indie", "electronic"),
    "睡觉": ("ambient", "acoustic", "chill"),
    "休息": ("acoustic", "chill", "jazz"),
    "派对": ("dance", "pop", "electronic"),
    "聚会": ("pop", "dance", "electronic"),
}


class PlaylistRecommendationService:
    """基于 MCP 的歌单推荐服务"""

    def __init__(self, mcp_adapter: Optional[MCPClientAdapter] = None) -> None:
        self.mcp_adapter = mcp_adapter or MCPClientAdapter()
        self._search_tool = None
        logger.info("PlaylistRecommendationService 初始化完成")

    # ------------------------------------------------------------------ #
    # 公共接口
    # ------------------------------------------------------------------ #
    async def generate_smart_playlist(
        self,
        user_query: str,
        user_preferences: Optional[UserPreferences] = None,
        target_size: int = 30,
        create_spotify_playlist: bool = True,
        public: bool = False,
    ) -> Dict[str, Any]:
        """
        生成智能歌单

        Args:
            user_query: 用户自然语言请求
            user_preferences: 用户偏好（流派/歌手/年代等）
            target_size: 目标歌曲数量
            create_spotify_playlist: 是否同步创建 Spotify 播放列表
            public: Spotify 播放列表是否公开

        Returns:
            {
                "songs": [Song dict...],
                "playlist": Optional[PlaylistInfo dict],
                "context": {...},
                "seed_summary": {...}
            }
        """
        prefs = user_preferences or {}
        context = self._analyze_query(user_query)
        logger.info(
            "生成智能歌单: query='%s', target_size=%s, context=%s",
            user_query,
            target_size,
            context,
        )

        # 准备种子
        seed_track_names, seed_artist_names = await self._prepare_seed_names(
            user_query, prefs
        )
        seed_genres = self._derive_seed_genres(context, prefs)

        seed_summary = {
            "tracks": seed_track_names[:5],
            "artists": seed_artist_names[:5],
            "genres": seed_genres[:5],
        }

        candidates: List[Song] = []

        # Step 1: 通过名称获取推荐（自动解析 ID）
        try:
            if seed_track_names or seed_artist_names or seed_genres:
                candidates.extend(
                    await self.mcp_adapter.get_recommendations_by_names(
                        seed_track_names=seed_track_names or None,
                        seed_artist_names=seed_artist_names or None,
                        seed_genres=seed_genres or None,
                        limit=max(target_size * 2, 20),
                    )
                )
        except Exception as err:  # noqa: BLE001
            logger.warning("通过名称获取推荐失败: %s", err)

        # Step 2: 如果还不够，尝试基于 ID 的推荐（使用 query 搜索的 Top 结果）
        if len(candidates) < target_size:
            track_ids = await self._search_track_ids_for_query(user_query)
            if track_ids or seed_genres:
                try:
                    extra = await self.mcp_adapter.get_recommendations(
                        seed_tracks=track_ids or None,
                        seed_genres=seed_genres or None,
                        limit=max(target_size * 2, 20),
                    )
                    candidates.extend(extra)
                except Exception as err:  # noqa: BLE001
                    logger.warning("通过 ID 获取推荐失败: %s", err)

        # Step 3: 兜底使用用户热门歌曲
        if len(candidates) < target_size:
            try:
                top_tracks = await self.mcp_adapter.get_user_top_tracks(
                    limit=target_size
                )
                candidates.extend(top_tracks)
            except Exception as err:  # noqa: BLE001
                logger.debug("获取用户热门歌曲失败: %s", err)

        # 去重并平衡
        unique_candidates = self._merge_unique_songs(candidates)
        balanced_songs = self.balance_playlist(unique_candidates, target_size)

        if not balanced_songs:
            logger.error("无法生成歌单，候选歌曲为空")
            return {
                "songs": [],
                "playlist": None,
                "context": context,
                "seed_summary": seed_summary,
            }

        playlist_meta: Optional[PlaylistInfo] = None
        if create_spotify_playlist:
            playlist_meta = await self._create_spotify_playlist(
                songs=balanced_songs,
                user_query=user_query,
                context=context,
                preferences=prefs,
                public=public,
            )

        logger.info(
            "歌单生成完成: songs=%s, playlist_created=%s",
            len(balanced_songs),
            bool(playlist_meta),
        )

        return {
            "songs": [song.to_dict() for song in balanced_songs],
            "playlist": playlist_meta.to_dict() if playlist_meta else None,
            "context": context,
            "seed_summary": seed_summary,
        }

    # ------------------------------------------------------------------ #
    # Playlist balancing
    # ------------------------------------------------------------------ #
    def balance_playlist(
        self,
        songs: List[Song],
        target_size: int = 30,
        balance_by: str = "genre",
    ) -> List[Song]:
        """
        对歌曲进行平衡（按流派/艺人轮询），提升歌单多样性
        """
        if not songs or target_size <= 0:
            return []

        # 去重（优先按 Spotify ID）
        deduped: List[Song] = []
        seen: set[str] = set()
        for song in songs:
            key = song.spotify_id or f"{song.title}-{song.artist}".lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(song)

        logger.debug("去重后候选歌曲数量: %s", len(deduped))

        # 构建分组
        group_key = (
            (lambda s: (s.genre or "未知").lower())
            if balance_by == "genre"
            else (lambda s: (s.artist or "未知").lower())
        )
        buckets: Dict[str, List[Song]] = defaultdict(list)
        for song in deduped:
            buckets[group_key(song)].append(song)

        for bucket in buckets.values():
            bucket.sort(key=lambda s: s.popularity or 0, reverse=True)

        # 轮询取歌
        balanced: List[Song] = []
        bucket_keys = list(buckets.keys())
        pointer = 0
        while bucket_keys and len(balanced) < target_size:
            key = bucket_keys[pointer % len(bucket_keys)]
            bucket = buckets[key]
            if bucket:
                balanced.append(bucket.pop(0))
            if not bucket:
                bucket_keys.remove(key)
                pointer = 0
            else:
                pointer += 1

        # 若仍不足，补齐最热门的剩余歌曲
        if len(balanced) < target_size:
            remaining = [
                song for bucket in buckets.values() for song in bucket if song
            ]
            remaining.sort(key=lambda s: s.popularity or 0, reverse=True)
            for song in remaining:
                if len(balanced) >= target_size:
                    break
                balanced.append(song)

        return balanced[:target_size]

    # ------------------------------------------------------------------ #
    # Helper methods
    # ------------------------------------------------------------------ #
    def _get_search_tool(self):
        if self._search_tool is None:
            self._search_tool = get_music_search_tool()
        return self._search_tool

    def _analyze_query(self, user_query: str) -> Dict[str, Any]:
        query = user_query.lower() if user_query else ""
        detected_moods = [
            mood for mood in MOOD_TO_GENRES.keys() if mood in user_query
        ]
        detected_activities = [
            act for act in ACTIVITY_TO_GENRES.keys() if act in user_query
        ]
        return {
            "moods": detected_moods,
            "activities": detected_activities,
            "has_query": bool(user_query.strip()),
        }

    def _derive_seed_genres(
        self, context: Dict[str, Any], preferences: UserPreferences
    ) -> List[str]:
        seed_genres: List[str] = []

        for mood in context.get("moods", []):
            seed_genres.extend(MOOD_TO_GENRES.get(mood, ()))
        for activity in context.get("activities", []):
            seed_genres.extend(ACTIVITY_TO_GENRES.get(activity, ()))

        seed_genres.extend(
            [genre.lower() for genre in preferences.get("favorite_genres", [])]
        )

        # 去重
        unique_genres: List[str] = []
        for genre in seed_genres:
            if genre not in unique_genres:
                unique_genres.append(genre)

        logger.debug("生成种子流派: %s", unique_genres)
        return unique_genres

    async def _prepare_seed_names(
        self, user_query: str, preferences: UserPreferences
    ) -> Tuple[List[Dict[str, str]], List[str]]:
        track_seeds: List[Dict[str, str]] = []
        artist_seeds: List[str] = []

        # 用户显式偏好
        for fav in preferences.get("favorite_artists", [])[:5]:
            if fav and isinstance(fav, str):
                artist_seeds.append(fav)

        favorite_songs = preferences.get("favorite_songs", []) or []
        for fav in favorite_songs[:5]:
            title = fav.get("title") or fav.get("song") or fav.get("name")
            artist = fav.get("artist") or fav.get("artist_name")
            if title:
                track_seeds.append(
                    {"song_name": title, "artist_name": artist or ""}
                )

        # 从 query 搜索候选歌曲（帮助 cold-start）
        if user_query:
            try:
                search_results = await self._get_search_tool().search_songs(
                    user_query, limit=3
                )
                for song in search_results:
                    track_seeds.append(
                        {"song_name": song.title, "artist_name": song.artist}
                    )
            except Exception as err:  # noqa: BLE001
                logger.debug("根据 query 搜索歌曲失败: %s", err)

        # 去重
        unique_tracks: List[Dict[str, str]] = []
        seen_pairs: set[Tuple[str, str]] = set()
        for item in track_seeds:
            key = (item["song_name"].lower(), item.get("artist_name", "").lower())
            if key not in seen_pairs:
                unique_tracks.append(item)
                seen_pairs.add(key)

        unique_artists = []
        seen_artists = set()
        for artist in artist_seeds:
            key = artist.lower()
            if key not in seen_artists:
                unique_artists.append(artist)
                seen_artists.add(key)

        logger.debug(
            "生成种子歌曲: %s, 艺术家: %s",
            [t["song_name"] for t in unique_tracks],
            unique_artists,
        )
        return unique_tracks, unique_artists

    async def _search_track_ids_for_query(self, query: str) -> List[str]:
        if not query.strip():
            return []
        try:
            songs = await self._get_search_tool().search_songs(query, limit=5)
            return [
                song.spotify_id
                for song in songs
                if song.spotify_id and song.spotify_id.strip()
            ][:5]
        except Exception as err:  # noqa: BLE001
            logger.debug("搜索歌曲 ID 失败: %s", err)
            return []

    def _merge_unique_songs(self, songs: List[Song]) -> List[Song]:
        merged: List[Song] = []
        seen = set()
        for song in songs:
            key = song.spotify_id or f"{song.title}-{song.artist}".lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append(song)
        return merged

    async def _create_spotify_playlist(
        self,
        songs: List[Song],
        user_query: str,
        context: Dict[str, Any],
        preferences: UserPreferences,
        public: bool,
    ) -> Optional[PlaylistInfo]:
        if not songs:
            return None

        playlist_name = self._build_playlist_name(user_query, context, preferences)
        description = self._build_playlist_description(
            user_query=user_query,
            context=context,
            song_count=len(songs),
        )

        try:
            playlist = await self.mcp_adapter.create_playlist(
                name=playlist_name,
                songs=songs,
                description=description,
                public=public,
            )
            return playlist
        except Exception as err:  # noqa: BLE001
            logger.warning("创建 Spotify 播放列表失败: %s", err)
            return None

    def _build_playlist_name(
        self,
        user_query: str,
        context: Dict[str, Any],
        preferences: UserPreferences,
    ) -> str:
        if context.get("moods"):
            mood = context["moods"][0]
            return f"{mood}心情专属歌单"
        if context.get("activities"):
            activity = context["activities"][0]
            return f"适合{activity}的节奏"
        if preferences.get("favorite_artists"):
            artist = preferences["favorite_artists"][0]
            return f"{artist}灵感精选"
        if preferences.get("favorite_genres"):
            genre = preferences["favorite_genres"][0]
            return f"{genre}氛围歌单"
        if user_query.strip():
            return f"AI 智能歌单：{user_query[:24]}"
        return "AI 智能歌单"

    def _build_playlist_description(
        self,
        user_query: str,
        context: Dict[str, Any],
        song_count: int,
    ) -> str:
        parts = []
        if user_query.strip():
            parts.append(f"用户需求：{user_query.strip()}")
        if context.get("moods"):
            parts.append(f"感知心情：{', '.join(context['moods'])}")
        if context.get("activities"):
            parts.append(f"适配场景：{', '.join(context['activities'])}")
        parts.append(f"共收录 {song_count} 首精选歌曲")
        parts.append(
            f"由 AI 在 {datetime.now().strftime('%Y-%m-%d %H:%M')} 自动生成"
        )
        return " | ".join(parts)


__all__ = ["PlaylistRecommendationService"]

