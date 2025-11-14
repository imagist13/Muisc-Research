'use client';

import { useState, FormEvent } from 'react';
import SendButton from './SendButton';
import { theme } from '@/styles/theme';

interface ChatInputProps {
  onSubmit: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export default function ChatInput({
  onSubmit,
  placeholder = '输入你的问题...',
  disabled = false,
}: ChatInputProps) {
  const [value, setValue] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (value.trim() && !disabled) {
      onSubmit(value.trim());
      setValue('');
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        position: 'fixed',
        bottom: 0,
        left: '200px',
        right: 0,
        padding: '2rem 2.5rem',
        backgroundColor: theme.colors.background.card,
        borderTop: `1px solid ${theme.colors.border.default}`,
        display: 'flex',
        gap: '1.25rem',
        alignItems: 'center',
      }}
    >
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        style={{
          flex: 1,
          padding: '1rem 1.25rem',
          fontSize: '1.0625rem',
          minHeight: '52px',
          border: `1px solid ${theme.colors.border.default}`,
          borderRadius: theme.borderRadius.md,
          backgroundColor: theme.colors.background.main,
          color: theme.colors.text.primary,
          outline: 'none',
          transition: 'border-color 0.2s',
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = theme.colors.border.focus;
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = theme.colors.border.default;
        }}
      />
      <SendButton
        onClick={(e) => {
          e.preventDefault();
          if (value.trim() && !disabled) {
            onSubmit(value.trim());
            setValue('');
          }
        }}
        disabled={disabled || !value.trim()}
      />
    </form>
  );
}

