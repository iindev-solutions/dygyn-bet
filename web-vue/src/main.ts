import './assets/styles/main.css'

import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import { router } from './router'
import { useUserStore } from './stores/user'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

router.beforeEach((to) => {
  const user = useUserStore()
  if (to.meta.requiresAdmin && user.loaded && !user.isAdmin) return '/admin-login'
  return true
})

app.mount('#app')
