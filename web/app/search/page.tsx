'use client';

import { useState } from 'react';
import { searchMusic } from '@/lib/api';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [genre, setGenre] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResults([]);

    try {
      const response = await searchMusic(query, genre || undefined);
      setResults(response.results || []);
    } catch (error) {
      console.error(error);
      alert('搜索失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1>音乐搜索</h1>
      <form onSubmit={handleSubmit} style={{ marginTop: '2rem' }}>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="query" style={{ display: 'block', marginBottom: '0.5rem' }}>
            搜索关键词：
          </label>
          <input
            id="query"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="例如：周杰伦"
            style={{
              width: '100%',
              padding: '0.75rem',
              fontSize: '1rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
            }}
            required
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="genre" style={{ display: 'block', marginBottom: '0.5rem' }}>
            流派（可选）：
          </label>
          <input
            id="genre"
            type="text"
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            placeholder="例如：流行"
            style={{
              width: '100%',
              padding: '0.75rem',
              fontSize: '1rem',
              border: '1px solid #ccc',
              borderRadius: '4px',
            }}
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '0.75rem 1.5rem',
            fontSize: '1rem',
            backgroundColor: '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? '搜索中...' : '搜索'}
        </button>
      </form>

      {results.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h2>搜索结果：</h2>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {results.map((song, index) => (
              <li
                key={index}
                style={{
                  padding: '1rem',
                  marginBottom: '0.5rem',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '4px',
                }}
              >
                <strong>{song.title}</strong> - {song.artist}
                {song.genre && <span style={{ marginLeft: '1rem', color: '#666' }}>{song.genre}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

