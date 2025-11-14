'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import WelcomeScreen from '@/components/Content/WelcomeScreen';
import ThinkingIndicator from '@/components/Content/ThinkingIndicator';
import ResultsDisplay from '@/components/Content/ResultsDisplay';
import { getMockRecommendations, mockDelay } from '@/lib/mockData';

export default function PlaylistPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ response?: string; recommendations?: any[] } | null>(null);

  const handleSubmit = async (value: string) => {
    setLoading(true);
    setResult(null);

    try {
      // 模拟API延迟
      await mockDelay(1800);
      
      // 使用模拟数据创建歌单
      const mockData = getMockRecommendations(value);
      setResult({
        response: `已为你创建歌单：${value}\n\n${mockData.response}\n\n歌单已保存，你可以随时查看和编辑。`,
        recommendations: mockData.recommendations,
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

