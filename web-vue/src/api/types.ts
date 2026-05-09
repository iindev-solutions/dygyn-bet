export interface ApiUser {
  id: number
  telegram_id: number
  first_name?: string
  last_name?: string
  username?: string
  language_code?: string
  score?: number
  is_admin: boolean
}

export interface EventTotals {
  picks?: number
  points?: number
}

export interface Participant {
  id: number
  name: string
  region?: string
  city_or_village?: string
  bio?: string
  avatar_url?: string
  short_description?: string
  qualification_route?: string
  strengths?: string
  previous_dygyn_note?: string
  source_url?: string
  social_url?: string
  social_links?: Array<string | { url?: string }>
  pick_count?: number
  confidence_sum?: number
  confidence_points?: number
  summary?: PlayerSummary
}

export interface PickItem {
  player_id: number
  confidence_points: number
}

export interface EventResult {
  player_id?: number
  player_name: string
  place: number
  score?: string | number | null
}

export interface LiveStanding {
  day_number: number
  player_id?: number
  participant_id?: number
  player_name: string
  place: number
  total_points?: number | null
  is_winner?: boolean
  status?: string
}

export interface LiveDisciplineResult {
  day_number: number
  discipline_id: string
  discipline_name: string
  player_id?: number
  participant_id?: number
  player_name: string
  result_text?: string | null
  result_value?: number | null
  result_unit?: string | null
  place?: number | null
  points?: number | null
  status?: string
}

export interface LiveResults {
  standings?: LiveStanding[]
  discipline_results?: LiveDisciplineResult[]
  last_updated_at?: string | null
}

export interface EventSummary {
  id: number
  title: string
  starts_at: string
  description?: string
  status: 'draft' | 'open' | 'locked' | 'settled' | string
  participant_count?: number
  pick_count?: number
  totals?: EventTotals
}

export interface EventDetail extends EventSummary {
  participants: Participant[]
  my_picks?: PickItem[]
  results?: EventResult[]
  live_results?: LiveResults | null
}

export interface Discipline {
  discipline_id: string
  name_ru: string
  name_yakut?: string
  sort_order?: number
}

export interface PlayerSummary {
  history_count?: number
  wins?: number
  podiums?: number
}

export interface PlayerHistoryItem {
  year: number
  competition: string
  place?: number | null
  score?: string | number | null
  notes?: string | null
}

export interface DisciplineResult {
  year: number
  event_title: string
  discipline_id: string
  discipline_name?: string
  name_yakut?: string
  result_text?: string | null
  result_value?: number | null
  result_unit?: string | null
  place?: number | null
  points?: number | null
  overall_rank?: number | null
  overall_points?: number | null
}

export interface PlayerDetail extends Participant {
  history?: PlayerHistoryItem[]
  discipline_results?: DisciplineResult[]
}

export interface LeaderboardUser {
  telegram_id: number
  first_name?: string
  last_name?: string
  username?: string
  picks: number
  correct?: number
  score: number
}

export interface PredictionPayload {
  items: Array<{ participant_id: number; confidence_points: number }>
}

export interface DisciplineResultPayload {
  day_number: number
  participant_id: number
  discipline_id: string
  result_text: string
  result_value: number | null
  result_unit: string
  place: number | null
  points: number | null
  status: string
  notes: string
}

export interface StandingPayload {
  day_number: number
  participant_id: number
  place: number
  total_points: number | null
  is_winner: boolean
  status: string
  notes: string
}

export interface AnalyticsEventPayload {
  event_name:
    | 'app_open'
    | 'rating_open'
    | 'rules_open'
    | 'participant_detail_open'
    | 'vote_save'
    | 'png_share'
  anonymous_id: string
  path: string
  metadata?: Record<string, string | number | boolean | null>
}

export interface AnalyticsDailyRow {
  day: string
  count: number
  unique_count: number
  events: Record<string, number>
}

export interface AnalyticsEventTotal {
  event_name: string
  count: number
  unique_count: number
}

export interface AnalyticsTopPath {
  path: string
  count: number
}

export interface AnalyticsSummary {
  days: number
  since: string
  generated_at: string
  daily: AnalyticsDailyRow[]
  events: AnalyticsEventTotal[]
  top_paths: AnalyticsTopPath[]
}
