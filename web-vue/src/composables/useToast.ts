import { readonly, ref } from 'vue'

import { getTelegramWebApp } from './useTelegramInit'

const message = ref('')
const visible = ref(false)
let timer: number | undefined

export function useToast() {
  function show(text: string, haptic: 'success' | 'warning' | 'error' = 'success') {
    message.value = text
    visible.value = true
    if (timer) window.clearTimeout(timer)
    timer = window.setTimeout(() => {
      visible.value = false
    }, 2600)
    getTelegramWebApp()?.HapticFeedback?.notificationOccurred?.(haptic)
  }

  function hide() {
    visible.value = false
  }

  return { message: readonly(message), visible: readonly(visible), show, hide }
}
