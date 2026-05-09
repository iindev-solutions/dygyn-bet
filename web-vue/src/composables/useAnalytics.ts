import { useRoute } from 'vue-router'

import { trackAnalyticsEvent } from '@/api/analytics'
import type { AnalyticsEventPayload } from '@/api/types'

const STORAGE_KEY = 'dygyn_analytics_id'

type AnalyticsEventName = AnalyticsEventPayload['event_name']
type AnalyticsMetadata = NonNullable<AnalyticsEventPayload['metadata']>

function randomId(): string {
  if (crypto.randomUUID) return crypto.randomUUID()
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`
}

function anonymousId(): string {
  try {
    const existing = localStorage.getItem(STORAGE_KEY)
    if (existing) return existing
    const next = randomId()
    localStorage.setItem(STORAGE_KEY, next)
    return next
  } catch {
    return randomId()
  }
}

export function useAnalytics() {
  const route = useRoute()

  function track(eventName: AnalyticsEventName, metadata: AnalyticsMetadata = {}) {
    void trackAnalyticsEvent({
      event_name: eventName,
      anonymous_id: anonymousId(),
      path: route.path,
      metadata,
    }).catch(() => {})
  }

  return { track }
}
