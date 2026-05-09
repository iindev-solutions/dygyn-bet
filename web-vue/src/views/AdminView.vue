<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { adminWebLogout } from '@/api/adminAuth'
import AdminAnalyticsPanel from '@/components/admin/AdminAnalyticsPanel.vue'
import { useToast } from '@/composables/useToast'
import { useAdminStore } from '@/stores/admin'
import { useEventsStore } from '@/stores/events'
import { useUserStore } from '@/stores/user'
import { formatDate, numberOrNull } from '@/utils/display'

const router = useRouter()
const userStore = useUserStore()
const eventsStore = useEventsStore()
const adminStore = useAdminStore()
const toast = useToast()

const event = computed(() => eventsStore.selectedEvent)

onMounted(async () => {
  if (!userStore.loaded) {
    try {
      await userStore.load({ skipTelegramInit: true })
    } catch {
      await router.replace('/admin-login')
      return
    }
  }
  if (!userStore.isAdmin) {
    await router.replace('/admin-login')
    return
  }
  await Promise.all([adminStore.loadDisciplines(), adminStore.loadAnalytics()])
  if (!event.value) await eventsStore.loadEvents()
})

async function refreshAdmin() {
  if (!event.value) return
  await eventsStore.loadEvent(event.value.id)
  toast.show('Админка обновлена')
}

async function logout() {
  await adminWebLogout()
  userStore.clear()
  await router.replace('/admin-login')
}

async function submitDisciplineResult(payload: Event) {
  payload.preventDefault()
  if (!event.value) return
  const form = new FormData(payload.currentTarget as HTMLFormElement)
  await adminStore.upsertDisciplineResult(event.value.id, {
    day_number: Number(form.get('day_number')),
    participant_id: Number(form.get('participant_id')),
    discipline_id: String(form.get('discipline_id')),
    result_text: String(form.get('result_text') || ''),
    result_value: numberOrNull(form.get('result_value')),
    result_unit: String(form.get('result_unit') || ''),
    place: numberOrNull(form.get('place')),
    points: numberOrNull(form.get('points')),
    status: String(form.get('status') || 'provisional'),
    notes: String(form.get('notes') || ''),
  })
  await eventsStore.loadEvent(event.value.id)
  toast.show('Результат сохранён')
}

async function submitStanding(payload: Event) {
  payload.preventDefault()
  if (!event.value) return
  const form = new FormData(payload.currentTarget as HTMLFormElement)
  await adminStore.upsertStanding(event.value.id, {
    day_number: Number(form.get('day_number')),
    participant_id: Number(form.get('participant_id')),
    place: Number(form.get('place')),
    total_points: numberOrNull(form.get('total_points')),
    is_winner: form.get('is_winner') === 'on',
    status: String(form.get('status') || 'provisional'),
    notes: String(form.get('notes') || ''),
  })
  await eventsStore.loadEvent(event.value.id)
  toast.show('Таблица сохранена')
}

async function submitFinish(payload: Event) {
  payload.preventDefault()
  if (!event.value) return
  if (!window.confirm('Завершить событие и начислить очки болельщикам?')) return
  const form = new FormData(payload.currentTarget as HTMLFormElement)
  const data = await adminStore.finish(event.value.id, Number(form.get('winner_participant_id')))
  eventsStore.selectedEvent = data.event
  await eventsStore.loadEvents()
  toast.show('Событие завершено')
}
</script>

