'use client';

import { ReactNode } from 'react';
import Header from './Header';
import Sidebar from '../Navigation/Sidebar';
import ChatInput from '../Input/ChatInput';
import { theme } from '@/styles/theme';

interface MainLayoutProps {
  children: ReactNode;
  onInputSubmit?: (value: string) => void;
  inputPlaceholder?: string;
  inputDisabled?: boolean;
}

export default function MainLayout({
  children,
  onInputSubmit,
  inputPlaceholder,
  inputDisabled = false,
}: MainLayoutProps) {
  return (
    <div
      style={{
        display: 'flex',
        minHeight: '100vh',
        backgroundColor: theme.colors.background.main,
      }}
    >
      <Sidebar />
      <div
        style={{
          marginLeft: '200px',
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          paddingBottom: onInputSubmit ? '120px' : 0,
        }}
      >
        <Header />
        <main
          style={{
            flex: 1,
            padding: '4rem 2rem 2rem',
            overflowY: 'auto',
          }}
        >
          {children}
        </main>
        {onInputSubmit && (
          <ChatInput
            onSubmit={onInputSubmit}
            placeholder={inputPlaceholder}
            disabled={inputDisabled}
          />
        )}
      </div>
    </div>
  );
}

