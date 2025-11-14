import Link from 'next/link';

export default function Home() {
  return (
    <main style={{ padding: '2rem', minHeight: '100vh', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginTop: '4rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>音乐推荐 Agent</h1>
        <p style={{ fontSize: '1.2rem', color: '#666', marginBottom: '3rem' }}>
          用自然语言和 AI 获取个性化音乐推荐
        </p>
        
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link
            href="/recommendations"
            style={{
              padding: '1rem 2rem',
              fontSize: '1.1rem',
              backgroundColor: '#0070f3',
              color: 'white',
              borderRadius: '8px',
              textDecoration: 'none',
              display: 'inline-block',
              transition: 'background-color 0.2s',
            }}
          >
            智能推荐
          </Link>
          <Link
            href="/search"
            style={{
              padding: '1rem 2rem',
              fontSize: '1.1rem',
              backgroundColor: '#333',
              color: 'white',
              borderRadius: '8px',
              textDecoration: 'none',
              display: 'inline-block',
              transition: 'background-color 0.2s',
            }}
          >
            音乐搜索
          </Link>
        </div>
      </div>
    </main>
  );
}

