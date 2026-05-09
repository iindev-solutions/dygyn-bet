import { api } from './client'
import type { AnalyticsEventPayload, AnalyticsSummary } from './types'

export function trackAnalyticsEvent(payload: AnalyticsEventPayload) {
  return api<{ ok: boolean }>('/analytics', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getAdminAnalytics(days = 14) {
  return api<{ analytics: AnalyticsSummary }>(`/admin/analytics?days=${days}`)
}
