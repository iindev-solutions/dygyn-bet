<script setup lang="ts">
import { computed, ref } from 'vue'

import type { EventDetail, LiveDisciplineResult, LiveStanding, Participant } from '@/api/types'
import { useToast } from '@/composables/useToast'
import { useEventsStore } from '@/stores/events'
import {
  formatDate,
  MAX_PICKS,
  statusLabel,
  supportPercent,
  topSupport,
  TOTAL_CONFIDENCE_POINTS,
} from '@/utils/display'
import { createAndShareStoryCard } from '@/utils/storyCard'

const eventsStore = useEventsStore()
const toast = useToast()
const storyHelp = ref('Дальше: Instagram → Stories → выбрать PNG из галереи/загрузок.')
const storyBusy = ref(false)

const selectedEvent = computed(() => eventsStore.selectedEvent)
const canPick = computed(() => selectedEvent.value?.status === 'open')
const topLeaders = computed(() => topSupport(selectedEvent.value, 3))

function eventParticipantCount(event: EventDetail): number {
  return event.participant_count || event.participants?.length || 0
}

function selectedSet(): Set<number> {
  return new Set(eventsStore.draftPlayerIds)
}

function sideValue(event: EventDetail, participant: Participant): string | number {
  if (selectedSet().has(Number(participant.id)))
    return eventsStore.draftAllocations[participant.id] || 0
  return `${supportPercent(event, participant)}%`
}

function sideLabel(participant: Participant): string {
  return selectedSet().has(Number(participant.id)) ? 'мой голос' : 'поддержка'
}

function togglePick(participantId: number) {
  const result = eventsStore.toggleDraftPick(participantId)
  if (result === 'max') toast.show(`Можно выбрать максимум ${MAX_PICKS} участников`, 'warning')
}

function setAllocation(participantId: number, raw: Event) {
  const input = raw.target as HTMLInputElement
  eventsStore.setDraftAllocation(participantId, Number(input.value))
}

async function savePicks() {
  if (!eventsStore.draftPlayerIds.length) {
    toast.show('Выберите хотя бы одного участника', 'warning')
    return
  }
  if (!eventsStore.isValidAllocation) {
    toast.show('Нужно распределить ровно 100 очков', 'warning')
    return
  }
  await eventsStore.saveCurrentPrediction()
  toast.show('Голос сохранён')
}

function buildShareText(): string {
  return `Мой голос на Игры Дыгына: ${eventsStore.pickedSummaries().join(', ')}`
}

async function copyShareText() {
  const text = buildShareText()
  try {
    await navigator.clipboard.writeText(text)
    toast.show('Текст скопирован')
  } catch {
    window.prompt('Скопируйте текст:', text)
  }
}

async function nativeShare() {
  const text = buildShareText()
  if (navigator.share) {
    try {
      await navigator.share({ title: 'Голосование Игр Дыгына', text })
      return
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return
    }
  }
  await copyShareText()
}

async function shareStoryCard() {
  const event = selectedEvent.value
  const picks = eventsStore.pickedParticipants()
  if (!event || !picks.length) {
    toast.show('Сначала выберите участника', 'warning')
    return
  }
  storyBusy.value = true
  try {
    const result = await createAndShareStoryCard(event, picks)
    storyHelp.value = result.message
    toast.show(
      result.shared ? 'Выберите Instagram Stories в меню' : 'PNG скачан — открой Instagram Stories',
    )
  } catch (err) {
    toast.show(err instanceof Error ? err.message : 'Не удалось собрать карточку', 'error')
  } finally {
    storyBusy.value = false
  }
}

function standingsFor(day: number): LiveStanding[] {
  return (selectedEvent.value?.live_results?.standings || [])
    .filter((row) => Number(row.day_number) === day)
    .slice(0, 5)
}

function disciplineRowsFor(day: number): LiveDisciplineResult[] {
  return (selectedEvent.value?.live_results?.discipline_results || [])
    .filter((row) => Number(row.day_number) === day)
    .slice(0, 8)
}

const hasLiveResults = computed(() => {
  const results = selectedEvent.value?.live_results
  return Boolean(results?.standings?.length || results?.discipline_results?.length)
})
</script>

