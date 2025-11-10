# 🚀 歌单推荐功能实现指南

## 📋 快速开始

### 第一步：理解架构

请先阅读：
- [架构设计文档](./PLAYLIST_RECOMMENDATION_ARCHITECTURE.md) - 详细设计
- [架构图](./ARCHITECTURE_DIAGRAM.md) - 可视化视图

### 第二步：检查依赖

确保已安装：
```bash
pip install spotipy python-dotenv mcp
```

确保已配置：
- Spotify API 凭证（`.env` 文件）
- MCP 服务器可运行（`mcp/music_server_updated_2025.py`）

### 第三步：实现顺序

按照以下顺序实现：

## 📝 实现步骤

### Step 1: 创建 MCP 适配器基础结构

**文件**: `tools/mcp_adapter.py`

```python
"""
MCP 客户端适配器
封装 MCP 工具调用，提供统一的接口
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

# 需要导入你的 Song 数据类
from tools.music_tools import Song


@dataclass
class PlaylistInfo:
    """播放列表信息"""
    id: str
    name: str
    url: str
    description: str
    track_count: int


class MCPClientAdapter:
    """MCP 客户端适配器"""
    
    def __init__(self):
        # TODO: 初始化 MCP 客户端连接
        # 选项1: 使用 MCP SDK
        # 选项2: 直接导入 MCP 服务器函数
        pass
    
    async def search_tracks(self, query: str, limit: int = 10) -> List[Song]:
        """搜索歌曲"""
        # TODO: 调用 MCP search_tracks 工具
        # TODO: 转换数据格式
        pass
    
    async def get_recommendations(
        self,
        seed_tracks: List[str] = None,
        seed_artists: List[str] = None,
        seed_genres: List[str] = None,
        limit: int = 20
    ) -> List[Song]:
        """获取推荐"""
        # TODO: 调用 MCP get_recommendations 工具
        pass
    
    # ... 其他方法
```

**任务清单**:
- [ ] 创建文件结构
- [ ] 实现 MCP 客户端连接（选择连接方式）
- [ ] 实现 `search_tracks` 方法
- [ ] 实现数据格式转换函数
- [ ] 编写单元测试

### Step 2: 重构音乐工具

**文件**: `tools/music_tools.py`

**修改点**:
1. `MusicSearchTool.__init__()` - 添加 `mcp_adapter` 参数
2. `MusicSearchTool.search_songs()` - 使用 MCP 适配器
3. `MusicRecommenderEngine.__init__()` - 添加 `mcp_adapter` 参数
4. `MusicRecommenderEngine.recommend_by_mood()` - 使用 MCP 推荐

**示例**:
```python
class MusicSearchTool:
    def __init__(self, mcp_adapter: MCPClientAdapter = None):
        if mcp_adapter is None:
            from tools.mcp_adapter import MCPClientAdapter
            mcp_adapter = MCPClientAdapter()
        self.mcp_adapter = mcp_adapter
        # 移除旧的模拟数据初始化
    
    async def search_songs(self, query: str, genre: str = None, limit: int = 10):
        # 使用 MCP 适配器搜索
        songs = await self.mcp_adapter.search_tracks(query, limit)
        
        # 如果有流派过滤，在这里过滤
        if genre:
            # TODO: 实现流派过滤（需要从 artist 获取流派）
            pass
        
        return songs
```

**任务清单**:
- [ ] 修改 `MusicSearchTool` 使用 MCP
- [ ] 修改 `MusicRecommenderEngine` 使用 MCP
- [ ] 移除模拟数据代码
- [ ] 更新所有调用处
- [ ] 运行测试确保兼容性

### Step 3: 扩展工作流图

**文件**: `graphs/music_graph.py`

**新增节点**:

