import { ensureTelegramInit, getTelegramInitData } from '@/composables/useTelegramInit'

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: unknown,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

type ApiOptions = RequestInit & { skipJsonContentType?: boolean }

function trimTrailingSlash(value: string): string {
  return value.replace(/\/$/, '')
}

const envApiBase = import.meta.env.VITE_API_BASE
const viteBase = import.meta.env.BASE_URL
const apiBase = trimTrailingSlash(envApiBase || `${viteBase}api`)

export function apiUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  return `${apiBase}${cleanPath}`
}

export async function api<T>(path: string, options: ApiOptions = {}): Promise<T> {
  await ensureTelegramInit({ timeoutMs: 1800 })

  const { skipJsonContentType, ...requestOptions } = options
  const headers = new Headers(requestOptions.headers)
  const isFormData = requestOptions.body instanceof FormData

  if (!isFormData && !skipJsonContentType) headers.set('Content-Type', 'application/json')

  const initData = getTelegramInitData()
  if (initData) headers.set('X-Telegram-Init-Data', initData)

  const response = await fetch(apiUrl(path), { ...requestOptions, headers })
  const json = await response.json().catch(() => null)

  if (!response.ok) {
    const message = typeof json?.detail === 'string' ? json.detail : `HTTP ${response.status}`
    throw new ApiError(message, response.status, json)
  }

  return json as T
}
