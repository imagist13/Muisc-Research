# 组件结构说明

## 项目结构

```
web/
├── app/                          # Next.js App Router 页面
│   ├── layout.tsx               # 根布局
│   ├── page.tsx                 # 首页
│   ├── recommendations/         # 音乐推荐页面
│   ├── search/                  # 歌曲搜索页面
│   └── playlist/                # 歌单创作页面
│
├── components/                  # React 组件
│   ├── Layout/                  # 布局组件
│   │   ├── MainLayout.tsx       # 主布局容器
│   │   └── Header.tsx           # 顶部栏（GitHub链接）
│   │
│   ├── Navigation/              # 导航组件
│   │   ├── Sidebar.tsx          # 左侧导航栏
│   │   └── NavItem.tsx          # 导航项
│   │
│   ├── Input/                   # 输入组件
│   │   ├── ChatInput.tsx        # 底部输入框
│   │   └── SendButton.tsx       # 发送按钮
│   │
│   └── Content/                 # 内容组件
│       ├── WelcomeScreen.tsx    # 欢迎界面（Logo圆圈）
│       ├── ThinkingIndicator.tsx # 思考中指示器
│       ├── ResultsDisplay.tsx   # 结果展示
│       └── SongCard.tsx         # 歌曲卡片
│
├── styles/                      # 样式配置
│   └── theme.ts                 # 绿色主题配置
│
├── lib/                         # 工具函数
│   └── api.ts                   # API 客户端
│
└── public/                      # 静态资源
```

## 组件说明

### Layout 组件

#### MainLayout
主布局容器，包含：
- 左侧导航栏
- 顶部 Header
- 内容区域
- 底部输入框（可选）

**Props:**
- `children`: ReactNode - 子内容
- `onInputSubmit?`: (value: string) => void - 输入提交回调
- `inputPlaceholder?`: string - 输入框占位符
- `inputDisabled?`: boolean - 输入框是否禁用

#### Header
顶部栏，显示 GitHub 链接。

### Navigation 组件

#### Sidebar
左侧固定导航栏，包含三个导航项：
- 音乐推荐
- 歌曲搜索
- 歌单创作

#### NavItem
导航项组件，支持：
- 路由高亮
- 悬停效果
- 点击跳转

### Input 组件

#### ChatInput
底部固定输入框，包含：
- 文本输入
- 发送按钮
- 表单验证

#### SendButton
圆形发送按钮，带悬停动画效果。

### Content 组件

#### WelcomeScreen
欢迎界面，显示：
- Logo 圆圈（音乐图标）
- 欢迎文字

#### ThinkingIndicator
思考中指示器，显示：
- "思考与网络搜索" 文字
- 动画点效果

#### ResultsDisplay
结果展示组件，支持：
- 文本响应展示
- 歌曲列表展示

#### SongCard
歌曲卡片，显示：
- 歌曲标题和艺术家
- 流派和情绪标签
- 推荐理由

## 主题配置

所有颜色和样式配置在 `styles/theme.ts` 中，使用绿色主题：
- 主绿色：`#10b981`
- 深绿色：`#059669`
- 浅绿色：`#d1fae5`
- 背景色：`#f0fdf4`

## 使用示例

```tsx
import MainLayout from '@/components/Layout/MainLayout';
import WelcomeScreen from '@/components/Content/WelcomeScreen';

export default function Page() {
  return (
    <MainLayout>
      <WelcomeScreen />
    </MainLayout>
  );
}
```

