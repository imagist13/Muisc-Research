# 🎵 音乐推荐Agent

一个基于AI的智能音乐推荐系统，提供个性化的音乐推荐服务。

## ✨ 功能特色

### 🎼 核心功能

1. **智能推荐**
   - 根据心情推荐音乐（开心、悲伤、放松等）
   - 根据活动场景推荐（运动、学习、工作、睡觉等）
   - 根据音乐流派推荐
   - 根据喜欢的艺术家推荐
   - 相似歌曲推荐

2. **音乐搜索**
   - 按歌曲名搜索
   - 按艺术家搜索
   - 按流派筛选
   - 快速查找热门歌曲

3. **智能对话**
   - 自然语言交互
   - 音乐知识问答
   - 个性化聊天体验

## 🏗️ 架构设计

### 项目结构

```
music_agent/
├── music_agent.py              # Agent主入口
├── music_app.py                # Streamlit Web界面
├── graphs/
│   └── music_graph.py          # LangGraph工作流
├── schemas/
│   └── music_state.py          # 状态定义
├── tools/
│   └── music_tools.py          # 音乐工具（搜索、推荐引擎）
└── prompts/
    └── music_prompts.py        # LLM提示词模板
```

### 工作流设计

```
用户输入
    ↓
意图分析 (analyze_intent)
    ↓
条件路由 (route_by_intent)
    ├─→ 搜索歌曲 (search_songs) ──→ 生成解释 (generate_explanation)
    ├─→ 生成推荐 (generate_recommendations) ──→ 生成解释
    └─→ 通用聊天 (general_chat)
    ↓
返回结果
```

### 意图类型

- `search` - 搜索歌曲
- `recommend_by_mood` - 根据心情推荐
- `recommend_by_activity` - 根据活动场景推荐
- `recommend_by_genre` - 根据流派推荐
- `recommend_by_artist` - 根据艺术家推荐
- `recommend_by_favorites` - 根据喜欢的歌曲推荐
- `general_chat` - 通用聊天

## 🚀 快速开始

### 环境要求

- Python 3.9+
- 已安装项目依赖（见 `requirements.txt`）

### 环境变量配置

```bash
# 必需
export SILICONFLOW_API_KEY="your-siliconflow-api-key"

# 可选（用于embedding功能）
export DASH_SCOPE_API_KEY="your-dashscope-api-key"
```

### 运行Web界面

```bash
# 启动Streamlit应用
streamlit run music_app.py
```

访问 http://localhost:8501 即可使用Web界面。

### 命令行测试

```bash
# 运行测试脚本
python music_agent.py
```

## 📖 使用示例

### Python API调用

```python
import asyncio
from music_agent import MusicRecommendationAgent

async def main():
    # 创建Agent实例
    agent = MusicRecommendationAgent()
    
    # 示例1: 智能推荐
    result = await agent.get_recommendations(
        "我现在心情很好，推荐一些开心的音乐"
    )
    print(result["response"])
    
    # 示例2: 搜索音乐
    search_result = await agent.search_music("周杰伦", genre="流行")
    for song in search_result["results"]:
        print(f"{song['title']} - {song['artist']}")
    
    # 示例3: 根据心情推荐
    mood_result = await agent.get_recommendations_by_mood("放松")
    for rec in mood_result["recommendations"]:
        print(f"{rec['song']['title']}: {rec['reason']}")
    
    # 示例4: 获取相似歌曲
    similar_result = await agent.get_similar_songs("晴天", "周杰伦")
    for song in similar_result["similar_songs"]:
        print(f"{song['title']} - {song['artist']}")

asyncio.run(main())
```

### Web界面使用

1. **智能推荐页**：输入你的需求，获取个性化推荐
2. **音乐搜索页**：搜索特定歌曲或艺术家
3. **快捷按钮**：使用侧边栏的快捷按钮快速获取推荐

## 🎸 支持的音乐流派

- 流行 (Pop)
- 摇滚 (Rock)
- 民谣 (Folk)
- 电子 (Electronic)
- 说唱 (Hip-Hop)
- 抒情 (Ballad)
- 古风 (Chinese Ancient Style)
- 爵士 (Jazz)

## 💡 推荐示例

### 根据心情

```python
# 开心时
"我现在心情很好，想听点开心的音乐"

# 悲伤时
"推荐一些悲伤的音乐，想听听伤感的歌"

# 放松时
"想要放松一下，推荐一些舒缓的音乐"
```

