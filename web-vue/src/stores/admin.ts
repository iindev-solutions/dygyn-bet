import { defineStore } from 'pinia'
import { ref } from 'vue'

import { finishEvent, listDisciplines, saveDisciplineResult, saveStanding } from '@/api/admin'
import type { Discipline, DisciplineResultPayload, StandingPayload } from '@/api/types'

export const useAdminStore = defineStore('admin', () => {
  const disciplines = ref<Discipline[]>([])
  const loading = ref(false)

  async function loadDisciplines() {
    if (disciplines.value.length) return disciplines.value
    loading.value = true
    try {
      const data = await listDisciplines()
      disciplines.value = data.disciplines
      return data.disciplines
    } finally {
      loading.value = false
    }
  }

  async function upsertDisciplineResult(eventId: number, payload: DisciplineResultPayload) {
    await saveDisciplineResult(eventId, payload)
  }

  async function upsertStanding(eventId: number, payload: StandingPayload) {
    await saveStanding(eventId, payload)
  }

  async function finish(eventId: number, winnerParticipantId: number) {
    return finishEvent(eventId, winnerParticipantId)
  }

  return { disciplines, loading, loadDisciplines, upsertDisciplineResult, upsertStanding, finish }
})
