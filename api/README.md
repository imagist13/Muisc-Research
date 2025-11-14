# 音乐推荐API服务器

基于FastAPI的流式音乐推荐API服务器，支持SSE（Server-Sent Events）流式输出。

## 功能特性

- ✅ SSE流式输出推荐结果
- ✅ 实时状态更新（思考、处理中、完成）
- ✅ 支持音乐推荐和歌单生成
- ✅ CORS支持，可与前端无缝集成
- ✅ 自动API文档（Swagger UI）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

确保设置了必要的环境变量（或在`setting.json`中配置）：

```bash
export SILICONFLOW_API_KEY="your-api-key"
export API_PORT=8501  # 可选，默认8501
export API_HOST=0.0.0.0  # 可选，默认0.0.0.0
```

### 3. 启动服务器

```bash
# 方式1: 使用启动脚本
python api/start_server.py

# 方式2: 直接使用uvicorn
uvicorn api.server:app --host 0.0.0.0 --port 8501 --reload
```

### 4. 访问API文档

启动后访问：http://localhost:8501/docs

## API端点

### 流式推荐接口

**POST** `/api/recommendations/stream`

流式获取音乐推荐，使用SSE格式返回。

**请求体：**
```json
{
  "query": "想运动，来点劲爆的",
  "genre": "电子",
  "mood": "兴奋",
  "user_preferences": {}
}
```

**响应格式（SSE）：**
```
data: {"type": "start", "message": "开始分析你的需求..."}

data: {"type": "thinking", "message": "正在理解你的音乐偏好..."}

data: {"type": "response", "text": "根据你的需求...", "is_complete": false}

data: {"type": "song", "song": {...}, "index": 0, "total": 5}

data: {"type": "complete", "success": true}
```

### 流式歌单生成接口

**POST** `/api/playlist/stream`

流式生成智能歌单。

**请求体：**
```json
{
  "query": "适合早晨通勤的活力歌单",
  "target_size": 30,
  "create_spotify_playlist": false,
  "public": false,
  "user_preferences": {}
}
```

### 非流式接口（兼容）

- **POST** `/api/recommendations` - 获取推荐（非流式）
- **POST** `/api/playlist` - 生成歌单（非流式）

## SSE事件类型

| 事件类型 | 说明 |
|---------|------|
| `start` | 开始处理 |
| `thinking` | 思考/处理中 |
| `response` | 响应文本（流式输出） |
| `recommendations_start` | 开始获取推荐 |
| `song` | 单个歌曲数据 |
| `recommendations_complete` | 推荐完成 |
| `songs_start` | 开始获取歌曲列表 |
| `songs_complete` | 歌曲列表完成 |
| `context` | 上下文信息 |
| `seed_summary` | 种子摘要 |
| `playlist` | 播放列表信息 |
| `complete` | 全部完成 |
| `error` | 错误信息 |

## 前端集成

前端使用`fetch` API读取SSE流：

```typescript
const response = await fetch('/api/recommendations/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: '...' }),
});

const reader = response.body?.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const text = decoder.decode(value);
  // 解析SSE数据
  const lines = text.split('\n');
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      // 处理事件
    }
  }
}
```

## 开发

### 代码结构

```
api/
├── server.py          # FastAPI主服务器
├── start_server.py    # 启动脚本
└── README.md         # 本文档
```

### 调试

启用详细日志：

```bash
uvicorn api.server:app --log-level debug
```

## 注意事项

1. SSE连接需要保持打开状态，确保前端正确处理连接关闭
2. 流式输出速度可通过`asyncio.sleep()`调整
3. 生产环境建议使用反向代理（如Nginx）处理SSE连接
4. 确保CORS配置正确，允许前端域名访问

