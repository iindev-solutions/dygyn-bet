import { computed, onMounted, onUnmounted, shallowRef, toValue, type MaybeRefOrGetter } from 'vue'

const SECOND_MS = 1000
const MINUTE_MS = SECOND_MS * 60
const HOUR_MS = MINUTE_MS * 60
const DAY_MS = HOUR_MS * 24

export interface CountdownPart {
  label: string
  value: string
}

export function useCountdown(targetIso: MaybeRefOrGetter<string | undefined>) {
  const now = shallowRef(Date.now())
  let timer: number | undefined

  const targetTime = computed(() => {
    const value = toValue(targetIso)
    if (!value) return null
    const time = Date.parse(value)
    return Number.isNaN(time) ? null : time
  })

  const remainingMs = computed(() => {
    if (targetTime.value === null) return null
    return Math.max(0, targetTime.value - now.value)
  })

  const isElapsed = computed(() => remainingMs.value === 0 && targetTime.value !== null)

  const parts = computed<CountdownPart[]>(() => {
    const ms = remainingMs.value
    if (ms === null) return []
    const days = Math.floor(ms / DAY_MS)
    const hours = Math.floor((ms % DAY_MS) / HOUR_MS)
    const minutes = Math.floor((ms % HOUR_MS) / MINUTE_MS)
    return [
      { label: 'дней', value: String(days).padStart(2, '0') },
      { label: 'часов', value: String(hours).padStart(2, '0') },
      { label: 'мин', value: String(minutes).padStart(2, '0') },
    ]
  })

  onMounted(() => {
    timer = window.setInterval(() => {
      now.value = Date.now()
    }, MINUTE_MS)
  })

  onUnmounted(() => {
    if (timer !== undefined) window.clearInterval(timer)
  })

  return { isElapsed, parts, remainingMs }
}
