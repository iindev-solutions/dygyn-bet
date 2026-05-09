<script setup lang="ts">
import { computed, onMounted } from 'vue'

import PlayerGridCard from '@/components/players/PlayerGridCard.vue'
import SocialIconLink from '@/components/players/SocialIconLink.vue'
import { useAnalytics } from '@/composables/useAnalytics'
import { useBackButton } from '@/composables/useBackButton'
import { usePlayersStore } from '@/stores/players'
import {
  formatDisciplineOutcome,
  formatResultValue,
  groupDisciplineResults,
  initials,
  overallResultSummary,
  playerBadges,
  playerOrigin,
  playerSocialUrl,
  visibleHistoryNote,
} from '@/utils/display'

const playersStore = usePlayersStore()
const analytics = useAnalytics()
const selectedPlayer = computed(() => playersStore.selectedPlayer)
const hasSelectedPlayer = computed(() => Boolean(selectedPlayer.value))
const disciplineGroups = computed(() =>
  selectedPlayer.value ? groupDisciplineResults(selectedPlayer.value.discipline_results || []) : [],
)
const badges = computed(() => (selectedPlayer.value ? playerBadges(selectedPlayer.value) : []))
const selectedSocialUrl = computed(() =>
  selectedPlayer.value ? playerSocialUrl(selectedPlayer.value) : '',
)

onMounted(() => {
  playersStore.loadPlayers()
})

useBackButton(hasSelectedPlayer, () => playersStore.clearSelectedPlayer())

async function openPlayer(playerId: number) {
  analytics.track('participant_detail_open', { participant_id: playerId })
  await playersStore.loadPlayer(playerId)
}
</script>

<template>
  <div class="stack">
    <template v-if="selectedPlayer">
      <article class="card player-detail">
        <button type="button" class="ghost" @click="playersStore.clearSelectedPlayer">
          ← Участники
        </button>
        <div class="profile-head">
          <img
            v-if="selectedPlayer.avatar_url"
            class="profile-photo"
            :src="selectedPlayer.avatar_url"
            :alt="selectedPlayer.name"
            loading="lazy"
          />
          <span v-else class="profile-photo avatar">{{ initials(selectedPlayer.name) }}</span>
          <div>
            <h2>{{ selectedPlayer.name }}</h2>
            <p class="muted">{{ playerOrigin(selectedPlayer) }}</p>
          </div>
        </div>

        <div v-if="badges.length || selectedSocialUrl" class="profile-actions">
          <div v-if="badges.length" class="profile-badges">
            <span v-for="badge in badges" :key="badge" class="badge profile-badge">{{
              badge
            }}</span>
          </div>
          <SocialIconLink v-if="selectedSocialUrl" :href="selectedSocialUrl" />
        </div>

        <p v-if="selectedPlayer.short_description">{{ selectedPlayer.short_description }}</p>
        <div
          v-if="selectedPlayer.bio && selectedPlayer.bio !== selectedPlayer.short_description"
          class="history-item"
        >
          <strong>Биография</strong><br />
          <span class="muted">{{ selectedPlayer.bio }}</span>
        </div>
        <div v-if="selectedPlayer.qualification_route" class="history-item">
          <strong>Отбор</strong><br />
          <span class="muted">{{ selectedPlayer.qualification_route }}</span>
        </div>
        <div v-if="selectedPlayer.strengths" class="history-item">
          <strong>Сильные стороны</strong><br />
          <span class="muted">{{ selectedPlayer.strengths }}</span>
        </div>
        <div v-if="selectedPlayer.previous_dygyn_note" class="history-item">
          <strong>Опыт Игр Дыгына</strong><br />
          <span class="muted">{{ selectedPlayer.previous_dygyn_note }}</span>
        </div>

        <div v-if="selectedPlayer.history?.length" class="history">
          <h3>История выступлений</h3>
          <div
            v-for="item in selectedPlayer.history"
            :key="`${item.year}-${item.competition}`"
            class="history-item"
          >
            <div class="row">
              <strong>{{ item.competition }}</strong>
              <span>{{ item.year }}</span>
            </div>
            <p class="muted">
              {{ item.place ? `${item.place} место` : 'место не указано'
              }}{{ item.score ? ` · ${item.score} очков` : '' }}
            </p>
            <p v-if="visibleHistoryNote(item)">{{ visibleHistoryNote(item) }}</p>
          </div>
        </div>

        <a
          v-if="selectedPlayer.source_url"
          class="ghost wide source-link"
          :href="selectedPlayer.source_url"
          target="_blank"
          rel="noopener noreferrer"
        >
          Источник данных
        </a>
      </article>

      <article v-for="group in disciplineGroups" :key="group.title" class="card">
        <h2>{{ group.title }}</h2>
        <p v-if="overallResultSummary(group.rows)" class="muted result-summary">
          {{ overallResultSummary(group.rows) }}
        </p>
        <div class="table-wrap">
          <table class="result-table">
            <thead>
              <tr>
                <th>Вид</th>
                <th>Результат</th>
                <th>Итог</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in group.rows" :key="`${group.title}-${row.discipline_id}`">
                <td>
                  <strong>{{ row.discipline_name || row.discipline_id }}</strong
                  ><br /><small>{{ row.name_yakut || '' }}</small>
                </td>
                <td>{{ formatResultValue(row) }}</td>
                <td>{{ formatDisciplineOutcome(row) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
      <article v-if="!disciplineGroups.length" class="card">
        <p class="muted">Статистика по видам пока не загружена.</p>
      </article>
    </template>

    <template v-else>
      <article v-if="playersStore.loading" class="card empty">Загрузка участников...</article>
      <article v-else-if="!playersStore.players.length" class="card empty">
        Участники пока не загружены.
      </article>
      <template v-else>
        <article class="card screen-head">
          <p class="eyebrow">Атлеты</p>
          <h2>Выберите участника</h2>
          <p class="muted">Фото, регион и подробная статистика по дисциплинам.</p>
        </article>
        <section class="players-grid" aria-label="Участники">
          <PlayerGridCard
            v-for="player in playersStore.players"
            :key="player.id"
            :player="player"
            @open="openPlayer"
          />
        </section>
      </template>
    </template>
  </div>
</template>
