import { api } from './client'
import type { PlayerDetail, Participant } from './types'

export function listPlayers() {
  return api<{ players: Participant[] }>('/players')
}

export function getPlayer(playerId: number) {
  return api<{ player: PlayerDetail }>(`/players/${playerId}`)
}
