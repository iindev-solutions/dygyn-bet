import { createRouter, createWebHashHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/events' },
    { path: '/events', component: () => import('@/views/EventsView.vue') },
    { path: '/stats', component: () => import('@/views/StatsView.vue') },
    { path: '/players', component: () => import('@/views/PlayersView.vue') },
    { path: '/rules', component: () => import('@/views/RulesView.vue') },
    {
      path: '/admin',
      component: () => import('@/views/AdminView.vue'),
      meta: { requiresAdmin: true },
    },
    { path: '/:pathMatch(.*)*', redirect: '/events' },
  ],
})
