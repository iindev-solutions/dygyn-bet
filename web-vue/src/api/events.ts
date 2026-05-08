import { api } from './client'
import type { EventDetail, EventSummary, PredictionPayload } from './types'

export function listEvents() {
  return api<{ events: EventSummary[] }>('/events')
}

export function getEvent(eventId: number) {
  return api<{ event: EventDetail }>(`/events/${eventId}`)
}

export function savePrediction(eventId: number, payload: PredictionPayload) {
  return api<{ event: EventDetail }>(`/events/${eventId}/prediction`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
