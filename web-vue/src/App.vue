<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'

import heroImage from '@/assets/images/dygyn-logo.jpeg'
import { useTelegramInit } from '@/composables/useTelegramInit'
import { useToast } from '@/composables/useToast'
import { useEventsStore } from '@/stores/events'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const telegram = useTelegramInit()
const toast = useToast()
const userStore = useUserStore()
const eventsStore = useEventsStore()

const booting = ref(true)
const bootError = ref('')

const tabs = computed(() => {
  const baseTabs = [
    { path: '/events', label: 'Игры' },
    { path: '/stats', label: 'Поддержка' },
    { path: '/players', label: 'Участники' },
  ]
  if (userStore.isAdmin) baseTabs.push({ path: '/admin', label: 'Админ' })
  baseTabs.push({ path: '/rules', label: 'Правила' })
  return baseTabs
})

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(`${path}/`)
}

async function go(path: string) {
  await router.push(path)
}

onMounted(async () => {
  if (route.path === '/admin-login') {
    booting.value = false
    return
  }

  try {
    const telegramReady = telegram.init({ timeoutMs: 2200 })
    await userStore.load()
    await telegramReady
    await eventsStore.loadEvents()
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
    <header class="app-hero">
      <div class="hero-ornament" aria-hidden="true"></div>
      <div class="hero-photo">
        <img :src="heroImage" alt="Дыгын Оонньуулара" />
      </div>
      <div class="hero-copy">
        <p class="eyebrow">Дыгын Оонньуулара</p>
        <h1>Игры Дыгына</h1>
        <p class="hero-subtitle">Выберите топ-2 участников и распределите 100 очков.</p>
      </div>
      <p class="sr-only">Пользователь: {{ userStore.displayName }}</p>
    </header>

    <nav class="tabs" aria-label="Разделы">
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
