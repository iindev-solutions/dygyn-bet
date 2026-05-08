import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { getMe } from '@/api/user'
import type { ApiUser } from '@/api/types'

export const useUserStore = defineStore('user', () => {
  const user = ref<ApiUser | null>(null)
  const loading = ref(false)
  const loaded = ref(false)

  const isAdmin = computed(() => Boolean(user.value?.is_admin))
  const displayName = computed(() => {
    if (!user.value) return 'Загрузка пользователя...'
    return (
      [user.value.first_name, user.value.last_name].filter(Boolean).join(' ') ||
      user.value.username ||
      String(user.value.telegram_id)
    )
  })

  async function load() {
    loading.value = true
    try {
      const data = await getMe()
      user.value = data.user
      loaded.value = true
      return data.user
    } finally {
      loading.value = false
    }
  }

  return { user, loading, loaded, isAdmin, displayName, load }
})
