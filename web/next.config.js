/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // 如果需要代理到后端 API
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8501/:path*', // 代理到 Streamlit 后端
      },
    ];
  },
  // 图片优化配置
  images: {
    domains: ['localhost'],
    unoptimized: process.env.NODE_ENV === 'development',
  },
};

module.exports = nextConfig;

