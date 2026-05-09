import { defineStore } from 'pinia'
import { ref } from 'vue'

import {
  finishEvent,
  listDisciplines,
  loadAdminAnalytics,
  saveDisciplineResult,
  saveStanding,
} from '@/api/admin'
import type {
  AnalyticsSummary,
  Discipline,
  DisciplineResultPayload,
  StandingPayload,
} from '@/api/types'

export const useAdminStore = defineStore('admin', () => {
  const disciplines = ref<Discipline[]>([])
  const analytics = ref<AnalyticsSummary | null>(null)
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

  async function loadAnalytics(days = 14) {
    const data = await loadAdminAnalytics(days)
    analytics.value = data.analytics
    return data.analytics
  }

  return {
    disciplines,
    analytics,
    loading,
    loadDisciplines,
    loadAnalytics,
    upsertDisciplineResult,
    upsertStanding,
    finish,
  }
})
