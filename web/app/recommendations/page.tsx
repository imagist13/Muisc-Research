'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import WelcomeScreen from '@/components/Content/WelcomeScreen';
import ThinkingIndicator from '@/components/Content/ThinkingIndicator';
import ResultsDisplay from '@/components/Content/ResultsDisplay';
import { getMockRecommendations, mockDelay } from '@/lib/mockData';

export default function RecommendationsPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ response?: string; recommendations?: any[] } | null>(null);

  const handleSubmit = async (value: string) => {
    setLoading(true);
    setResult(null);

    try {
      // 模拟API延迟
      await mockDelay(1500);
      
      // 使用模拟数据
      const mockData = getMockRecommendations(value);
      setResult({
        response: mockData.response,
        recommendations: mockData.recommendations,
      });
    } catch (error) {
      setResult({
        response: '获取推荐失败，请稍后重试',
      });
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout
      onInputSubmit={handleSubmit}
      inputPlaceholder="例如：想运动，来点劲爆的"
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

