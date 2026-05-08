import { onBeforeUnmount, watch, type Ref } from 'vue'

import { getTelegramWebApp } from './useTelegramInit'

export function useBackButton(active: Ref<boolean>, onBack: () => void) {
  function bind(app: TelegramWebApp | null) {
    if (!app?.BackButton) return
    app.BackButton.onClick(onBack)
    if (active.value) app.BackButton.show()
    else app.BackButton.hide()
  }

  const unwatch = watch(
    active,
    (isActive) => {
      const app = getTelegramWebApp()
      if (!app?.BackButton) return
      if (isActive) app.BackButton.show()
      else app.BackButton.hide()
    },
    { immediate: true },
  )

  bind(getTelegramWebApp())

  onBeforeUnmount(() => {
    unwatch()
    const app = getTelegramWebApp()
    app?.BackButton?.offClick(onBack)
    app?.BackButton?.hide()
  })
}
