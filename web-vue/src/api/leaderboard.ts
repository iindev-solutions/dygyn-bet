import { api } from './client'
import type { LeaderboardUser } from './types'

export function getLeaderboard() {
  return api<{ leaderboard: LeaderboardUser[] }>('/leaderboard')
}
