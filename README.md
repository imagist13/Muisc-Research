<p align="center">
  <img src="assets/logo.png" alt="Music Recommendation Agent logo" width="140">
</p>

<h1 align="center">音乐推荐 Agent</h1>

<p align="center">
  用自然语言和 AI 获取个性化音乐推荐。
</p>

---

## Highlights

- 🎯 智能理解心情、场景、流派等需求，一键生成推荐歌单
- 🔍 集成搜索、推荐与解释，让你知道每首歌的推荐理由
- ⚙️ 基于 LangGraph + Streamlit，轻量部署即可运行
- 🔐 支持自定义 LLM（DeepSeek、Qwen 等）与本地音乐数据

## 项目概览

音乐推荐 Agent 是一个面向内容创作者与音乐爱好者的 AI 助手。通过自然语言对话即可完成：

- 心情或场景驱动的歌单生成
- 特定歌手、流派的音乐探索
- 推荐背后逻辑的透明解释
- 面向下一步集成的 API 化扩展接口

项目默认使用硅基流动提供的 DeepSeek / Qwen 模型，也可接入其他 OpenAI 风格的 LLM 服务。


## Quick Start

### 环境要求

- Python 3.8+
- pip / uv / poetry 等任意包管理工具
- 可选：GPU 环境以加速本地推理

### 安装

```bash
git clone <your-repo-url>
cd deep-search
pip install -r requirements.txt
```

### 配置密钥

```json
{
  "SILICONFLOW_API_KEY": "",
  "SILICONFLOW_BASE_URL": "https://api.siliconflow.cn/v1",
  "SILICONFLOW_CHAT_MODEL": "Qwen/Qwen2.5-72B-Instruct",
  "TAILYAPI_API_KEY": "",
  "TAILYAPI_BASE_URL": "https://api.tavily.com",
  "APP_NAME": "DeepSearch Quickstart",
  "SPOTIFY_CLIENT_ID": "",
  "SPOTIFY_CLIENT_SECRET": ""
}
```

> 提示：也可通过环境变量 `SILICONFLOW_API_KEY` 等方式配置，无需 `setting.json`。

### 本地运行

```bash
python run_music_app.py
```

访问 `http://localhost:8501` 即可体验 Web 界面。  
如需使用 Streamlit 自带命令，替换为：

```bash
streamlit run music_app.py
```

### 快速部署建议

- Docker 化部署：在项目根目录创建 Dockerfile，复制代码并执行 `streamlit run`
- 云端部署：使用 Streamlit Community Cloud、Railway、Render 等平台，配置环境变量即可上线
- 内部使用：可在企业 VPN 或内网环境中运行，结合 Nginx/Gunicorn 做反向代理

## 配置说明

- `SILICONFLOW_API_KEY`：硅基流动平台获取的 API Key
- `SILICONFLOW_BASE_URL`：硅基流动 API 路径，默认为 `https://api.siliconflow.cn/v1`
- `SILICONFLOW_CHAT_MODEL`：对话模型，例如 `deepseek-ai/DeepSeek-V3`


如需接入更多第三方服务，只需在 `setting.json` 中新增字段，并在 `config/settings_loader.py` 中读取。

## 使用指南

### Web 界面

1. 打开浏览器访问 `http://localhost:8501`
2. 在“智能推荐”页输入需求（心情、场景、歌手等）
3. 在“音乐搜索”页按关键字过滤本地音乐库
4. 查看侧边栏快捷按钮，快速测试预设场景

### Python API

```python
import asyncio
from music_agent import MusicRecommendationAgent

async def main():
    agent = MusicRecommendationAgent()

    result = await agent.get_recommendations("想运动，来点劲爆的")
    print(result["response"])

    search_result = await agent.search_music("周杰伦", genre="流行")
    for song in search_result["results"]:
        print(song["title"], song["artist"])

asyncio.run(main())
```

### 二次开发建议

