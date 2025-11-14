# UI 设计方案

## 设计概述

基于手绘线框图，实现一个绿色主题的音乐推荐 Web 应用。

## 色彩方案

- **主色调**：绿色系
  - 主绿色：`#10b981` (emerald-500)
  - 深绿色：`#059669` (emerald-600)
  - 浅绿色：`#d1fae5` (emerald-100)
  - 背景色：`#f0fdf4` (green-50)
  - 文字色：`#064e3b` (emerald-900)

## 布局结构

```
┌─────────────────────────────────────────┐
│  [GitHub链接]                           │
│  ┌──────┐  ┌────────────────────────┐  │
│  │ 导航 │  │                        │  │
│  │ 菜单 │  │     内容区域           │  │
│  │      │  │   (Logo/结果展示)      │  │
│  │      │  │                        │  │
│  └──────┘  └────────────────────────┘  │
│            ┌────────────────────────┐  │
│            │   输入框 [发送按钮]    │  │
│            └────────────────────────┘  │
└─────────────────────────────────────────┘
```

## 组件结构

### 1. Layout 组件
- `components/Layout/MainLayout.tsx` - 主布局容器
- `components/Layout/Header.tsx` - 顶部栏（GitHub链接）

### 2. Navigation 组件
- `components/Navigation/Sidebar.tsx` - 左侧导航栏
- `components/Navigation/NavItem.tsx` - 导航项

### 3. Input 组件
- `components/Input/ChatInput.tsx` - 底部输入框
- `components/Input/SendButton.tsx` - 发送按钮

### 4. Content 组件
- `components/Content/WelcomeScreen.tsx` - 欢迎界面（Logo圆圈）
- `components/Content/ThinkingIndicator.tsx` - 思考中指示器
- `components/Content/ResultsDisplay.tsx` - 结果展示
- `components/Content/SongCard.tsx` - 歌曲卡片

### 5. 主题配置
- `styles/theme.ts` - 主题颜色配置
- `styles/globals.css` - 全局样式（绿色主题）

## 交互流程

1. **初始状态**：显示欢迎界面（Logo圆圈）
2. **用户输入**：在底部输入框输入问题
3. **处理中**：显示"思考与网络搜索"指示器
4. **结果展示**：显示推荐结果或搜索结果

## 响应式设计

- 移动端：导航栏可折叠
- 桌面端：固定左侧导航栏
- 输入框：始终固定在底部

