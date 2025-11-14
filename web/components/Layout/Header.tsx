'use client';

import { theme } from '@/styles/theme';

export default function Header() {
  return (
    <header
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        padding: '1rem 2rem',
        zIndex: 100,
      }}
    >
      <a
        href="https://github.com"
        target="_blank"
        rel="noopener noreferrer"
        style={{
          color: theme.colors.text.secondary,
          fontSize: '0.875rem',
          textDecoration: 'none',
          transition: 'color 0.2s',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.color = theme.colors.primary[600];
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.color = theme.colors.text.secondary;
        }}
      >
        GitHub 地址
      </a>
    </header>
  );
}