- 对接真实音乐 API：扩展 `tools/music_tools.py`，替换本地 JSON 数据源
- 自定义提示词：修改 `prompts/music_prompts.py` 以调整 AI 语气与输出结构
- 新增意图类型：在 `schemas/music_state.py` 中添加枚举，在工作流中增加节点

## Screenshots

<p align="center">
  <img src="assets/首页.png" alt="应用首页界面" width="260">
  <img src="assets/搜素音乐.png" alt="搜索音乐界面" width="260">
  <img src="assets/推荐说明.png" alt="推荐说明界面" width="260">
</p>

## MCP 工具集

- `mcp/music_server_updated_2025.py`：封装 `search_tracks`、`get_recommendations`、`create_playlist`、`analyze_playlist` 等工具，直接调用 Spotify API（基于 Spotipy）。
- `mcp/siliconflow_server.py`：可选的 MCP 服务，用于与 SiliconFlow API 协同。
- `mcp/ARCHITECTURE_DIAGRAM.md`：系统架构示意，展示从 LangGraph 工作流到 MCP 再到 Spotify 的链路。
- `mcp/csv_to_json.py`、`mcp/analyze_songs.py`：辅助数据处理脚本，可生成/分析本地歌单。
- `mcp/verify_config.py`、`verify_spotify_config.py`：用于诊断凭证与网络状态。

> 想要单独运行 MCP 服务器，可在 `mcp/` 下安装 `requirements.txt` 后执行 `python music_server_updated_2025.py`，再在主项目中通过 `tools.mcp_adapter` 调用。

## 架构一览

```
用户请求
  └─▶ 意图识别 (analyze_intent)
        └─▶ 条件路由 (route_by_intent)
                ├─▶ search_songs           → 推荐解释
                ├─▶ generate_recommendations → 推荐解释
                └─▶ general_chat
                      ↓
                  最终响应
```

- **LangGraph 工作流**：基于有向图节点管理不同任务
- **音乐工具层**：负责搜索、相似度匹配、心情标签解析
- **LLM 层**：负责自然语言理解与推荐解释生成
- **Streamlit 前端**：展示推荐结果、可视化推荐理由

## 技术栈

- LangGraph：工作流编排
- LangChain：LLM 能力封装
- Streamlit：交互式 Web 界面
- Pydantic：数据校验与状态管理
- asyncio：异步调度，提高响应效率

## 数据与扩展

- 示例数据存储在 `data/music_database.json`
- 音乐条目字段包含标题、艺术家、流派、情绪标签、推荐理由等
- 未来可对接 Spotify、网易云、Apple Music 等真实数据源
- 支持嵌入模型，将用户喜好与历史行为写入向量数据库

## 测试与验证

- `python test_config.py`：确认 `setting.json` 加载成功、环境变量写入正确、SiliconFlow 模型可用。
- `python test_music_mcp.py`：在配置好 Spotify 凭证后运行，逐项验证搜索、心情/活动推荐与 LangGraph 智能体链路。
- Streamlit UI 内置系统状态面板，可实时检查 API Key、最近推荐、MCP 运行情况。

> 建议在首次部署或更换凭证后先跑通以上脚本，确保外部依赖可用。

## Repository Map

```
deep search/
├── music_agent.py          # 智能推荐核心
├── music_app.py            # Streamlit 前端
├── run_music_app.py        # 启动脚本
├── config/                 # 配置加载
├── graphs/                 # LangGraph 工作流
├── tools/                  # 推荐与搜索工具
└── data/music_database.json# 示例音乐数据
```

## Roadmap

- [ ] 对接 Spotify / 网易云音乐 API，实现实时乐库
- [ ] 支持用户登录与偏好记忆
- [ ] 在线播放 & 歌单分享功能
- [ ] 推荐算法优化（协同过滤、向量检索）
- [ ] 多语言界面与推荐说明

## Contributing

欢迎以 Issue / PR 的形式提交需求或改进建议：

- Fork 本仓库并创建新分支
- 遵循已有代码风格，尽量补充测试或示例
- 在 PR 中说明变更背景与验证方式

## License

MIT License
