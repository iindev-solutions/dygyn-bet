<script setup lang="ts">
import { onMounted } from 'vue'

import { useAnalytics } from '@/composables/useAnalytics'

const analytics = useAnalytics()

onMounted(() => {
  analytics.track('rules_open')
})
</script>

<template>
  <div class="stack">
    <article class="card">
      <h2>Правила</h2>
      <ol>
        <li>Один Telegram-пользователь может выбрать до двух участников на одно событие.</li>
        <li>До сохранения можно менять выбор и распределение очков.</li>
        <li>Очки уверенности — виртуальные, не деньги. Выбор должен суммарно давать 100 очков.</li>
        <li>После сохранения выбора можно скачать PNG-карточку для публикации.</li>
        <li>
          После внесения результата администратором правильным голосам начисляются очки рейтинга.
        </li>
      </ol>
    </article>

    <article class="card">
      <h2>Конфиденциальность</h2>
      <p class="muted">
        Мы используем Telegram-профиль для входа и сохранения голоса. В аналитике храним только
        технические события без Telegram ID, username, IP и текста голосов.
      </p>
      <p class="muted">
        Проект от
        <a
          class="inline-link"
          href="https://iindiinda.duckdns.org/"
          target="_blank"
          rel="noopener noreferrer"
          >iindev</a
        >.
      </p>
    </article>
  </div>
</template>
