<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { adminWebLogin } from '@/api/adminAuth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submitLogin() {
  error.value = ''
  loading.value = true
  try {
    const data = await adminWebLogin(username.value, password.value)
    userStore.setUser(data.user)
    await router.replace('/admin')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Не удалось войти'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="stack">
    <article class="card">
      <h2>Вход администратора</h2>
      <p class="muted">Для браузерной админки без Telegram.</p>
      <form class="admin-form" @submit.prevent="submitLogin">
        <label>
          Логин
          <input v-model="username" name="username" autocomplete="username" required />
        </label>
        <label>
          Пароль
          <input
            v-model="password"
            name="password"
            type="password"
            autocomplete="current-password"
            required
          />
        </label>
        <p v-if="error" class="muted">{{ error }}</p>
        <button class="primary wide" type="submit" :disabled="loading">
          {{ loading ? 'Входим...' : 'Войти' }}
        </button>
      </form>
    </article>
  </div>
</template>
