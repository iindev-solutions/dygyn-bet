export {}

declare global {
  interface Window {
    Telegram?: {
      WebApp?: TelegramWebApp
    }
  }

  interface TelegramWebApp {
    initData: string
    initDataUnsafe?: {
      user?: {
        id?: number
        first_name?: string
        last_name?: string
        username?: string
        language_code?: string
      }
    }
    ready: () => void
    expand: () => void
    close?: () => void
    BackButton?: {
      show: () => void
      hide: () => void
      onClick: (callback: () => void) => void
      offClick: (callback: () => void) => void
    }
    HapticFeedback?: {
      notificationOccurred?: (type: 'error' | 'success' | 'warning') => void
      impactOccurred?: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void
      selectionChanged?: () => void
    }
  }
}
