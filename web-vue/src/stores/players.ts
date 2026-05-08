import { defineStore } from 'pinia'
import { ref } from 'vue'

import { getPlayer, listPlayers } from '@/api/players'
import type { Participant, PlayerDetail } from '@/api/types'

export const usePlayersStore = defineStore('players', () => {
  const players = ref<Participant[]>([])
  const selectedPlayer = ref<PlayerDetail | null>(null)
  const loading = ref(false)

  async function loadPlayers(force = false) {
    if (players.value.length && !force) return players.value
    loading.value = true
    try {
      const data = await listPlayers()
      players.value = data.players
      selectedPlayer.value = null
      return data.players
    } finally {
      loading.value = false
    }
  }

  async function loadPlayer(playerId: number) {
    loading.value = true
    try {
      const data = await getPlayer(playerId)
      selectedPlayer.value = data.player
      return data.player
    } finally {
      loading.value = false
    }
  }

  function clearSelectedPlayer() {
    selectedPlayer.value = null
  }

  return { players, selectedPlayer, loading, loadPlayers, loadPlayer, clearSelectedPlayer }
})
