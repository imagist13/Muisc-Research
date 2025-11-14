'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { theme } from '@/styles/theme';

interface NavItemProps {
  href: string;
  label: string;
}

export default function NavItem({ href, label }: NavItemProps) {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <Link href={href}>
      <div
        style={{
          padding: '1rem 1.5rem',
          marginBottom: '0.5rem',
          borderRadius: theme.borderRadius.md,
          backgroundColor: isActive ? theme.colors.primary[500] : 'transparent',
          color: isActive ? '#ffffff' : theme.colors.text.primary,
          cursor: 'pointer',
          transition: 'all 0.2s',
          fontWeight: isActive ? 600 : 400,
        }}
        onMouseEnter={(e) => {
          if (!isActive) {
            e.currentTarget.style.backgroundColor = theme.colors.background.hover;
          }
        }}
        onMouseLeave={(e) => {
          if (!isActive) {
            e.currentTarget.style.backgroundColor = 'transparent';
          }
        }}
      >
        {label}
      </div>
    </Link>
  );
}

