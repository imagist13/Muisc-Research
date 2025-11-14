'use client';

import { theme } from '@/styles/theme';

interface ThinkingIndicatorProps {
  message?: string;
}

export default function ThinkingIndicator({ message }: ThinkingIndicatorProps) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        padding: '1rem',
        marginBottom: '1rem',
      }}
    >
      <div
        style={{
          width: '12px',
          height: '12px',
          borderRadius: theme.borderRadius.full,
          backgroundColor: theme.colors.primary[500],
        }}
      />
      <span
        style={{
          color: theme.colors.text.secondary,
          fontSize: '0.875rem',
        }}
      >
        {message || '思考与网络搜索'}
      </span>
      <div
        style={{
          display: 'flex',
          gap: '4px',
          marginLeft: '0.5rem',
        }}
      >
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: '4px',
              height: '4px',
              borderRadius: theme.borderRadius.full,
              backgroundColor: theme.colors.primary[400],
              animation: `pulse 1.4s ease-in-out ${i * 0.2}s infinite`,
            }}
          />
        ))}
      </div>
      <style jsx>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 0.4;
            transform: scale(1);
          }
          50% {
            opacity: 1;
            transform: scale(1.2);
          }
        }
      `}</style>
    </div>
  );
}

