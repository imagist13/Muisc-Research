'use client';

import { theme } from '@/styles/theme';
import SongCard from './SongCard';

interface Song {
  title: string;
  artist: string;
  genre?: string;
  mood?: string;
  reason?: string;
}

interface ResultsDisplayProps {
  response?: string;
  songs?: Song[];
}

export default function ResultsDisplay({ response, songs }: ResultsDisplayProps) {
  return (
    <div
      style={{
        padding: '1.5rem',
      }}
    >
      {response && (
        <div
          style={{
            padding: '1.25rem',
            marginBottom: '1.5rem',
            backgroundColor: theme.colors.background.card,
            borderRadius: theme.borderRadius.md,
            border: `1px solid ${theme.colors.border.default}`,
            boxShadow: theme.shadows.sm,
          }}
        >
          <p
            style={{
              color: theme.colors.text.primary,
              lineHeight: '1.75',
              whiteSpace: 'pre-wrap',
            }}
          >
            {response}
          </p>
        </div>
      )}

      {songs && songs.length > 0 && (
        <div>
          <h2
            style={{
              fontSize: '1.25rem',
              fontWeight: 600,
              color: theme.colors.text.primary,
              marginBottom: '1rem',
            }}
          >
            推荐歌曲
          </h2>
          {songs.map((song, index) => (
            <SongCard key={index} {...song} />
          ))}
        </div>
      )}
    </div>
  );
}

