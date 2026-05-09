<script setup lang="ts">
import { computed, onMounted, shallowRef } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useAnalytics } from '@/composables/useAnalytics'
import { useTelegramInit } from '@/composables/useTelegramInit'
import { useToast } from '@/composables/useToast'
import { useEventsStore } from '@/stores/events'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const telegram = useTelegramInit()
const toast = useToast()
const analytics = useAnalytics()
const userStore = useUserStore()
const eventsStore = useEventsStore()

const booting = shallowRef(true)
const bootError = shallowRef('')

const tabs = computed(() => [
  { path: '/events', label: 'Главная' },
  { path: '/stats', label: 'Рейтинг' },
  { path: '/players', label: 'Атлеты' },
  { path: '/rules', label: 'Правила' },
])
const isAdminShell = computed(() => route.path.startsWith('/admin'))

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(`${path}/`)
}

async function go(path: string) {
  await router.push(path)
}

function isAdminEntry(): boolean {
  return route.path.startsWith('/admin') || window.location.hash.startsWith('#/admin')
}

function trackAppOpenOnce() {
  try {
    if (sessionStorage.getItem('dygyn_app_open_tracked')) return
    sessionStorage.setItem('dygyn_app_open_tracked', '1')
  } catch {
    // Session storage can be unavailable in strict browser modes; tracking still stays best-effort.
  }
  analytics.track('app_open', {
    event_id: eventsStore.selectedEvent?.id || null,
    has_saved_vote: Boolean(eventsStore.selectedEvent?.my_picks?.length),
  })
}

onMounted(async () => {
  if (isAdminEntry()) {
    booting.value = false
    return
  }

  try {
    const telegramReady = telegram.init({ timeoutMs: 2200 })
    await userStore.load()
    await telegramReady
    await eventsStore.loadEvents()
    trackAppOpenOnce()
    if (window.location.hash === '#stats') await router.replace('/stats')
  } catch (err) {
    if (route.meta.requiresAdmin) {
      await router.replace('/admin-login')
    } else {
      bootError.value = err instanceof Error ? err.message : 'Не удалось открыть сервис'
    }
  } finally {
    booting.value = false
  }
})
</script>

<template>
  <main class="app">
    <p class="sr-only">Пользователь: {{ userStore.displayName }}</p>

    <nav v-if="!isAdminShell" class="tabs" aria-label="Разделы">
      <button
        v-for="tab in tabs"
        :key="tab.path"
        type="button"
        :class="{ active: isActive(tab.path) }"
        @click="go(tab.path)"
      >
        {{ tab.label }}
      </button>
    </nav>

    <div v-if="booting" class="stack">
      <article class="card empty">Загрузка...</article>
    </div>

    <div v-else-if="bootError" class="stack">
      <article class="card">
        <h2>Не удалось открыть сервис</h2>
        <p class="muted">{{ bootError }}</p>
        <p>
          Откройте приложение из Telegram-кнопки бота или включите ALLOW_DEV_LOGIN=1 для локальной
          разработки.
        </p>
      </article>
    </div>

    <RouterView v-else />
  </main>

  <div v-if="toast.visible.value" class="toast">{{ toast.message.value }}</div>
</template>
