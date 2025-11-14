'use client';

import { theme } from '@/styles/theme';

export default function WelcomeScreen() {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        gap: '1.5rem',
      }}
    >
      <div
        style={{
          width: '120px',
          height: '120px',
          borderRadius: theme.borderRadius.full,
          backgroundColor: theme.colors.primary[100],
          border: `4px solid ${theme.colors.primary[300]}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: theme.shadows.lg,
        }}
      >
        <svg
          width="60"
          height="60"
          viewBox="0 0 24 24"
          fill="none"
          stroke={theme.colors.primary[600]}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M9 18V5l12-2v13"></path>
          <circle cx="6" cy="18" r="3"></circle>
          <circle cx="18" cy="16" r="3"></circle>
        </svg>
      </div>
      <p
        style={{
          color: theme.colors.text.secondary,
          fontSize: '1.125rem',
          textAlign: 'center',
        }}
      >
        用自然语言和 AI 获取个性化音乐推荐
      </p>
    </div>
  );
}

