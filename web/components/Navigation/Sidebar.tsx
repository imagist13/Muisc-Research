'use client';

import NavItem from './NavItem';
import { theme } from '@/styles/theme';

const navItems = [
  { href: '/recommendations', label: '音乐推荐' },
  { href: '/search', label: '歌曲搜索' },
  { href: '/playlist', label: '歌单创作' },
];

export default function Sidebar() {
  return (
    <aside
      style={{
        position: 'fixed',
        left: 0,
        top: 0,
        width: '200px',
        height: '100vh',
        backgroundColor: theme.colors.background.card,
        borderRight: `1px solid ${theme.colors.border.default}`,
        padding: '4rem 1rem 1rem',
        overflowY: 'auto',
      }}
    >
      <nav>
        {navItems.map((item) => (
          <NavItem key={item.href} href={item.href} label={item.label} />
        ))}
      </nav>
    </aside>
  );
}

