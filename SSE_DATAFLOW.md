# SSE流式数据流设计文档

## 概述

本文档描述了音乐推荐系统的前后端SSE（Server-Sent Events）流式数据流设计。

## 架构图

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  前端组件   │ ──────> │ Next.js API   │ ──────> │ FastAPI     │
│ (React)     │         │ Route (代理)  │         │ Server      │
└─────────────┘         └──────────────┘         └─────────────┘
     ▲                        │                        │
     │                        │                        │
     │                        │                        ▼
     │                        │                 ┌─────────────┐
     │                        │                 │ Music Agent │
     │                        │                 │ & Services  │
     │                        │                 └─────────────┘
     │                        │                        │
     └────────────────────────┴────────────────────────┘
                    SSE Stream (流式数据)
```

## 数据流详解

### 1. 前端发起请求

**位置**: `web/app/recommendations/page.tsx`

```typescript
const cancel = streamRecommendations(
  { query: value },
  (event: SSEEvent) => {
    // 处理SSE事件
  }
);
```

### 2. API客户端处理

**位置**: `web/lib/api.ts`

- 使用`fetch` API发起POST请求
- 读取`ReadableStream`响应体
- 解析SSE格式数据（`data: {...}\n\n`）
- 调用回调函数处理每个事件

### 3. Next.js API路由（代理）

**位置**: `web/app/api/recommendations/stream/route.ts`

- 接收前端请求
- 转发到FastAPI后端
- 透传流式响应

### 4. FastAPI后端处理

**位置**: `api/server.py`

- 接收请求参数
- 调用`MusicRecommendationAgent`或`PlaylistRecommendationService`
- 使用异步生成器流式输出结果
- 发送SSE格式事件

### 5. 服务层处理

**位置**: `services/playlist_service.py`, `music_agent.py`

- 执行实际的推荐逻辑
- 可以进一步拆分为多个步骤
- 每个步骤完成后发送事件

## SSE事件格式

### 标准格式

```
data: {"type": "event_type", "data": {...}}\n\n
```

### 事件类型

#### 1. 开始事件
```json
{
  "type": "start",
  "message": "开始分析你的需求..."
}
```

#### 2. 思考事件
```json
{
  "type": "thinking",
  "message": "正在理解你的音乐偏好..."
}
```

#### 3. 响应文本（流式）
```json
{
  "type": "response",
  "text": "根据你的需求，我为你推荐...",
  "is_complete": false
}
```

#### 4. 歌曲数据
```json
{
  "type": "song",
  "song": {
    "title": "歌曲名",
    "artist": "艺术家",
    "genre": "流派"
  },
  "index": 0,
  "total": 5
}
```

#### 5. 完成事件
```json
{
  "type": "complete",
  "success": true
}
```

#### 6. 错误事件
```json
{
  "type": "error",
  "error": "错误信息"
}
```

## 前端状态管理

### 状态变量

```typescript
const [loading, setLoading] = useState(false);
const [thinkingMessage, setThinkingMessage] = useState<string>('');
const [responseText, setResponseText] = useState<string>('');
const [songs, setSongs] = useState<any[]>([]);
const [error, setError] = useState<string | null>(null);
```

### 事件处理逻辑

```typescript
switch (event.type) {
  case 'start':
    setThinkingMessage(event.message);
    break;
  case 'thinking':
    setThinkingMessage(event.message);
    break;
  case 'response':
    setResponseText(event.text);
    if (event.is_complete) {
      setThinkingMessage('');
    }
    break;
  case 'song':
    setSongs(prev => [...prev, event.song]);
    break;
  case 'complete':
    setLoading(false);
    break;
  case 'error':
    setError(event.error);
    setLoading(false);
    break;
}
```

## 流式输出控制

### 后端控制

在`api/server.py`中，通过`asyncio.sleep()`控制输出速度：

```python
yield f"data: {json.dumps({...}, ensure_ascii=False)}\n\n"
await asyncio.sleep(0.05)  # 控制输出间隔
```

### 前端渲染

前端实时更新UI，实现打字机效果：

```typescript
case 'response':
  if (event.text) {
    setResponseText(event.text);  // 实时更新文本
  }
  break;
```

## 错误处理

### 连接错误

前端使用`AbortController`处理连接中断：

```typescript
const abortController = new AbortController();
// ...
return () => {
  if (abortController) {
    abortController.abort();
  }
};
```

### 数据解析错误

```typescript
try {
  const data = JSON.parse(line.slice(6));
  onEvent(data);
} catch (e) {
  console.error('Failed to parse SSE data:', e);
}
```

## 性能优化

### 1. 缓冲处理

前端使用缓冲区处理不完整的SSE数据：

```typescript
let buffer = '';
buffer += decoder.decode(value, { stream: true });
const lines = buffer.split('\n');
buffer = lines.pop() || '';  // 保留不完整的行
```

### 2. 去重处理

避免重复添加相同的歌曲：

```typescript
setSongs((prev) => {
  const exists = prev.some(
    (s) => s.title === event.song?.title && s.artist === event.song?.artist
  );
  if (exists) return prev;
  return [...prev, event.song];
});
```

## 使用示例

### 后端启动

```bash
python api/start_server.py
```

### 前端启动

```bash
cd web
npm run dev
```

### 测试流式推荐

1. 打开前端页面：http://localhost:3000/recommendations
2. 输入查询："想运动，来点劲爆的"
3. 观察流式输出效果

## 扩展点

### 1. 更细粒度的步骤

可以在服务层拆分更多步骤，例如：
- 分析意图
- 搜索歌曲
- 生成推荐
- 平衡歌单

### 2. 进度指示

添加进度百分比：

```json
{
  "type": "progress",
  "current": 3,
  "total": 10,
  "percentage": 30
}
```

### 3. 取消支持

前端可以随时取消请求：

```typescript
const cancel = streamRecommendations(...);
// 稍后取消
cancel();
```

## 注意事项

1. **连接保持**: SSE连接需要保持打开，确保网络稳定
2. **编码格式**: 使用`ensure_ascii=False`支持中文
3. **CORS配置**: 确保后端CORS配置正确
4. **错误恢复**: 实现重连机制处理网络中断
5. **资源清理**: 组件卸载时清理SSE连接

## 相关文件

- `api/server.py` - FastAPI后端服务器
- `web/lib/api.ts` - 前端API客户端
- `web/app/api/recommendations/stream/route.ts` - Next.js API路由
- `web/app/recommendations/page.tsx` - 推荐页面组件
- `services/playlist_service.py` - 歌单服务

