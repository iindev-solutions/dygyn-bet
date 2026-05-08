import { api } from './client'
import type { ApiUser } from './types'

export function getMe(options: { skipTelegramInit?: boolean } = {}) {
  return api<{ user: ApiUser }>('/me', { skipTelegramInit: options.skipTelegramInit })
}
