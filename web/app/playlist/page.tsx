'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import WelcomeScreen from '@/components/Content/WelcomeScreen';
import ThinkingIndicator from '@/components/Content/ThinkingIndicator';
import ResultsDisplay from '@/components/Content/ResultsDisplay';

export default function PlaylistPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ response?: string; recommendations?: any[] } | null>(null);

  const handleSubmit = async (value: string) => {
    setLoading(true);
    setResult(null);

    try {
      // TODO: 实现歌单创作 API 调用
      // 暂时模拟响应
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setResult({
        response: `已为你创建歌单：${value}\n\n这个功能正在开发中，敬请期待！`,
      });
    } catch (error) {
      setResult({
        response: '创建歌单失败，请稍后重试',
      });
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout
      onInputSubmit={handleSubmit}
      inputPlaceholder="例如：创建一个适合运动的歌单"
      inputDisabled={loading}
    >
      {!result && !loading && <WelcomeScreen />}
      {loading && <ThinkingIndicator />}
      {result && (
        <ResultsDisplay
          response={result.response}
          songs={result.recommendations}
        />
      )}
    </MainLayout>
  );
}

