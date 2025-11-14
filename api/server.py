"""
FastAPI后端服务器
支持SSE流式输出音乐推荐
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional

# 添加项目根目录到Python路径（如果还没有）
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# 在导入其他模块之前加载配置
try:
    from config.settings_loader import load_and_setup_settings
    load_and_setup_settings()
except Exception as e:
    print(f"警告: 无法从 setting.json 加载配置: {e}")

from config.logging_config import get_logger
from music_agent import MusicRecommendationAgent
from services import PlaylistRecommendationService

logger = get_logger(__name__)

app = FastAPI(title="Music Recommendation API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局Agent实例
_agent: Optional[MusicRecommendationAgent] = None
_playlist_service: Optional[PlaylistRecommendationService] = None


def get_agent() -> MusicRecommendationAgent:
    """获取Agent实例（单例模式）"""
    global _agent
    if _agent is None:
        _agent = MusicRecommendationAgent()
    return _agent


def get_playlist_service() -> PlaylistRecommendationService:
    """获取歌单服务实例（单例模式）"""
    global _playlist_service
    if _playlist_service is None:
        _playlist_service = PlaylistRecommendationService()
    return _playlist_service


# 请求模型
class RecommendationRequest(BaseModel):
    query: str
    genre: Optional[str] = None
    mood: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None


class PlaylistRequest(BaseModel):
    query: str
    target_size: int = 30
    create_spotify_playlist: bool = False
    public: bool = False
    user_preferences: Optional[Dict[str, Any]] = None


async def stream_recommendations(
    query: str,
    genre: Optional[str] = None,
    mood: Optional[str] = None,
    user_preferences: Optional[Dict[str, Any]] = None
) -> AsyncGenerator[str, None]:
    """
    流式生成推荐结果
    
    Yields:
        SSE格式的数据块
    """
    try:
        agent = get_agent()
        
        # 发送开始事件
        yield f"data: {json.dumps({'type': 'start', 'message': '开始分析你的需求...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.1)
        
        # 发送思考事件
        yield f"data: {json.dumps({'type': 'thinking', 'message': '正在理解你的音乐偏好...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.2)
        
        # 执行推荐（这里可以进一步拆分步骤）
        result = await agent.get_recommendations(
            query=query,
            user_preferences=user_preferences
        )
        
        # 发送响应文本（流式输出）
        if result.get("success") and result.get("response"):
            response_text = result["response"]
            # 逐字符或逐词流式输出
            words = response_text.split()
            for i, word in enumerate(words):
                partial_text = " ".join(words[:i+1])
                yield f"data: {json.dumps({'type': 'response', 'text': partial_text, 'is_complete': False}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.05)  # 控制输出速度
            
            # 发送完整响应
            yield f"data: {json.dumps({'type': 'response', 'text': response_text, 'is_complete': True}, ensure_ascii=False)}\n\n"
        
        # 发送推荐歌曲（逐个发送）
        if result.get("success") and result.get("recommendations"):
            recommendations = result["recommendations"]
            yield f"data: {json.dumps({'type': 'recommendations_start', 'count': len(recommendations)}, ensure_ascii=False)}\n\n"
            
            for i, rec in enumerate(recommendations):
                song = rec.get("song", rec)
                yield f"data: {json.dumps({'type': 'song', 'song': song, 'index': i, 'total': len(recommendations)}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)
            
            yield f"data: {json.dumps({'type': 'recommendations_complete'}, ensure_ascii=False)}\n\n"
        
        # 发送完成事件
        yield f"data: {json.dumps({'type': 'complete', 'success': True}, ensure_ascii=False)}\n\n"
        
    except Exception as e:
        logger.error(f"流式推荐失败: {str(e)}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"


async def stream_playlist(
    query: str,
    target_size: int = 30,
    create_spotify_playlist: bool = False,
    public: bool = False,
    user_preferences: Optional[Dict[str, Any]] = None
) -> AsyncGenerator[str, None]:
    """
    流式生成歌单
    
    Yields:
        SSE格式的数据块
    """
    try:
        service = get_playlist_service()
        
        # 发送开始事件
        yield f"data: {json.dumps({'type': 'start', 'message': '开始生成你的专属歌单...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.1)
        
        # 分析查询
        yield f"data: {json.dumps({'type': 'thinking', 'message': '正在分析你的需求...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.2)
        
        # 准备种子
        yield f"data: {json.dumps({'type': 'thinking', 'message': '正在准备推荐种子...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.2)
        
        # 获取推荐
        yield f"data: {json.dumps({'type': 'thinking', 'message': '正在从Spotify获取推荐...'}, ensure_ascii=False)}\n\n"
        
        # 执行歌单生成
        result = await service.generate_smart_playlist(
            user_query=query,
            user_preferences=user_preferences or {},
            target_size=target_size,
            create_spotify_playlist=create_spotify_playlist,
            public=public
        )
        
        # 发送上下文信息
        if result.get("context"):
            yield f"data: {json.dumps({'type': 'context', 'context': result['context']}, ensure_ascii=False)}\n\n"
        
        # 发送种子摘要
        if result.get("seed_summary"):
            yield f"data: {json.dumps({'type': 'seed_summary', 'seed_summary': result['seed_summary']}, ensure_ascii=False)}\n\n"
        
        # 发送歌曲列表（逐个发送）
        if result.get("songs"):
            songs = result["songs"]
            yield f"data: {json.dumps({'type': 'songs_start', 'count': len(songs)}, ensure_ascii=False)}\n\n"
            
            for i, song in enumerate(songs):
                yield f"data: {json.dumps({'type': 'song', 'song': song, 'index': i, 'total': len(songs)}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.05)
            
            yield f"data: {json.dumps({'type': 'songs_complete'}, ensure_ascii=False)}\n\n"
        
        # 发送播放列表信息
        if result.get("playlist"):
            yield f"data: {json.dumps({'type': 'playlist', 'playlist': result['playlist']}, ensure_ascii=False)}\n\n"
        
        # 发送完成事件
        yield f"data: {json.dumps({'type': 'complete', 'success': True}, ensure_ascii=False)}\n\n"
        
    except Exception as e:
        logger.error(f"流式歌单生成失败: {str(e)}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"


@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "service": "Music Recommendation API"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/api/recommendations/stream")
async def stream_recommendations_endpoint(request: RecommendationRequest):
    """
    流式获取音乐推荐（SSE）
    """
    return StreamingResponse(
        stream_recommendations(
            query=request.query,
            genre=request.genre,
            mood=request.mood,
            user_preferences=request.user_preferences
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/playlist/stream")
async def stream_playlist_endpoint(request: PlaylistRequest):
    """
    流式生成歌单（SSE）
    """
    return StreamingResponse(
        stream_playlist(
            query=request.query,
            target_size=request.target_size,
            create_spotify_playlist=request.create_spotify_playlist,
            public=request.public,
            user_preferences=request.user_preferences
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """
    获取音乐推荐（非流式，兼容旧接口）
    """
    try:
        agent = get_agent()
        result = await agent.get_recommendations(
            query=request.query,
            user_preferences=request.user_preferences
        )
        return result
    except Exception as e:
        logger.error(f"获取推荐失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/playlist")
async def generate_playlist(request: PlaylistRequest):
    """
    生成歌单（非流式，兼容旧接口）
    """
    try:
        service = get_playlist_service()
        result = await service.generate_smart_playlist(
            user_query=request.query,
            user_preferences=request.user_preferences or {},
            target_size=request.target_size,
            create_spotify_playlist=request.create_spotify_playlist,
            public=request.public
        )
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"生成歌单失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", "8501"))
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

