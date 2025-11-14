# 音乐推荐 Web 前端

基于 Next.js 14 构建的音乐推荐系统前端应用。

## 技术栈

- **Next.js 14** - React 框架
- **TypeScript** - 类型安全
- **App Router** - Next.js 最新路由系统

## 快速开始

### 安装依赖

```bash
npm install
# 或
yarn install
# 或
pnpm install
```

### 配置环境变量

复制 `.env.local.example` 为 `.env.local` 并配置：

```bash
cp .env.local.example .env.local
```

编辑 `.env.local` 文件，设置后端 API 地址。

### 开发模式

```bash
npm run dev
```

访问 [http://localhost:3000](http://localhost:3000) 查看应用。

### 构建生产版本

```bash
npm run build
npm start
```

## 项目结构

```
web/
├── app/                # Next.js App Router 目录
│   ├── layout.tsx     # 根布局
│   ├── page.tsx       # 首页
│   └── globals.css    # 全局样式
├── components/         # React 组件
├── lib/               # 工具函数和 API 客户端
├── public/            # 静态资源
├── next.config.js     # Next.js 配置
├── tsconfig.json      # TypeScript 配置
└── package.json       # 项目依赖
```

## 开发指南

### 添加新页面

在 `app/` 目录下创建新的文件夹和 `page.tsx` 文件即可。

### 添加组件

在 `components/` 目录下创建组件文件。

### API 调用

在 `lib/` 目录下创建 API 客户端函数，用于与后端通信。

## 与后端集成

当前配置会将 `/api/*` 路径代理到 `http://localhost:8501`（Streamlit 后端）。

如需修改代理地址，请编辑 `next.config.js` 中的 `rewrites` 配置。

