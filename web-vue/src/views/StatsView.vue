<script setup lang="ts">
import { onMounted } from 'vue'

import { useEventsStore } from '@/stores/events'
import { useLeaderboardStore } from '@/stores/leaderboard'
import { supportPercent, topSupport } from '@/utils/display'

const eventsStore = useEventsStore()
const leaderboardStore = useLeaderboardStore()

onMounted(() => {
  leaderboardStore.loadLeaderboard()
})

function leaderName(user: {
  first_name?: string
  last_name?: string
  username?: string
  telegram_id: number
}): string {
  return (
    [user.first_name, user.last_name].filter(Boolean).join(' ') ||
    user.username ||
    String(user.telegram_id)
  )
}
</script>

<template>
  <div class="stack">
    <article v-if="eventsStore.selectedEvent" class="card">
      <h2>Статистика поддержки</h2>
      <div class="history">
        <template v-if="topSupport(eventsStore.selectedEvent, 10).length">
          <div
            v-for="(participant, index) in topSupport(eventsStore.selectedEvent, 10)"
            :key="participant.id"
            class="history-item"
          >
            <div class="row">
              <strong>{{ index + 1 }}. {{ participant.name }}</strong>
              <span class="percent"
                >{{ supportPercent(eventsStore.selectedEvent, participant) }}%</span
              >
            </div>
            <p class="muted">
              {{ participant.pick_count || 0 }} голосов ·
              {{ Number(participant.confidence_sum || 0) }} очков уверенности
            </p>
            <div class="progress">
              <span
                :style="{ width: `${supportPercent(eventsStore.selectedEvent, participant)}%` }"
              ></span>
            </div>
          </div>
        </template>
        <p v-else class="muted">Статистика появится после первых голосов.</p>
      </div>
    </article>

    <article class="card">
      <h2>Рейтинг болельщиков</h2>
      <div v-if="leaderboardStore.loading" class="empty">Загрузка рейтинга...</div>
      <div v-else class="history">
        <template v-if="leaderboardStore.leaderboard.length">
          <article
            v-for="(user, index) in leaderboardStore.leaderboard"
            :key="user.telegram_id"
            class="leader-row"
          >
            <span class="avatar">{{ index + 1 }}</span>
            <div>
              <strong>{{ leaderName(user) }}</strong>
              <p class="muted">{{ user.picks }} голосов · {{ user.correct || 0 }} верных</p>
            </div>
            <span class="badge">{{ user.score }} очков</span>
          </article>
        </template>
        <div v-else class="empty">Рейтинг появится после первых голосов.</div>
      </div>
    </article>
  </div>
</template>
