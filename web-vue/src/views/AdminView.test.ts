// @vitest-environment jsdom

import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { getMe } from '@/api/user'
import { useEventsStore } from '@/stores/events'

import AdminView from './AdminView.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({ replace: vi.fn() }),
}))

vi.mock('@/api/user', () => ({
  getMe: vi.fn(),
}))

vi.mock('@/api/admin', () => ({
  listDisciplines: vi.fn().mockResolvedValue({ disciplines: [] }),
  loadAdminAnalytics: vi.fn().mockResolvedValue({
    analytics: {
      days: 14,
      since: '2026-05-01',
      generated_at: '',
      daily: [],
      events: [],
      top_paths: [],
    },
  }),
  saveDisciplineResult: vi.fn(),
  saveStanding: vi.fn(),
  finishEvent: vi.fn(),
}))

describe('AdminView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(getMe).mockReset()
  })

  it('hydrates browser admin session before showing missing rights on direct route', async () => {
    vi.mocked(getMe).mockResolvedValue({
      user: {
        id: 1,
        telegram_id: -900001,
        first_name: 'Admin',
        username: 'admin',
        is_admin: true,
      },
    })

    useEventsStore().selectedEvent = {
      id: 1,
      title: 'Дыгын 2026',
      starts_at: '2026-06-01T00:00:00Z',
      status: 'open',
      participants: [],
      my_picks: [],
      totals: {},
      live_results: null,
    }

    const wrapper = mount(AdminView)
    await flushPromises()

    expect(getMe).toHaveBeenCalledWith({ skipTelegramInit: true })
    expect(wrapper.text()).not.toContain('Нужны права администратора')
    expect(wrapper.text()).toContain('Админ')
  })
})
