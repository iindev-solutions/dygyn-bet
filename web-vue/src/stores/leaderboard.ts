import { defineStore } from 'pinia'
import { ref } from 'vue'

import { getLeaderboard } from '@/api/leaderboard'
import type { LeaderboardUser } from '@/api/types'

export const useLeaderboardStore = defineStore('leaderboard', () => {
  const leaderboard = ref<LeaderboardUser[]>([])
  const loading = ref(false)

  async function loadLeaderboard() {
    loading.value = true
    try {
      const data = await getLeaderboard()
      leaderboard.value = data.leaderboard
    } finally {
      loading.value = false
    }
  }

  return { leaderboard, loading, loadLeaderboard }
})
