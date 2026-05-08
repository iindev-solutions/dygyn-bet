import { api } from './client'
import type { ApiUser } from './types'

export function adminWebLogin(username: string, password: string) {
  return api<{ ok: boolean; user: ApiUser }>('/admin/web-login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
    skipTelegramInit: true,
  })
}

export function adminWebLogout() {
  return api<{ ok: boolean }>('/admin/web-logout', {
    method: 'POST',
    skipTelegramInit: true,
  })
}
