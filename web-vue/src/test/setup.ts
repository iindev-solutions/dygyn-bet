import { vi } from 'vitest'

Object.defineProperty(window, 'Telegram', {
  value: undefined,
  writable: true,
})

Object.defineProperty(window.navigator, 'share', {
  value: vi.fn(),
  writable: true,
})
