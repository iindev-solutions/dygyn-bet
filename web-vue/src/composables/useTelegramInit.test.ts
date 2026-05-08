import { describe, expect, it, vi } from 'vitest'

import { ensureTelegramInit, getTelegramInitData } from './useTelegramInit'

describe('useTelegramInit', () => {
  it('waits for a late Telegram WebApp object before auth requests need initData', async () => {
    vi.useFakeTimers()
    window.Telegram = undefined

    const promise = ensureTelegramInit({ timeoutMs: 1000, intervalMs: 10 })
    await vi.advanceTimersByTimeAsync(30)

    const ready = vi.fn()
    const expand = vi.fn()
    window.Telegram = {
      WebApp: {
        initData: 'signed-init-data',
        ready,
        expand,
      },
    }

    await vi.advanceTimersByTimeAsync(10)
    const app = await promise

    expect(app).toBe(window.Telegram.WebApp)
    expect(ready).toHaveBeenCalledOnce()
    expect(expand).toHaveBeenCalledOnce()
    expect(getTelegramInitData()).toBe('signed-init-data')

    vi.useRealTimers()
  })
})
