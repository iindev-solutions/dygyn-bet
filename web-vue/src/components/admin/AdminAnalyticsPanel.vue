<script setup lang="ts">
import { computed } from 'vue'

import type { AnalyticsSummary } from '@/api/types'

const props = defineProps<{
  analytics: AnalyticsSummary | null
}>()

const labels: Record<string, string> = {
  app_open: 'Открытия',
  rating_open: 'Рейтинг',
  rules_open: 'Правила',
  participant_detail_open: 'Карточки атлетов',
  vote_save: 'Сохранения голосов',
  png_share: 'PNG-карточки',
}

const eventTotals = computed(() => props.analytics?.events || [])
const dailyRows = computed(() => props.analytics?.daily || [])
const maxDailyCount = computed(() =>
  Math.max(1, ...dailyRows.value.map((row) => Number(row.count || 0))),
)
const totalEvents = computed(() =>
  eventTotals.value.reduce((sum, row) => sum + Number(row.count || 0), 0),
)
const uniqueVisitors = computed(() =>
  Math.max(0, ...dailyRows.value.map((row) => Number(row.unique_count || 0))),
)

function labelFor(eventName: string): string {
  return labels[eventName] || eventName
}

function dayLabel(value: string): string {
  const [, month, day] = value.split('-')
  return `${day}.${month}`
}
</script>

<template>
  <article class="card analytics-panel">
    <div class="row">
      <div>
        <h2>Аналитика</h2>
        <p class="muted">Без Telegram ID, username, IP и текста голосов.</p>
      </div>
      <span class="badge">{{ analytics?.days || 14 }} дней</span>
    </div>

    <div v-if="!analytics" class="empty">Загрузка аналитики...</div>
    <template v-else>
      <div class="analytics-kpis">
        <div class="stat-box-lite">
          <strong>{{ totalEvents }}</strong>
          <span>событий</span>
        </div>
        <div class="stat-box-lite">
          <strong>{{ uniqueVisitors }}</strong>
          <span>уник. за день max</span>
        </div>
        <div class="stat-box-lite">
          <strong>{{
            eventTotals.find((row) => row.event_name === 'vote_save')?.count || 0
          }}</strong>
          <span>голосов</span>
        </div>
      </div>

      <div class="analytics-chart" aria-label="События по дням">
        <div
          v-for="row in dailyRows"
          :key="row.day"
          class="analytics-bar"
          :style="{
            '--bar-height': `${Math.max(6, (Number(row.count || 0) / maxDailyCount) * 100)}%`,
          }"
        >
          <span class="analytics-bar__value">{{ row.count }}</span>
          <span class="analytics-bar__fill"></span>
          <small>{{ dayLabel(row.day) }}</small>
        </div>
      </div>

      <div class="analytics-grid">
        <div class="history-item">
          <h3>События</h3>
          <div v-for="row in eventTotals" :key="row.event_name" class="row analytics-row">
            <span>{{ labelFor(row.event_name) }}</span>
            <strong>{{ row.count }}</strong>
          </div>
          <p v-if="!eventTotals.length" class="muted">Пока пусто.</p>
        </div>
        <div class="history-item">
          <h3>Экраны</h3>
          <div v-for="row in analytics.top_paths" :key="row.path" class="row analytics-row">
            <span>{{ row.path }}</span>
            <strong>{{ row.count }}</strong>
          </div>
          <p v-if="!analytics.top_paths.length" class="muted">Пока пусто.</p>
        </div>
      </div>
    </template>
  </article>
</template>

<style scoped>
.analytics-panel {
  display: grid;
  gap: 14px;
}

.analytics-kpis,
.analytics-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.stat-box-lite {
  padding: 12px 10px;
  border: 1px solid var(--line);
  border-radius: 17px;
  background: rgba(255, 255, 255, 0.055);
}

.stat-box-lite strong {
  display: block;
  font-size: 24px;
  line-height: 1;
}

.stat-box-lite span {
  color: var(--hint);
  font-size: 12px;
  font-weight: 850;
}

.analytics-chart {
  display: grid;
  grid-template-columns: repeat(14, minmax(16px, 1fr));
  gap: 7px;
  align-items: end;
  min-height: 178px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: rgba(0, 0, 0, 0.17);
}

.analytics-bar {
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 6px;
  align-items: end;
  min-width: 0;
  height: 148px;
  color: var(--hint);
  font-size: 10px;
  text-align: center;
}

.analytics-bar__value {
  color: var(--text);
  font-weight: 850;
}

.analytics-bar__fill {
  display: block;
  width: 100%;
  height: var(--bar-height);
  min-height: 6px;
  border-radius: 999px 999px 6px 6px;
  background: linear-gradient(180deg, var(--accent-soft), var(--accent));
}

.analytics-row {
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 224, 161, 0.08);
}

.analytics-row:last-child {
  border-bottom: 0;
}

.analytics-row span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 420px) {
  .analytics-kpis,
  .analytics-grid {
    grid-template-columns: 1fr;
  }

  .analytics-chart {
    gap: 4px;
  }

  .analytics-bar small {
    writing-mode: vertical-rl;
  }
}
</style>
