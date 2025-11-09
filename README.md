# 🎵 音乐推荐Agent

<div align="center">

**一个基于AI的智能音乐推荐系统，提供个性化的音乐推荐服务**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-green.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[快速开始](#-安装和配置) • [功能特性](#-功能特性) • [使用示例](#-使用方法) • [项目架构](#-项目架构)

</div>

---

> 🎶 **用自然语言和AI聊音乐，让推荐更懂你**  
> 基于 LangGraph 构建的智能音乐推荐系统，支持根据心情、场景、流派等多种维度进行个性化推荐。使用硅基流动 API（支持 DeepSeek、Qwen 等模型），提供直观的 Streamlit Web 界面。

### 🚀 快速体验

```bash
# 1. 克隆仓库
git clone <your-repo-url>
cd deep-search

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API 密钥（在 setting.json 中）
# 4. 启动应用
python run_music_app.py
```

### 💡 使用示例

- **心情推荐**: "我现在心情很好，推荐一些开心的音乐"
- **场景推荐**: "适合运动时听的音乐"
- **搜索歌曲**: "搜索周杰伦的歌曲"
- **流派推荐**: "推荐一些好听的民谣"

## ✨ 功能特性

- 🎯 **智能推荐**: 根据心情、场景、流派、艺术家等多种方式推荐音乐
- 🔍 **音乐搜索**: 快速搜索歌曲、艺术家和专辑
- 💬 **自然对话**: 像朋友一样和用户聊音乐，理解自然语言需求
- 🎼 **多维度推荐**: 支持心情推荐、场景推荐、相似歌曲推荐等
- 🔄 **工作流编排**: 基于LangGraph的智能工作流管理
- 🌐 **Web界面**: 基于Streamlit的直观Web界面

## 📁 项目架构

```
deep search/
├── config/                    # 配置管理
│   └── settings_loader.py    # 配置加载器（从setting.json读取）
├── llms/                      # LLM集成
│   ├── base.py               # LLM基类
│   └── siliconflow_llm.py    # 硅基流动LLM实现
├── schemas/                   # 数据模型
│   └── music_state.py        # 音乐状态定义
├── graphs/                    # 工作流图
│   └── music_graph.py        # 音乐推荐工作流图
├── prompts/                   # 提示词
│   └── music_prompts.py      # 音乐推荐提示词
├── tools/                     # 工具
│   └── music_tools.py         # 音乐工具（搜索、推荐引擎）
├── data/                      # 数据文件
│   └── music_database.json   # 音乐数据库
├── music_agent.py            # Agent主入口类
├── music_app.py              # Streamlit Web界面
├── run_music_app.py          # 快速启动脚本
├── setting.json              # 配置文件（API密钥等）
└── requirements.txt          # 依赖包
```

## 🚀 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置文件设置

创建 `setting.json` 文件并配置以下内容：

```json
{
  "SILICONFLOW_API_KEY": "your_siliconflow_api_key_here",
  "SILICONFLOW_BASE_URL": "https://api.siliconflow.cn/v1",
  "SILICONFLOW_CHAT_MODEL": "deepseek-ai/DeepSeek-V3",
  "DASH_SCOPE_API_KEY": "your_dashscope_api_key_here",
  "DASH_SCOPE_BASE_URL": "https://api.deepseek.com",
  "DASH_SCOPE_EMBEDDING_MODEL": "text-embedding-ada-002",
  "APP_NAME": "Music Recommendation Agent"
}
```

**支持的模型**：
- `deepseek-ai/DeepSeek-V3` (推荐)
- `Qwen/Qwen2.5-72B-Instruct`
- `Qwen/Qwen2.5-32B-Instruct`
- 其他硅基流动支持的模型

> 💡 **提示**: 也可以使用环境变量配置，但推荐使用 `setting.json` 文件。

### 3. 运行应用

**方式一：使用快速启动脚本（推荐）**

```bash
python run_music_app.py
```

**方式二：直接运行Streamlit**

```bash
streamlit run music_app.py
```

启动后访问 http://localhost:8501 即可使用Web界面。

## 📖 使用方法

### Web界面使用

启动应用后，你可以：

1. **智能推荐页**：输入你的需求，获取个性化推荐
   - "我现在心情很好，推荐一些开心的音乐"
   - "适合运动时听的音乐"
   - "推荐一些好听的民谣"

2. **音乐搜索页**：搜索特定歌曲或艺术家
   - "搜索周杰伦的歌曲"
   - "找一下《晴天》这首歌"

3. **快捷按钮**：使用侧边栏的快捷按钮快速获取推荐

### Python API使用

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

asyncio.run(main())
```

### 推荐示例

**根据心情**：
- "我现在心情很好，想听点开心的音乐"
- "推荐一些悲伤的音乐，想听听伤感的歌"
- "想要放松一下，推荐一些舒缓的音乐"

**根据场景**：
- "适合运动时听的音乐"
- "推荐一些适合学习的背景音乐"
- "推荐一些助眠音乐"

**搜索和发现**：
- "搜索周杰伦的歌曲"
- "推荐一些好听的民谣"
- "有没有类似《晴天》的歌曲"

## 🔄 工作流程

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

## 🛠️ 技术栈

- **LangGraph**: AI工作流编排
- **LangChain**: LLM应用框架
- **硅基流动 (SiliconFlow)**: 大语言模型服务（支持DeepSeek、Qwen等）
- **Streamlit**: Web界面框架
- **Python**: 后端开发语言
- **asyncio**: 异步编程
- **Pydantic**: 数据验证

## 🎸 支持的音乐流派

- 流行 (Pop)
- 摇滚 (Rock)
- 民谣 (Folk)
- 电子 (Electronic)
- 说唱 (Hip-Hop)
- 抒情 (Ballad)
- 古风 (Chinese Ancient Style)
- 爵士 (Jazz)

## ⚠️ 注意事项

1. **API密钥**: 需要有效的硅基流动API密钥（在 `setting.json` 中配置）
2. **模型选择**: 推荐使用 `deepseek-ai/DeepSeek-V3` 或 `Qwen/Qwen2.5-72B-Instruct`
3. **音乐数据**: 当前使用本地JSON文件存储音乐数据，位于 `data/music_database.json`
4. **扩展性**: 可以轻松对接真实音乐API（Spotify、网易云等）

## 🔮 未来规划

- [ ] 对接真实音乐API（Spotify、网易云等）
- [ ] 添加在线播放功能
- [ ] 用户偏好学习和个性化
- [ ] 歌单生成和管理
- [ ] 音乐风格深度分析
- [ ] 推荐算法优化

## 📚 相关文档

- [MUSIC_README.md](MUSIC_README.md) - 完整功能文档
- [MUSIC_QUICKSTART.md](MUSIC_QUICKSTART.md) - 快速开始指南
- [音乐推荐Agent总览.md](音乐推荐Agent总览.md) - 项目总览

## 许可证

MIT License
