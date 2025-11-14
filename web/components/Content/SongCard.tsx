'use client';

import { theme } from '@/styles/theme';

interface SongCardProps {
  title: string;
  artist: string;
  genre?: string;
  mood?: string;
  reason?: string;
}

export default function SongCard({ title, artist, genre, mood, reason }: SongCardProps) {
  return (
    <div
      style={{
        padding: '1.25rem',
        marginBottom: '1rem',
        backgroundColor: theme.colors.background.card,
        borderRadius: theme.borderRadius.md,
        border: `1px solid ${theme.colors.border.default}`,
        boxShadow: theme.shadows.sm,
        transition: 'all 0.2s',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = theme.shadows.md;
        e.currentTarget.style.transform = 'translateY(-2px)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = theme.shadows.sm;
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          marginBottom: '0.5rem',
        }}
      >
        <div
          style={{
            width: '40px',
            height: '40px',
            borderRadius: theme.borderRadius.md,
            backgroundColor: theme.colors.primary[100],
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke={theme.colors.primary[600]}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
        </div>
        <div style={{ flex: 1 }}>
          <h3
            style={{
              fontSize: '1.125rem',
              fontWeight: 600,
              color: theme.colors.text.primary,
              marginBottom: '0.25rem',
            }}
          >
            {title}
          </h3>
          <p
            style={{
              fontSize: '0.875rem',
              color: theme.colors.text.secondary,
            }}
          >
            {artist}
          </p>
        </div>
      </div>
      {(genre || mood) && (
        <div
          style={{
            display: 'flex',
            gap: '0.5rem',
            marginBottom: '0.75rem',
            flexWrap: 'wrap',
          }}
        >
          {genre && (
            <span
              style={{
                padding: '0.25rem 0.75rem',
                fontSize: '0.75rem',
                backgroundColor: theme.colors.primary[100],
                color: theme.colors.primary[700],
                borderRadius: theme.borderRadius.full,
              }}
            >
              {genre}
            </span>
          )}
          {mood && (
            <span
              style={{
                padding: '0.25rem 0.75rem',
                fontSize: '0.75rem',
                backgroundColor: theme.colors.primary[200],
                color: theme.colors.primary[700],
                borderRadius: theme.borderRadius.full,
              }}
            >
              {mood}
            </span>
          )}
        </div>
      )}
      {reason && (
        <p
          style={{
            fontSize: '0.875rem',
            color: theme.colors.text.muted,
            lineHeight: '1.5',
            marginTop: '0.5rem',
          }}
        >
          {reason}
        </p>
      )}
    </div>
  );
}

