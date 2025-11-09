# 🎵 音乐推荐Agent - 快速开始

## 📦 项目文件结构

```
音乐推荐Agent相关文件:
├── music_agent.py              # Agent主入口
├── music_app.py                # Streamlit Web界面
├── music_examples.py           # 使用示例代码
├── run_music_app.py            # 快速启动脚本
├── MUSIC_README.md             # 完整文档
├── MUSIC_QUICKSTART.md         # 本文件
├── graphs/
│   └── music_graph.py          # LangGraph工作流
├── schemas/
│   └── music_state.py          # 状态定义
├── tools/
│   └── music_tools.py          # 音乐工具
└── prompts/
    └── music_prompts.py        # 提示词模板
```

## ⚡ 5分钟快速体验

### 步骤1: 设置环境变量

Windows PowerShell:
```powershell
$env:SILICONFLOW_API_KEY = "your-siliconflow-api-key"
```

Windows CMD:
```cmd
set SILICONFLOW_API_KEY=your-siliconflow-api-key
```

Linux/Mac:
```bash
export SILICONFLOW_API_KEY="your-siliconflow-api-key"
```

### 步骤2: 启动Web界面

方法1 - 使用启动脚本（推荐）:
```bash
python run_music_app.py
```

方法2 - 直接启动:
```bash
streamlit run music_app.py
```

### 步骤3: 访问界面

打开浏览器访问: http://localhost:8501

## 🎮 Web界面使用

### 智能推荐页

1. **快捷按钮** (左侧边栏)
   - 😊 开心 - 推荐快乐音乐
   - 😢 悲伤 - 推荐伤感音乐
   - 🏃 运动 - 推荐运动音乐
   - 😌 放松 - 推荐舒缓音乐
   - 💼 工作 - 推荐工作音乐
   - 💤 睡觉 - 推荐助眠音乐

2. **自然语言输入**

输入示例：
```
我现在心情很好，想听点开心的音乐
推荐一些适合运动的歌曲
有没有类似《晴天》的歌曲
推荐周杰伦的经典歌曲
想听一些民谣风格的歌
```

### 音乐搜索页

- 输入歌曲名、艺术家或专辑
- 可选择流派筛选
- 点击搜索按钮

## 💻 Python API使用

### 基础示例

```python
import asyncio
from music_agent import MusicRecommendationAgent

async def main():
    # 创建Agent
    agent = MusicRecommendationAgent()
    
    # 智能推荐
    result = await agent.get_recommendations(
        "我现在心情很好，推荐一些开心的音乐"
    )
    print(result["response"])

asyncio.run(main())
```

### 搜索音乐

```python
# 搜索艺术家
result = await agent.search_music("周杰伦")

# 按流派搜索
result = await agent.search_music("", genre="民谣")
```

### 根据心情推荐

```python
result = await agent.get_recommendations_by_mood("开心", limit=5)

for rec in result["recommendations"]:
    song = rec["song"]
    print(f"{song['title']} - {song['artist']}")
    print(f"理由: {rec['reason']}")
```

### 根据活动场景推荐

```python
result = await agent.get_recommendations_by_activity("运动", limit=5)
```

### 获取相似歌曲

```python
result = await agent.get_similar_songs("晴天", "周杰伦", limit=5)
```

## 🎯 运行示例代码

### 运行所有示例

```bash
python music_examples.py
# 选择 1 - 运行所有示例
```

### 交互模式

```bash
python music_examples.py
# 选择 2 - 交互模式
```

在交互模式中，你可以：
- 输入任何音乐需求
- 与Agent自然对话
- 查看实时推荐结果

## 🎨 支持的功能

### ✅ 推荐类型

- ✓ 根据心情推荐
- ✓ 根据活动场景推荐
- ✓ 根据音乐流派推荐
- ✓ 根据艺术家推荐
- ✓ 相似歌曲推荐
- ✓ 智能对话推荐

### ✅ 支持的心情

开心、快乐、悲伤、伤心、放松、舒缓、激动、兴奋、怀旧、平静、浪漫

### ✅ 支持的场景

运动、健身、学习、工作、开车、睡觉、休息、派对、聚会

### ✅ 支持的流派

流行、摇滚、民谣、电子、说唱、抒情、古风、爵士

## 📝 常用命令

```bash
# 启动Web界面
python run_music_app.py

# 运行示例
python music_examples.py

# 测试Agent
python music_agent.py

# 查看日志
# 日志会输出到控制台
```

## 🔧 常见问题

### Q: API密钥如何获取？

A: 访问 [硅基流动官网](https://cloud.siliconflow.cn/) 注册并获取API密钥。

### Q: 启动失败怎么办？

A: 检查：
1. 是否设置了 `SILICONFLOW_API_KEY` 环境变量
2. 是否安装了所有依赖: `pip install -r requirements.txt`
3. Python版本是否 >= 3.9

### Q: 推荐结果为空？

A: 
1. 检查网络连接
2. 确认API密钥有效
3. 查看控制台日志了解详细错误

### Q: 如何添加更多歌曲？

A: 编辑 `tools/music_tools.py`，在 `_initialize_music_db()` 方法中添加更多 `Song` 对象。

## 🚀 下一步

1. **自定义数据** - 添加你喜欢的歌曲到数据库
2. **优化提示词** - 编辑 `prompts/music_prompts.py` 改进推荐效果
3. **对接API** - 连接真实音乐平台API（Spotify、网易云等）
4. **扩展功能** - 添加播放列表生成、用户偏好学习等功能

## 📚 完整文档

详细文档请查看: [MUSIC_README.md](MUSIC_README.md)

## 💡 使用技巧

1. **详细描述需求** - 越详细的描述，推荐越准确
   ```
   ❌ "推荐歌曲"
   ✅ "我现在在健身房锻炼，想听一些节奏感强的电子音乐"
   ```

2. **使用快捷按钮** - 快速获取常见场景推荐

3. **查看推荐理由** - 了解为什么推荐这些歌曲

4. **尝试不同场景** - 探索各种心情和场景的推荐

5. **保持对话** - 可以基于之前的推荐继续提问

## 🎵 示例对话

```
你: 我现在心情很好，想听点开心的音乐

助手: 根据你现在开心的心情，我为你精心挑选了这几首歌曲...
推荐: 
1. 告白气球 - 周杰伦 (流行)
2. Wake Me Up - Avicii (电子)
...

你: 有没有类似告白气球的歌？

助手: 当然！这些歌曲和《告白气球》风格相近...
```

## 📞 获取帮助

- 查看完整文档: `MUSIC_README.md`
- 运行示例代码: `python music_examples.py`
- 查看源代码注释

---

🎵 开始你的音乐之旅吧！

