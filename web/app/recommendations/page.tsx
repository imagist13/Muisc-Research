'use client';

import { useState, useEffect, useRef } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import WelcomeScreen from '@/components/Content/WelcomeScreen';
import ThinkingIndicator from '@/components/Content/ThinkingIndicator';
import ResultsDisplay from '@/components/Content/ResultsDisplay';
import { streamRecommendations, type SSEEvent } from '@/lib/api';

export default function RecommendationsPage() {
  const [loading, setLoading] = useState(false);
  const [thinkingMessage, setThinkingMessage] = useState<string>('');
  const [responseText, setResponseText] = useState<string>('');
  const [songs, setSongs] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const cancelRef = useRef<(() => void) | null>(null);

  const handleSubmit = async (value: string) => {
    // 重置状态
    setLoading(true);
    setThinkingMessage('');
    setResponseText('');
    setSongs([]);
    setError(null);

    // 取消之前的请求
    if (cancelRef.current) {
      cancelRef.current();
    }

    // 开始流式请求
    const cancel = streamRecommendations(
      { query: value },
      (event: SSEEvent) => {
        switch (event.type) {
          case 'start':
            setThinkingMessage(event.message || '开始分析你的需求...');
            break;

          case 'thinking':
            setThinkingMessage(event.message || '正在思考...');
            break;

          case 'response':
            if (event.text) {
              setResponseText(event.text);
              // 当响应完成时，隐藏思考指示器
              if (event.is_complete) {
                setThinkingMessage('');
              }
            }
            break;

          case 'recommendations_start':
            setThinkingMessage('正在获取推荐歌曲...');
            setSongs([]);
            break;

          case 'song':
            if (event.song) {
              setSongs((prev) => {
                // 避免重复添加
                const exists = prev.some(
                  (s) =>
                    s.title === event.song?.title &&
                    s.artist === event.song?.artist
                );
                if (exists) return prev;
                return [...prev, event.song];
              });
            }
            break;

          case 'recommendations_complete':
            setThinkingMessage('');
            break;

          case 'complete':
            setLoading(false);
            setThinkingMessage('');
            break;

          case 'error':
            setError(event.error || '发生未知错误');
            setLoading(false);
            setThinkingMessage('');
            break;

          default:
            break;
        }
      }
    );

    cancelRef.current = cancel;
  };

  // 清理函数
  useEffect(() => {
    return () => {
      if (cancelRef.current) {
        cancelRef.current();
      }
    };
  }, []);

  const hasResult = responseText || songs.length > 0;

  return (
    <MainLayout
      onInputSubmit={handleSubmit}
      inputPlaceholder="例如：想运动，来点劲爆的"
      inputDisabled={loading}
    >
      {!hasResult && !loading && !error && <WelcomeScreen />}
      {(loading || thinkingMessage) && (
        <ThinkingIndicator message={thinkingMessage} />
      )}
      {error && (
        <div
          style={{
            padding: '1rem',
            margin: '1rem',
            backgroundColor: '#fee2e2',
            color: '#991b1b',
            borderRadius: '0.5rem',
            border: '1px solid #fecaca',
          }}
        >
          {error}
        </div>
      )}
      {hasResult && (
        <ResultsDisplay response={responseText} songs={songs} />
      )}
    </MainLayout>
  );
}

