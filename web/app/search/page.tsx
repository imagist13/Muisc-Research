'use client';

import { useState } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import WelcomeScreen from '@/components/Content/WelcomeScreen';
import ThinkingIndicator from '@/components/Content/ThinkingIndicator';
import ResultsDisplay from '@/components/Content/ResultsDisplay';
import { getMockSearchResults, mockDelay } from '@/lib/mockData';

export default function SearchPage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);

  const handleSubmit = async (value: string) => {
    setLoading(true);
    setResults([]);

    try {
      // 模拟API延迟
      await mockDelay(1200);
      
      // 简单解析：如果包含"流派"或"genre"，尝试提取
      const parts = value.split(/流派|genre/i);
      const query = parts[0].trim();
      const genre = parts[1]?.trim() || undefined;

      // 使用模拟数据
      const mockData = getMockSearchResults(query, genre);
      setResults(mockData.results || []);
    } catch (error) {
      console.error(error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout
      onInputSubmit={handleSubmit}
      inputPlaceholder="例如：周杰伦 或 周杰伦 流派：流行"
      inputDisabled={loading}
    >
      {results.length === 0 && !loading && <WelcomeScreen />}
      {loading && <ThinkingIndicator />}
      {results.length > 0 && (
        <ResultsDisplay songs={results} />
      )}
    </MainLayout>
  );
}

