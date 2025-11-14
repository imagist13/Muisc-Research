import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '音乐推荐 Agent',
  description: '用自然语言和 AI 获取个性化音乐推荐',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body style={{ margin: 0, padding: 0 }}>{children}</body>
    </html>
  );
}