```python
async def analyze_user_preferences_node(self, state: MusicAgentState) -> Dict[str, Any]:
    """分析用户偏好节点"""
    logger.info("--- [步骤] 分析用户偏好 ---")
    
    try:
        from tools.mcp_adapter import MCPClientAdapter
        adapter = MCPClientAdapter()
        
        # 获取用户数据
        top_tracks = await adapter.get_user_top_tracks(limit=20)
        top_artists = await adapter.get_user_top_artists(limit=20)
        
        # 分析偏好
        preferences = extract_user_preferences(top_tracks, top_artists)
        
        return {
            "user_preferences": preferences,
            "favorite_songs": [song.to_dict() for song in top_tracks],
            "step_count": state.get("step_count", 0) + 1
        }
    except Exception as e:
        logger.error(f"分析用户偏好失败: {str(e)}")
        return {
            "user_preferences": {},
            "step_count": state.get("step_count", 0) + 1,
            "error_log": state.get("error_log", []) + [
                {"node": "analyze_user_preferences", "error": str(e)}
            ]
        }


async def create_playlist_node(self, state: MusicAgentState) -> Dict[str, Any]:
    """创建歌单节点"""
    logger.info("--- [步骤] 创建播放列表 ---")
    
    try:
        from tools.mcp_adapter import MCPClientAdapter
        adapter = MCPClientAdapter()
        
        # 获取推荐结果
        recommendations = state.get("recommendations", [])
        songs = [rec["song"] for rec in recommendations]
        
        # 生成播放列表名称和描述
        intent = state.get("intent_type", "")
        playlist_name = generate_playlist_name(intent, state)
        description = generate_playlist_description(state)
        
        # 创建播放列表
        playlist = await adapter.create_playlist(
            name=playlist_name,
            songs=songs,
            description=description,
            public=False
        )
        
        return {
            "playlist": playlist.to_dict(),
            "step_count": state.get("step_count", 0) + 1
        }
    except Exception as e:
        logger.error(f"创建播放列表失败: {str(e)}")
        return {
            "playlist": None,
            "step_count": state.get("step_count", 0) + 1,
            "error_log": state.get("error_log", []) + [
                {"node": "create_playlist", "error": str(e)}
            ]
        }
```

**更新路由**:
```python
def route_by_intent(self, state: MusicAgentState) -> str:
    """根据意图路由"""
    intent = state.get("intent_type", "")
    
    if intent.startswith("create_playlist"):
        return "create_playlist"
    elif intent == "search_songs":
        return "search_songs"
    # ... 其他路由
```

**任务清单**:
- [ ] 添加 `analyze_user_preferences_node`
- [ ] 添加 `create_playlist_node`
- [ ] 更新路由逻辑
- [ ] 更新图结构
- [ ] 测试新节点

### Step 4: 创建歌单推荐服务

**文件**: `services/playlist_service.py` (新建)

```python
"""
歌单推荐服务
核心业务逻辑
"""

from typing import List, Dict, Any
from tools.mcp_adapter import MCPClientAdapter, PlaylistInfo
from schemas.music_state import UserPreferences


class PlaylistRecommendationService:
    """歌单推荐服务"""
    
    def __init__(self, mcp_adapter: MCPClientAdapter = None):
        if mcp_adapter is None:
            mcp_adapter = MCPClientAdapter()
        self.mcp_adapter = mcp_adapter
    
    async def generate_smart_playlist(
        self,
        user_query: str,
        user_preferences: UserPreferences = None,
        target_size: int = 30
    ) -> PlaylistInfo:
        """生成智能歌单"""
        # 1. 理解用户需求
        # 2. 获取推荐
        # 3. 平衡歌单
        # 4. 创建播放列表
        pass
    
    def balance_playlist(
        self,
        songs: List[Song],
        target_size: int = 30,
        balance_by: str = "genre"
    ) -> List[Song]:
        """平衡歌单"""
        # 实现平衡算法
        pass
```

**任务清单**:
- [ ] 创建服务文件
- [ ] 实现智能歌单生成
- [ ] 实现平衡算法
- [ ] 编写测试

## 🔧 技术细节

### MCP 客户端连接方式

**方式 1: 直接导入 MCP 服务器函数**（推荐用于开发）

