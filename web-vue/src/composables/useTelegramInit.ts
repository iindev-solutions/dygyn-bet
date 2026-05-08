import { readonly, ref, shallowRef } from 'vue'

const webApp = shallowRef<TelegramWebApp | null>(null)
const initData = ref('')
const ready = ref(false)
const waiting = ref(false)
const error = ref<string | null>(null)

let initPromise: Promise<TelegramWebApp | null> | null = null
let initialized = false
let lastMissAt = 0

interface InitOptions {
  timeoutMs?: number
  intervalMs?: number
}

function currentWebApp(): TelegramWebApp | null {
  if (typeof window === 'undefined') return null
  return window.Telegram?.WebApp ?? null
}

function waitForWebApp(timeoutMs: number, intervalMs: number): Promise<TelegramWebApp | null> {
  const existing = currentWebApp()
  if (existing) return Promise.resolve(existing)

  return new Promise((resolve) => {
    const startedAt = Date.now()
    const timer = window.setInterval(() => {
      const app = currentWebApp()
      if (app) {
        window.clearInterval(timer)
        resolve(app)
        return
      }
      if (Date.now() - startedAt >= timeoutMs) {
        window.clearInterval(timer)
        resolve(null)
      }
    }, intervalMs)
  })
}

export async function ensureTelegramInit(
  options: InitOptions = {},
): Promise<TelegramWebApp | null> {
  const timeoutMs = options.timeoutMs ?? 1800
  const intervalMs = options.intervalMs ?? 25

  if (initialized) return webApp.value
  if (!currentWebApp() && lastMissAt && Date.now() - lastMissAt < 5000) return null
  if (initPromise) return initPromise

  waiting.value = true
  error.value = null
  initPromise = (async () => {
    const app = await waitForWebApp(timeoutMs, intervalMs)
    if (!app) {
      lastMissAt = Date.now()
      initPromise = null
      return null
    }

    try {
      app.ready()
      app.expand()
      webApp.value = app
      initData.value = app.initData || ''
      ready.value = true
      initialized = true
      return app
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Telegram init failed'
      error.value = message
      initPromise = null
      return null
    }
  })().finally(() => {
    waiting.value = false
  })

  return initPromise
}

export function getTelegramInitData(): string {
  return initData.value || currentWebApp()?.initData || ''
}

export function getTelegramWebApp(): TelegramWebApp | null {
  return webApp.value || currentWebApp()
}

export function useTelegramInit() {
  return {
    webApp: readonly(webApp),
    initData: readonly(initData),
    ready: readonly(ready),
    waiting: readonly(waiting),
    error: readonly(error),
    init: ensureTelegramInit,
  }
}
