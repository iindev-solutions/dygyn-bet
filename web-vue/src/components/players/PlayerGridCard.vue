<script setup lang="ts">
import { computed } from 'vue'

import type { Participant } from '@/api/types'
import { initials, playerOrigin, playerSocialUrl } from '@/utils/display'

import SocialIconLink from './SocialIconLink.vue'

const props = defineProps<{
  player: Participant
}>()

const emit = defineEmits<{
  open: [playerId: number]
}>()

const socialUrl = computed(() => playerSocialUrl(props.player))
</script>

<template>
  <article class="player-tile">
    <button type="button" class="player-tile__open" @click="emit('open', props.player.id)">
      <span class="player-tile__photo-wrap">
        <img
          v-if="props.player.avatar_url"
          class="player-tile__photo"
          :src="props.player.avatar_url"
          :alt="props.player.name"
          loading="lazy"
        />
        <span v-else class="player-tile__photo player-tile__fallback">{{
          initials(props.player.name)
        }}</span>
      </span>
      <span class="player-tile__copy">
        <strong>{{ props.player.name }}</strong>
        <small>{{ playerOrigin(props.player) }}</small>
      </span>
    </button>

    <div class="player-tile__footer">
      <button type="button" class="ghost player-tile__stats" @click="emit('open', props.player.id)">
        Статы
      </button>
      <SocialIconLink v-if="socialUrl" :href="socialUrl" />
    </div>
  </article>
</template>

<style scoped>
.player-tile {
  display: grid;
  gap: 9px;
  min-width: 0;
  overflow: hidden;
  padding: 8px;
  border: 1px solid var(--line);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.045);
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.22);
}

.player-tile__open {
  display: grid;
  gap: 10px;
  width: 100%;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--text);
  text-align: left;
  cursor: pointer;
}

.player-tile__photo-wrap {
  display: block;
  overflow: hidden;
  aspect-ratio: 0.78;
  border: 1px solid rgba(255, 224, 161, 0.19);
  border-radius: 19px;
  background: rgba(255, 255, 255, 0.06);
}

.player-tile__photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
}

.player-tile__fallback {
  display: grid;
  place-items: center;
  color: var(--accent);
  font-size: 34px;
  font-weight: 950;
  background: rgba(226, 177, 82, 0.13);
}

.player-tile__copy {
  display: grid;
  gap: 3px;
  min-width: 0;
  padding: 0 4px;
}

.player-tile__copy strong,
.player-tile__copy small {
  overflow: hidden;
  text-overflow: ellipsis;
}

.player-tile__copy strong {
  display: -webkit-box;
  min-height: 40px;
  font-size: 16px;
  line-height: 1.18;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.player-tile__copy small {
  display: block;
  white-space: nowrap;
  color: var(--hint);
  font-size: 12px;
  font-weight: 800;
}

.player-tile__footer {
  display: flex;
  gap: 8px;
  align-items: center;
  min-height: 38px;
}

.player-tile__stats {
  flex: 1;
  min-height: 38px;
  padding: 8px 10px;
  border-radius: 14px;
  font-size: 13px;
}
</style>