```python
# 在 mcp_adapter.py 中
from mcp.music_server_updated_2025 import get_spotify_client, call_tool

class MCPClientAdapter:
    def __init__(self):
        self.sp = get_spotify_client()
    
    async def search_tracks(self, query: str, limit: int = 10):
        # 直接调用 Spotify API
        results = self.sp.search(q=query, type="track", limit=limit)
        # 转换格式
        return convert_to_songs(results)
```

**方式 2: 使用 MCP SDK 客户端**（推荐用于生产）

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClientAdapter:
    def __init__(self):
        self.session = None  # 在 async 上下文中初始化
    
    async def __aenter__(self):
        server_params = StdioServerParameters(
            command="python",
            args=["mcp/music_server_updated_2025.py"]
        )
        self.session = await stdio_client(server_params)
        return self
    
    async def search_tracks(self, query: str, limit: int = 10):
        result = await self.session.call_tool(
            "search_tracks",
            {"query": query, "limit": limit}
        )
        return convert_to_songs(result)
```

### 数据格式转换

```python
def spotify_track_to_song(track: Dict) -> Song:
    """Spotify track → Song"""
    return Song(
        title=track["name"],
        artist=", ".join([a["name"] for a in track["artists"]]),
        album=track["album"]["name"],
        popularity=track.get("popularity", 0),
        spotify_id=track["id"],
        spotify_uri=track["uri"],
        external_url=track["external_urls"]["spotify"]
    )
```

### 平衡算法示例

```python
def balance_by_genre(songs: List[Song], target_size: int) -> List[Song]:
    """按流派平衡"""
    # 1. 统计流派分布
    genre_count = {}
    for song in songs:
        genre = song.genre or "未知"
        genre_count[genre] = genre_count.get(genre, 0) + 1
    
    # 2. 计算每个流派应该选多少首
    num_genres = len(genre_count)
    songs_per_genre = target_size // num_genres
    
    # 3. 从每个流派选择歌曲
    selected = []
    for genre, count in genre_count.items():
        genre_songs = [s for s in songs if (s.genre or "未知") == genre]
        selected.extend(genre_songs[:songs_per_genre])
    
    # 4. 如果还不够，随机补充
    if len(selected) < target_size:
        remaining = [s for s in songs if s not in selected]
        selected.extend(remaining[:target_size - len(selected)])
    
    return selected[:target_size]
```

## 🧪 测试

### 单元测试示例

```python
# tests/test_mcp_adapter.py
import pytest
from tools.mcp_adapter import MCPClientAdapter

@pytest.mark.asyncio
async def test_search_tracks():
    adapter = MCPClientAdapter()
    results = await adapter.search_tracks("周杰伦", limit=5)
    assert len(results) > 0
    assert all(hasattr(song, 'title') for song in results)
```

### 集成测试示例

```python
# tests/test_playlist_creation.py
@pytest.mark.asyncio
async def test_create_playlist_workflow():
    agent = MusicRecommendationAgent()
    result = await agent.get_recommendations("给我推荐一个运动歌单")
    
    assert result["success"]
    assert result["playlist"] is not None
    assert "spotify.com" in result["playlist"]["url"]
```

## 📚 参考资源

- [MCP 文档](https://docs.anthropic.com/mcp)
- [Spotify API 文档](https://developer.spotify.com/documentation/web-api)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)

## ❓ 常见问题

**Q: MCP 服务器如何与 Agent 通信？**

A: 有两种方式：
1. 直接导入函数（开发阶段，简单快速）
2. 通过 MCP 协议（生产环境，更规范）

**Q: 如何处理 Spotify API 限制？**

A: 实现缓存和请求合并，避免频繁调用。

**Q: 用户偏好如何持久化？**

A: 可以存储在数据库或文件中，每次请求时加载。

## 🎯 下一步

完成 Step 1 后，继续 Step 2，逐步实现所有功能。

遇到问题？查看：
- [架构设计文档](./PLAYLIST_RECOMMENDATION_ARCHITECTURE.md)
- [架构图](./ARCHITECTURE_DIAGRAM.md)