<template>
  <div class="stack">
    <article v-if="userStore.loading" class="card empty">Загрузка...</article>
    <article v-else-if="!userStore.isAdmin" class="card empty">Нужны права администратора.</article>
    <article v-else-if="!event" class="card empty">Сначала создайте событие.</article>

    <template v-else>
      <article class="card">
        <div class="row">
          <div>
            <h2>Админ</h2>
            <p class="muted">{{ event.title }} · Day 1 / Day 2 / финал</p>
          </div>
          <div class="row">
            <button type="button" class="ghost" @click="refreshAdmin">Обновить</button>
            <button type="button" class="ghost" @click="logout">Выйти</button>
          </div>
        </div>
      </article>

      <AdminAnalyticsPanel :analytics="adminStore.analytics" />

      <article class="card">
        <h2>Результат дисциплины</h2>
        <form class="admin-form" @submit="submitDisciplineResult">
          <div class="form-grid">
            <label
              >День<select name="day_number">
                <option value="1">День 1</option>
                <option value="2">День 2</option>
              </select></label
            >
            <label
              >Статус<select name="status">
                <option value="provisional">Промежуточно</option>
                <option value="official">Официально</option>
              </select></label
            >
          </div>
          <label>
            Участник
            <select name="participant_id">
              <option
                v-for="participant in event.participants"
                :key="participant.id"
                :value="participant.id"
              >
                {{ participant.name }}
              </option>
            </select>
          </label>
          <label>
            Вид
            <select name="discipline_id">
              <option
                v-for="discipline in adminStore.disciplines"
                :key="discipline.discipline_id"
                :value="discipline.discipline_id"
              >
                {{ discipline.name_ru }}
              </option>
            </select>
          </label>
          <div class="form-grid">
            <label>Результат<input name="result_text" placeholder="5:40 / 50 / >102" /></label>
            <label
              >Число для сортировки<input
                name="result_value"
                type="number"
                step="0.01"
                placeholder="340"
            /></label>
          </div>
          <div class="form-grid">
            <label>Единица<input name="result_unit" placeholder="секунды / метры / очки" /></label>
            <label>Место<input name="place" type="number" min="1" /></label>
          </div>
          <label>Очки<input name="points" type="number" step="0.01" /></label>
          <label
            >Заметка<textarea name="notes" placeholder="Источник / комментарий"></textarea>
          </label>
          <button class="primary wide" type="submit">Сохранить результат</button>
        </form>
      </article>

      <article class="card">
        <h2>Таблица итогов</h2>
        <form class="admin-form" @submit="submitStanding">
          <div class="form-grid">
            <label
              >Раздел<select name="day_number">
                <option value="1">День 1</option>
                <option value="2">День 2</option>
                <option value="0">Общий зачёт</option>
              </select></label
            >
            <label
              >Статус<select name="status">
                <option value="provisional">Промежуточно</option>
                <option value="official">Официально</option>
              </select></label
            >
          </div>
          <label>
            Участник
            <select name="participant_id">
              <option
                v-for="participant in event.participants"
                :key="participant.id"
                :value="participant.id"
              >
                {{ participant.name }}
              </option>
            </select>
          </label>
          <div class="form-grid">
            <label>Место<input name="place" type="number" min="1" required /></label>
            <label>Сумма очков<input name="total_points" type="number" step="0.01" /></label>
          </div>
          <label
            ><span><input name="is_winner" type="checkbox" /> Победитель</span></label
          >
          <label
            >Заметка<textarea name="notes" placeholder="Источник / комментарий"></textarea>
          </label>
          <button class="primary wide" type="submit">Сохранить строку</button>
        </form>
      </article>

      <article class="card">
        <h2>Завершить событие</h2>
        <form class="admin-form" @submit="submitFinish">
          <label>
            Победитель
            <select name="winner_participant_id">
              <option
                v-for="participant in event.participants"
                :key="participant.id"
                :value="participant.id"
              >
                {{ participant.name }}
              </option>
            </select>
          </label>
          <button class="primary wide" type="submit">
            Зафиксировать победителя и начислить очки
          </button>
        </form>
      </article>

      <article class="card">
        <h2>Текущие результаты</h2>
        <div
          v-if="
            event.live_results?.standings?.length || event.live_results?.discipline_results?.length
          "
          class="history"
        >
          <p class="muted">
            {{
              event.live_results?.last_updated_at
                ? `Обновлено: ${formatDate(event.live_results.last_updated_at)}`
                : ''
            }}
          </p>
          <div
            v-for="row in event.live_results?.standings || []"
            :key="`s-${row.day_number}-${row.place}-${row.player_name}`"
            class="history-item"
          >
            <div class="row">
              <strong>{{ row.day_number === 0 ? 'Общий зачёт' : `День ${row.day_number}` }}</strong
              ><span>{{ row.place }} место</span>
            </div>
            <p>
              {{ row.player_name }} · {{ row.total_points ?? '—'
              }}{{ row.is_winner ? ' · победитель' : '' }}
            </p>
          </div>
          <div
            v-for="row in event.live_results?.discipline_results || []"
            :key="`d-${row.day_number}-${row.discipline_id}-${row.player_name}`"
            class="history-item"
          >
            <div class="row">
              <strong>День {{ row.day_number }} · {{ row.discipline_name }}</strong
              ><span>{{ row.place || '—' }}</span>
            </div>
            <p>{{ row.player_name }} · {{ row.result_text || row.result_value || '—' }}</p>
          </div>
        </div>
        <p v-else class="muted">Результаты ещё не внесены.</p>
      </article>
    </template>
  </div>
</template>