### 根据场景

```python
# 运动时
"适合运动时听的音乐"

# 学习工作时
"推荐一些适合学习的背景音乐"

# 睡觉前
"推荐一些助眠音乐"
```

### 搜索和发现

```python
# 搜索艺术家
"搜索周杰伦的歌曲"

# 按流派搜索
"推荐一些好听的民谣"

# 相似歌曲
"有没有类似《晴天》的歌曲"
```

## 🔧 自定义扩展

### 添加音乐数据源

编辑 `tools/music_tools.py` 中的 `MusicSearchTool` 类：

```python
class MusicSearchTool:
    def _initialize_music_db(self) -> List[Song]:
        """初始化音乐数据库"""
        # 在这里添加更多歌曲数据
        return [
            Song("歌名", "艺术家", "专辑", "流派", 年份, 时长, 流行度),
            # ... 更多歌曲
        ]
```

### 对接真实音乐API

可以对接以下音乐平台API：

- **Spotify API** - 国际音乐数据
- **网易云音乐API** - 中文音乐数据
- **QQ音乐API** - 中文音乐数据

修改 `MusicSearchTool.search_songs()` 方法即可。

### 自定义推荐算法

编辑 `tools/music_tools.py` 中的 `MusicRecommenderEngine` 类：

```python
class MusicRecommenderEngine:
    async def recommend_by_mood(self, mood: str, limit: int = 5):
        # 实现你的推荐逻辑
        pass
```

### 添加新的推荐场景

1. 在 `prompts/music_prompts.py` 中添加新的提示词
2. 在 `graphs/music_graph.py` 中添加新的节点
3. 在 `music_agent.py` 中添加新的API方法

## 📊 数据结构

### Song（歌曲）

```python
@dataclass
class Song:
    title: str              # 歌曲名
    artist: str             # 艺术家
    album: Optional[str]    # 专辑
    genre: Optional[str]    # 流派
    year: Optional[int]     # 发行年份
    duration: Optional[int] # 时长（秒）
    popularity: Optional[int] # 流行度（0-100）
```

### MusicRecommendation（推荐）

```python
@dataclass
class MusicRecommendation:
    song: Song              # 歌曲对象
    reason: str             # 推荐理由
    similarity_score: float # 相似度分数（0-1）
```

## 🎯 推荐策略

### 心情映射

- **开心/快乐** → 流行、电子
- **悲伤/伤心** → 抒情、民谣
- **放松/舒缓** → 民谣、爵士
- **激动/兴奋** → 摇滚、电子
- **怀旧** → 经典、流行
- **平静** → 古风、民谣
- **浪漫** → 抒情、流行

### 场景映射

- **运动/健身** → 电子、摇滚
- **学习/工作** → 古风、爵士
- **开车** → 流行、摇滚
- **睡觉/休息** → 民谣、抒情
- **派对/聚会** → 电子、流行

## 🐛 常见问题

### Q: 如何添加更多歌曲数据？

A: 编辑 `tools/music_tools.py` 中的 `_initialize_music_db()` 方法，添加更多 `Song` 对象。

### Q: 推荐结果不准确怎么办？

A: 可以调整以下内容：
1. 优化 `prompts/music_prompts.py` 中的提示词
2. 改进 `MusicRecommenderEngine` 中的推荐算法
3. 增加更多音乐数据和标签

### Q: 如何对接真实音乐API？

A: 修改 `MusicSearchTool` 类中的搜索方法，将模拟数据库替换为真实API调用。

### Q: 支持播放音乐吗？

A: 当前版本仅提供推荐功能。要支持播放，需要：
1. 获取音乐平台的播放链接
2. 在前端添加音频播放器组件

## 🔮 未来规划

- [ ] 对接真实音乐API（Spotify、网易云等）
- [ ] 添加在线播放功能
- [ ] 用户偏好学习和个性化
- [ ] 歌单生成和管理
- [ ] 音乐风格深度分析
- [ ] 多语言支持
- [ ] 社交分享功能
- [ ] 推荐算法优化

## 📝 技术栈

- **LangGraph** - AI工作流编排
- **DeepSeek** - 大语言模型
- **Streamlit** - Web界面框架
- **Python** - 后端开发语言
- **asyncio** - 异步编程

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

💬 有问题或建议？随时联系我们！

🎵 享受音乐，享受生活！

