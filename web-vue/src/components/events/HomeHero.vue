<script setup lang="ts">
import { computed } from 'vue'

import type { EventDetail, Participant } from '@/api/types'
import heroImage from '@/assets/images/dygyn-logo.jpeg'
import { useCountdown } from '@/composables/useCountdown'
import { formatDate, initials, statusLabel } from '@/utils/display'

const props = defineProps<{
  event: EventDetail | null
  loading?: boolean
}>()

const emit = defineEmits<{
  vote: []
}>()

const { isElapsed, parts } = useCountdown(() => props.event?.starts_at)

const heroPhotos = computed<Participant[]>(() => {
  const participants = props.event?.participants || []
  const withPhotos = participants.filter((participant) => participant.avatar_url)
  return (withPhotos.length ? withPhotos : participants).slice(0, 4)
})
const hasSavedVote = computed(() => Boolean(props.event?.my_picks?.length))
</script>

<template>
  <section class="home-hero" aria-label="Главная">
    <div class="home-hero__media" aria-hidden="true">
      <div class="home-hero__glow"></div>
      <img class="home-hero__logo" :src="heroImage" alt="" />
      <div class="home-hero__photos">
        <template v-if="heroPhotos.length">
          <div
            v-for="participant in heroPhotos"
            :key="participant.id"
            class="home-hero__photo-card"
          >
            <img
              v-if="participant.avatar_url"
              :src="participant.avatar_url"
              :alt="participant.name"
            />
            <span v-else>{{ initials(participant.name) }}</span>
          </div>
        </template>
        <template v-else>
          <div v-for="index in 4" :key="index" class="home-hero__photo-card is-empty">
            <span>{{ index }}</span>
          </div>
        </template>
      </div>
    </div>

    <div class="home-hero__copy">
      <p class="eyebrow">Дыгын Оонньуулара</p>
      <h1>Голосуй за фаворита</h1>
      <p class="home-hero__lead">
        Бот собирает выбор болельщиков: отметьте 1–2 участников, распределите 100 очков и следите за
        поддержкой в реальном времени.
      </p>
    </div>

    <div class="home-hero__countdown">
      <div>
        <span class="home-hero__kicker">{{ isElapsed ? 'старт' : 'до старта' }}</span>
        <strong>{{ props.event ? formatDate(props.event.starts_at) : 'дата скоро' }}</strong>
      </div>
      <div v-if="parts.length && !isElapsed" class="countdown-grid">
        <span v-for="part in parts" :key="part.label" class="countdown-part">
          <strong>{{ part.value }}</strong>
          <small>{{ part.label }}</small>
        </span>
      </div>
      <span v-else class="badge">{{
        props.event ? statusLabel(props.event.status) : 'скоро'
      }}</span>
    </div>

    <button
      v-if="!hasSavedVote"
      type="button"
      class="primary wide home-hero__cta"
      :disabled="loading || !event"
      @click="emit('vote')"
    >
      Выбрать участников
    </button>
  </section>
</template>

<style scoped>
.home-hero {
  position: relative;
  display: grid;
  gap: 16px;
  overflow: hidden;
  min-height: 548px;
  padding: 18px;
  border: 1px solid var(--line-strong);
  border-radius: 34px;
  background:
    radial-gradient(circle at 76% 8%, rgba(226, 177, 82, 0.3), transparent 30%),
    radial-gradient(circle at 16% 24%, rgba(111, 71, 18, 0.28), transparent 34%),
    linear-gradient(160deg, rgba(29, 27, 22, 0.94), rgba(7, 9, 13, 0.98) 64%);
  box-shadow: var(--shadow-strong);
}

.home-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(90deg, transparent, rgba(226, 177, 82, 0.42), transparent) top / 100%
    52px no-repeat;
  -webkit-mask: url('../../assets/images/ornament-yakut-1.svg') top center / auto 52px repeat-x;
  mask: url('../../assets/images/ornament-yakut-1.svg') top center / auto 52px repeat-x;
  opacity: 0.62;
}

.home-hero > * {
  position: relative;
  z-index: 1;
}

.home-hero__media {
  position: relative;
  min-height: 286px;
  margin-top: 18px;
}

.home-hero__glow {
  position: absolute;
  inset: 46px 20px auto;
  height: 210px;
  border-radius: 999px;
  background: rgba(226, 177, 82, 0.2);
  filter: blur(40px);
}

.home-hero__logo {
  position: absolute;
  inset: 28px 16px auto auto;
  width: 64%;
  height: 236px;
  object-fit: cover;
  border: 1px solid rgba(255, 224, 161, 0.2);
  border-radius: 30px;
  transform: rotate(2deg);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.46);
}

.home-hero__photos {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  align-items: end;
}

.home-hero__photo-card {
  display: grid;
  place-items: center;
  overflow: hidden;
  height: 118px;
  border: 1px solid rgba(255, 224, 161, 0.22);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.32);
}

.home-hero__photo-card:nth-child(2),
.home-hero__photo-card:nth-child(4) {
  height: 154px;
}

.home-hero__photo-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
}

.home-hero__photo-card span {
  color: var(--accent);
  font-size: 28px;
  font-weight: 950;
}

.home-hero__photo-card.is-empty {
  opacity: 0.65;
}

.home-hero__copy {
  max-width: 430px;
}

.home-hero__lead {
  margin: 0;
  color: var(--hint);
  font-size: 16px;
  line-height: 1.5;
}

.home-hero__countdown {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 24px;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(16px);
}

.home-hero__kicker,
.countdown-part small {
  display: block;
  color: var(--hint);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.countdown-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(52px, 1fr));
  gap: 7px;
}

.countdown-part {
  display: grid;
  gap: 2px;
  min-width: 0;
  padding: 10px 8px;
  border: 1px solid rgba(255, 224, 161, 0.14);
  border-radius: 17px;
  background: rgba(255, 255, 255, 0.055);
  text-align: center;
}

.countdown-part strong {
  color: var(--text);
  font-size: 22px;
  line-height: 1;
}

.home-hero__cta {
  margin-top: auto;
}

@media (max-width: 420px) {
  .home-hero {
    min-height: 524px;
    padding: 16px;
  }

  .home-hero__logo {
    width: 70%;
  }

  .home-hero__countdown {
    grid-template-columns: 1fr;
  }
}
</style>