<template>
  <div class="stack">
    <article v-if="eventsStore.loading" class="card empty">Загрузка игр...</article>
    <article v-else-if="!eventsStore.events.length" class="card empty">Пока нет событий.</article>

    <template v-if="selectedEvent">
      <article class="card event-card">
        <div class="row">
          <span class="badge">{{ statusLabel(selectedEvent.status) }}</span>
          <span class="muted">{{ formatDate(selectedEvent.starts_at) }}</span>
        </div>
        <h2>{{ selectedEvent.title }}</h2>
        <div class="stat-grid">
          <div class="stat-box">
            <strong>{{ eventParticipantCount(selectedEvent) }}</strong
            ><span>участников</span>
          </div>
          <div class="stat-box">
            <strong>{{ selectedEvent.totals?.picks || 0 }}</strong
            ><span>голосов</span>
          </div>
          <div class="stat-box"><strong>100</strong><span>очков</span></div>
        </div>
        <div class="history compact-support">
          <h3>Поддержка</h3>
          <template v-if="topLeaders.length">
            <div v-for="participant in topLeaders" :key="participant.id" class="history-item">
              <div class="row">
                <strong>{{ participant.name }}</strong>
                <span>{{ supportPercent(selectedEvent, participant) }}%</span>
              </div>
              <div class="progress">
                <span :style="{ width: `${supportPercent(selectedEvent, participant)}%` }"></span>
              </div>
            </div>
          </template>
          <p v-else class="muted">Поддержка появится после первых голосов.</p>
        </div>
      </article>

      <article v-if="eventsStore.events.length > 1" class="card">
        <h2>События</h2>
        <div class="choices">
          <button
            v-for="event in eventsStore.events"
            :key="event.id"
            type="button"
            class="choice"
            :class="{ selected: selectedEvent.id === event.id }"
            @click="eventsStore.loadEvent(event.id)"
          >
            <span>
              {{ event.title }}<br />
              <small
                >{{ formatDate(event.starts_at) }} · {{ event.participant_count }} участников ·
                {{ event.pick_count }} голосов</small
              >
            </span>
            <strong>{{ statusLabel(event.status) }}</strong>
          </button>
        </div>
      </article>

      <article class="card">
        <div class="row">
          <div>
            <h2>Выберите топ-2</h2>
            <p class="muted">
              {{ eventsStore.draftPlayerIds.length }}/{{ MAX_PICKS }} участников · всего 100 очков
            </p>
          </div>
          <span class="badge">{{ statusLabel(selectedEvent.status) }}</span>
        </div>

        <div class="support-list">
          <button
            v-for="(participant, index) in selectedEvent.participants"
            :key="participant.id"
            type="button"
            class="participant-card"
            :class="{ selected: selectedSet().has(Number(participant.id)) }"
            :disabled="!canPick"
            @click="togglePick(Number(participant.id))"
          >
            <span class="participant-main">
              <span class="rank-dot">{{ index + 1 }}</span>
              <span class="participant-copy">
                <strong>{{ participant.name }}</strong>
                <small
                  >{{ participant.region || 'регион не указан' }} ·
                  {{ participant.pick_count || 0 }} голосов ·
                  {{ Number(participant.confidence_sum || 0) }} очков</small
                >
                <span class="progress"
                  ><span :style="{ width: `${supportPercent(selectedEvent, participant)}%` }"></span
                ></span>
              </span>
            </span>
            <span class="participant-side">
              <span class="percent">{{ sideValue(selectedEvent, participant) }}</span>
              <small>{{ sideLabel(participant) }}</small>
            </span>
          </button>
          <div v-if="!selectedEvent.participants.length" class="empty">Участники не добавлены.</div>
        </div>

        <div v-if="canPick" class="confidence">
          <div class="allocation-head">
            <strong>Распределите 100 очков</strong>
            <span
              class="allocation-total"
              :class="eventsStore.isValidAllocation ? 'valid' : 'invalid'"
            >
              {{ eventsStore.allocationTotal }}/{{ TOTAL_CONFIDENCE_POINTS }}
            </span>
          </div>
          <p class="muted">Можно выбрать 1–2 участников. Сумма должна быть ровно 100.</p>

          <div v-if="eventsStore.draftPlayerIds.length === 1" class="allocation-presets">
            <button
              type="button"
              class="chip active"
              @click="eventsStore.applyAllocationPreset('100')"
            >
              100
            </button>
          </div>
          <div v-else-if="eventsStore.draftPlayerIds.length === 2" class="allocation-presets">
            <button type="button" class="chip" @click="eventsStore.applyAllocationPreset('50/50')">
              50/50
            </button>
            <button type="button" class="chip" @click="eventsStore.applyAllocationPreset('70/30')">
              70/30
            </button>
            <button type="button" class="chip" @click="eventsStore.applyAllocationPreset('30/70')">
              30/70
            </button>
          </div>

          <div class="allocation-list">
            <div
              v-for="playerId in eventsStore.draftPlayerIds"
              :key="playerId"
              class="allocation-row"
            >
              <div class="row">
                <strong>{{ eventsStore.participantById(playerId)?.name || playerId }}</strong>
                <span>{{ eventsStore.draftAllocations[playerId] || 1 }} очков</span>
              </div>
              <div class="allocation-control">
                <input
                  type="range"
                  min="1"
                  max="100"
                  :value="eventsStore.draftAllocations[playerId] || 1"
                  @input="setAllocation(playerId, $event)"
                />
                <input
                  class="allocation-number"
                  type="number"
                  inputmode="numeric"
                  min="1"
                  max="100"
                  :value="eventsStore.draftAllocations[playerId] || 1"
                  :aria-label="`Очки: ${eventsStore.participantById(playerId)?.name || playerId}`"
                  @change="setAllocation(playerId, $event)"
                />
              </div>
            </div>
            <p v-if="!eventsStore.draftPlayerIds.length" class="muted">
              Выберите участника — ему автоматически достанутся 100 очков.
            </p>
          </div>

          <div class="bottom-bar">
            <button
              type="button"
              class="primary wide"
              :disabled="!eventsStore.isValidAllocation || eventsStore.saving"
              @click="savePicks"
            >
              Сохранить голос
            </button>
          </div>
        </div>
        <p v-else class="muted">Голосование закрыто.</p>

        <div v-if="eventsStore.draftPlayerIds.length" class="share-card">
          <h3>Поделиться выбором</h3>
          <p class="muted">Нажмите кнопку: приложение откроет меню «Поделиться» или скачает PNG.</p>
          <p><strong>Мой выбор:</strong> {{ eventsStore.pickedSummaries().join(', ') }}</p>
          <div class="share-actions">
            <button type="button" class="ghost" @click="nativeShare">Поделиться</button>
            <button type="button" class="ghost" @click="copyShareText">Скопировать</button>
            <button type="button" class="primary" :disabled="storyBusy" @click="shareStoryCard">
              Сторис PNG
            </button>
          </div>
          <p class="muted story-help">{{ storyHelp }}</p>
        </div>

        <div v-if="selectedEvent.results?.length" class="history">
          <h3>Итоги</h3>
          <div
            v-for="result in selectedEvent.results"
            :key="`${result.place}-${result.player_name}`"
            class="history-item"
          >
            {{ result.place }} место — {{ result.player_name }}
            <span v-if="result.score">· {{ result.score }}</span>
          </div>
        </div>

        <div v-if="hasLiveResults" class="history">
          <h3>Ход Игр</h3>
          <template v-for="day in [0, 1, 2]" :key="`standing-${day}`">
            <div v-if="standingsFor(day).length" class="history-item">
              <strong>{{ day === 0 ? 'Общий зачёт' : `День ${day}` }}</strong>
              <div
                v-for="row in standingsFor(day)"
                :key="`${day}-${row.place}-${row.player_name}`"
                class="row"
              >
                <span>{{ row.place }}. {{ row.player_name }}</span>
                <span>{{ row.total_points ?? '—' }}{{ row.is_winner ? ' · победитель' : '' }}</span>
              </div>
            </div>
          </template>
          <template v-for="day in [1, 2]" :key="`discipline-${day}`">
            <div v-if="disciplineRowsFor(day).length" class="history-item">
              <strong>Результаты: день {{ day }}</strong>
              <div
                v-for="row in disciplineRowsFor(day)"
                :key="`${day}-${row.discipline_id}-${row.player_name}`"
                class="row"
              >
                <span>{{ row.discipline_name }} · {{ row.player_name }}</span>
                <span>{{ row.result_text || row.place || '—' }}</span>
              </div>
            </div>
          </template>
          <p class="muted">
            {{
              selectedEvent.live_results?.last_updated_at
                ? `Обновлено: ${formatDate(selectedEvent.live_results.last_updated_at)}`
                : ''
            }}
          </p>
        </div>
      </article>
    </template>
  </div>
</template>
