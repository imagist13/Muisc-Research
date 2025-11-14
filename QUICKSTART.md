# SSE流式数据流 - 快速启动指南

## 概述

已完成前后端SSE流式数据流的设计和实现，支持实时流式输出和渲染。

## 已实现的功能

✅ FastAPI后端服务器，支持SSE流式输出  
✅ Next.js API路由作为SSE代理  
✅ 前端组件支持流式渲染  
✅ 实时状态更新（思考、处理中、完成）  
✅ 错误处理和连接管理  

## 快速开始

### 1. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 2. 启动后端服务器

```bash
# 方式1: 使用启动脚本
python api/start_server.py

# 方式2: 直接使用uvicorn
uvicorn api.server:app --host 0.0.0.0 --port 8501 --reload
```

后端将在 http://localhost:8501 启动

### 3. 启动前端

```bash
cd web
npm install  # 如果还没安装依赖
npm run dev
```

前端将在 http://localhost:3000 启动

### 4. 测试流式推荐

1. 打开浏览器访问：http://localhost:3000/recommendations
2. 输入查询："想运动，来点劲爆的"
3. 观察流式输出效果：
   - 思考指示器显示处理状态
   - 响应文本逐词流式显示
   - 歌曲逐个添加到列表

## 数据流路径

```
用户输入
  ↓
前端组件 (recommendations/page.tsx)
  ↓
API客户端 (lib/api.ts) - streamRecommendations()
  ↓
Next.js API路由 (app/api/recommendations/stream/route.ts)
  ↓
FastAPI后端 (api/server.py) - stream_recommendations()
  ↓
Music Agent (music_agent.py)
  ↓
SSE流式输出
  ↓
前端实时渲染
```

## 关键文件

### 后端
- `api/server.py` - FastAPI服务器主文件
- `api/start_server.py` - 启动脚本
- `services/playlist_service.py` - 歌单服务（已支持流式）

### 前端
- `web/lib/api.ts` - API客户端，包含SSE流式处理
- `web/app/api/recommendations/stream/route.ts` - Next.js API路由
- `web/app/recommendations/page.tsx` - 推荐页面（已更新为流式）
- `web/components/Content/ThinkingIndicator.tsx` - 思考指示器（支持动态消息）

## SSE事件类型

| 事件 | 说明 |
|------|------|
| `start` | 开始处理 |
| `thinking` | 思考/处理中 |
| `response` | 响应文本（流式） |
| `song` | 单个歌曲 |
| `complete` | 完成 |
| `error` | 错误 |

## 环境变量

确保设置了必要的环境变量：

```bash
export SILICONFLOW_API_KEY="your-api-key"
export API_PORT=8501  # 可选
```

或在 `setting.json` 中配置。

## 测试API

### 使用curl测试

```bash
curl -X POST http://localhost:8501/api/recommendations/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "想运动，来点劲爆的"}' \
  --no-buffer
```

### 使用浏览器测试

访问 http://localhost:8501/docs 查看Swagger UI文档

## 故障排查

### 1. 后端无法启动

- 检查Python版本（需要3.8+）
- 检查依赖是否安装完整
- 检查环境变量是否正确设置

### 2. 前端无法连接后端

- 检查后端是否运行在8501端口
- 检查CORS配置
- 检查`NEXT_PUBLIC_API_URL`环境变量

### 3. SSE流式输出不工作

- 检查浏览器控制台是否有错误
- 检查网络请求是否正常
- 检查后端日志

## 下一步

1. 优化流式输出速度
2. 添加更多状态指示
3. 实现重连机制
4. 添加进度条
5. 优化错误处理

## 相关文档

- `SSE_DATAFLOW.md` - 详细的数据流设计文档
- `api/README.md` - API服务器文档

