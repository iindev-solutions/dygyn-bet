import { api } from './client'
import type { ApiUser } from './types'

export function getMe() {
  return api<{ user: ApiUser }>('/me')
}
