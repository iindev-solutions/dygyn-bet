import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { getEvent, listEvents, savePrediction } from '@/api/events'
import type { EventDetail, EventSummary, Participant, PickItem } from '@/api/types'
import { evenAllocation, MAX_PICKS, TOTAL_CONFIDENCE_POINTS } from '@/utils/display'

export const useEventsStore = defineStore('events', () => {
  const events = ref<EventSummary[]>([])
  const selectedEvent = ref<EventDetail | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const draftAllocationsByEvent = ref<Record<number, Record<number, number>>>({})

  const draftAllocations = computed(() => {
    const event = selectedEvent.value
    if (!event) return {}
    return draftAllocationsByEvent.value[event.id] || allocationsFromPicks(event.my_picks || [])
  })
  const draftPlayerIds = computed(() => Object.keys(draftAllocations.value).map(Number))
  const allocationTotal = computed(() =>
    Object.values(draftAllocations.value).reduce((sum, points) => sum + Number(points || 0), 0),
  )
  const isValidAllocation = computed(
    () => draftPlayerIds.value.length > 0 && allocationTotal.value === TOTAL_CONFIDENCE_POINTS,
  )

  function allocationsFromPicks(picks: PickItem[]): Record<number, number> {
    return Object.fromEntries(
      picks.map((pick) => [Number(pick.player_id), Number(pick.confidence_points || 0)]),
    ) as Record<number, number>
  }

  function participantById(playerId: number, event = selectedEvent.value): Participant | undefined {
    return event?.participants?.find((participant) => Number(participant.id) === Number(playerId))
  }

  function pickedParticipants(event = selectedEvent.value): Participant[] {
    if (!event) return []
    const allocations =
      draftAllocationsByEvent.value[event.id] || allocationsFromPicks(event.my_picks || [])
    return Object.keys(allocations)
      .map(Number)
      .map((id) => {
        const participant = participantById(id, event)
        if (!participant) return null
        return { ...participant, confidence_points: allocations[id] || 0 }
      })
      .filter((participant): participant is Participant => Boolean(participant))
  }

  function pickedSummaries(event = selectedEvent.value): string[] {
    if (!event) return []
    const allocations =
      draftAllocationsByEvent.value[event.id] || allocationsFromPicks(event.my_picks || [])
    return Object.keys(allocations).map((id) => {
      const participant = participantById(Number(id), event)
      return `${participant?.name || id} — ${allocations[Number(id)]} очков`
    })
  }

  async function loadEvents() {
    loading.value = true
    try {
      const data = await listEvents()
      events.value = data.events
      const selectedId = selectedEvent.value?.id
      const nextEvent =
        events.value.find((event) => Number(event.id) === Number(selectedId)) ||
        events.value.find((event) => event.status === 'open') ||
        events.value[0]
      if (nextEvent) await loadEvent(nextEvent.id)
    } finally {
      loading.value = false
    }
  }

  async function loadEvent(eventId: number) {
    const data = await getEvent(Number(eventId))
    selectedEvent.value = data.event
    draftAllocationsByEvent.value[data.event.id] = allocationsFromPicks(data.event.my_picks || [])
  }

  function setDraftAllocations(eventId: number, allocations: Record<number, number>) {
    draftAllocationsByEvent.value = {
      ...draftAllocationsByEvent.value,
      [eventId]: allocations,
    }
  }

  function toggleDraftPick(playerId: number): 'ok' | 'max' | 'empty' {
    const event = selectedEvent.value
    if (!event) return 'empty'
    const picks = [...draftPlayerIds.value]
    const index = picks.indexOf(playerId)
    if (index >= 0) {
      picks.splice(index, 1)
    } else {
      if (picks.length >= MAX_PICKS) return 'max'
      picks.push(playerId)
    }
    setDraftAllocations(event.id, evenAllocation(picks))
    return 'ok'
  }

  function setDraftAllocation(playerId: number, points: number) {
    const event = selectedEvent.value
    if (!event) return
    const allocations = { ...draftAllocations.value }
    allocations[playerId] = Math.max(1, Math.min(TOTAL_CONFIDENCE_POINTS, Number(points || 1)))
    setDraftAllocations(event.id, allocations)
  }

  function rebalanceDraftAllocations() {
    const event = selectedEvent.value
    if (!event) return
    setDraftAllocations(event.id, evenAllocation(draftPlayerIds.value))
  }

  function applyAllocationPreset(preset: string) {
    const event = selectedEvent.value
    if (!event) return
    const ids = draftPlayerIds.value
    if (!ids.length) return
    const parts = String(preset || '')
      .split('/')
      .map(Number)
    if (parts.length !== ids.length || parts.some((points) => !Number.isFinite(points))) return
    setDraftAllocations(
      event.id,
      Object.fromEntries(ids.map((playerId, index) => [playerId, parts[index] || 0])) as Record<
        number,
        number
      >,
    )
  }

  async function saveCurrentPrediction() {
    const event = selectedEvent.value
    if (!event || !isValidAllocation.value) return null
    saving.value = true
    try {
      const ids = draftPlayerIds.value
      const data = await savePrediction(event.id, {
        items: ids.map((participantId) => ({
          participant_id: participantId,
          confidence_points: draftAllocations.value[participantId] || 0,
        })),
      })
      selectedEvent.value = data.event
      draftAllocationsByEvent.value[data.event.id] = allocationsFromPicks(data.event.my_picks || [])
      await loadEvents()
      return data.event
    } finally {
      saving.value = false
    }
  }

  return {
    events,
    selectedEvent,
    loading,
    saving,
    draftAllocations,
    draftPlayerIds,
    allocationTotal,
    isValidAllocation,
    loadEvents,
    loadEvent,
    toggleDraftPick,
    setDraftAllocation,
    rebalanceDraftAllocations,
    applyAllocationPreset,
    saveCurrentPrediction,
    participantById,
    pickedParticipants,
    pickedSummaries,
  }
})
