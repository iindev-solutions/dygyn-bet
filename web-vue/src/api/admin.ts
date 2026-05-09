import { getAdminAnalytics } from './analytics'
import { api } from './client'
import type {
  AnalyticsSummary,
  Discipline,
  DisciplineResultPayload,
  EventDetail,
  StandingPayload,
} from './types'

export function listDisciplines() {
  return api<{ disciplines: Discipline[] }>('/disciplines')
}

export function saveDisciplineResult(eventId: number, payload: DisciplineResultPayload) {
  return api<{ results: unknown }>(`/admin/events/${eventId}/discipline-results`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function saveStanding(eventId: number, payload: StandingPayload) {
  return api<{ results: unknown }>(`/admin/events/${eventId}/standings`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function finishEvent(eventId: number, winnerParticipantId: number) {
  return api<{ event: EventDetail }>(`/admin/events/${eventId}/finish`, {
    method: 'POST',
    body: JSON.stringify({ winner_participant_id: winnerParticipantId }),
  })
}

export function loadAdminAnalytics(days = 14): Promise<{ analytics: AnalyticsSummary }> {
  return getAdminAnalytics(days)
}
