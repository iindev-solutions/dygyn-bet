import type {
  DisciplineResult,
  EventDetail,
  Participant,
  PlayerDetail,
  PlayerHistoryItem,
} from '@/api/types'

export const MAX_PICKS = 2
export const TOTAL_CONFIDENCE_POINTS = 100

export function formatDate(iso?: string): string {
  if (!iso) return ''
  try {
    return new Intl.DateTimeFormat('ru-RU', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

export function statusLabel(status?: string): string {
  const labels: Record<string, string> = {
    draft: 'черновик',
    open: 'открыто',
    locked: 'закрыто',
    settled: 'итоги',
  }
  return status ? labels[status] || status : ''
}

export function initials(name?: string): string {
  return String(name || '?')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0] || '')
    .join('')
    .toUpperCase()
}

export function getTotalPoints(event?: EventDetail | null): number {
  return Number(event?.totals?.points || 0)
}

export function supportPercent(
  event: EventDetail | null | undefined,
  participant: Participant,
): number {
  const totalPoints = getTotalPoints(event)
  const points = Number(participant.confidence_sum || 0)
  return totalPoints ? Math.round((points / totalPoints) * 100) : 0
}

export function topSupport(event: EventDetail | null | undefined, limit = 3): Participant[] {
  if (!event?.participants?.length) return []
  return [...event.participants]
    .sort((a, b) => Number(b.confidence_sum || 0) - Number(a.confidence_sum || 0))
    .slice(0, limit)
}

export function evenAllocation(playerIds: number[]): Record<number, number> {
  if (!playerIds.length) return {}
  const points = Math.floor(TOTAL_CONFIDENCE_POINTS / playerIds.length)
  return Object.fromEntries(playerIds.map((id) => [id, points])) as Record<number, number>
}

export function playerOrigin(player: Participant | PlayerDetail): string {
  const region = player.region || ''
  const place = player.city_or_village || ''
  if (region && place && region !== place) return `${region} · ${place}`
  return region || place || 'регион не указан'
}

export function visibleHistoryNote(item: PlayerHistoryItem): string {
  const note = String(item.notes || '').trim()
  return note.startsWith('[import:') ? '' : note
}

export function pluralRu(count: number, one: string, few: string, many: string): string {
  const n = Math.abs(Number(count || 0))
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return one
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return few
  return many
}

export function playerBadges(player: PlayerDetail): string[] {
  const summary = player.summary || {}
  const historyCount = Number(summary.history_count || 0)
  const wins = Number(summary.wins || 0)
  const podiums = Number(summary.podiums || 0)
  const note = `${player.previous_dygyn_note || ''} ${player.short_description || ''}`.toLowerCase()
  const badges: string[] = []

  if (wins > 0 || /победител|чемпион/.test(note)) badges.push('Титульный участник')
  else if (podiums > 0 || /приз[её]р|серебр|бронз|2 место|3 место/.test(note)) {
    badges.push('Призёр Игр')
  }
  if (/дебют/.test(note)) badges.push('Дебют')
  if (historyCount > 0) {
    badges.push(
      `${historyCount} ${pluralRu(historyCount, 'выступление', 'выступления', 'выступлений')} в базе`,
    )
  }

  return badges
}

export interface DisciplineGroup {
  title: string
  rows: DisciplineResult[]
}

export function groupDisciplineResults(results: DisciplineResult[]): DisciplineGroup[] {
  const map = new Map<string, DisciplineResult[]>()
  for (const row of results) {
    const key = `${row.year} · ${row.event_title}`
    const rows = map.get(key) || []
    rows.push(row)
    map.set(key, rows)
  }
  return [...map.entries()].map(([title, rows]) => ({ title, rows }))
}

export function isPlaceOnlyResult(text: string | null | undefined): boolean {
  return /^\d+\s*место$/i.test(String(text || '').trim())
}

export function formatResultValue(row: DisciplineResult): string {
  const text = String(row.result_text || '').trim()
  if (text && !isPlaceOnlyResult(text)) {
    if (row.result_value !== null && row.result_value !== undefined && row.result_unit) {
      return `${row.result_value} ${row.result_unit}`.trim()
    }
    return text
  }
  if (row.result_value !== null && row.result_value !== undefined) {
    return `${row.result_value} ${row.result_unit || ''}`.trim()
  }
  return 'не опубликован'
}

export function overallResultSummary(rows: DisciplineResult[]): string {
  const row = rows.find((item) => item.overall_rank || item.overall_points)
  if (!row) return ''
  const rank = row.overall_rank ? `${row.overall_rank} место` : 'место не указано'
  const points =
    row.overall_points !== null && row.overall_points !== undefined
      ? ` · ${row.overall_points} очков`
      : ''
  return `Общий зачёт: ${rank}${points}`
}

export function numberOrNull(value: FormDataEntryValue | null): number | null {
  const text = String(value ?? '').trim()
  return text ? Number(text) : null
}
