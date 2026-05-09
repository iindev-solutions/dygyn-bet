<script setup lang="ts">
defineProps<{
  href: string
}>()
</script>

<template>
  <a
    class="social-icon"
    :href="href"
    target="_blank"
    rel="noopener noreferrer"
    aria-label="Соцсеть"
  >
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="4" y="4" width="16" height="16" rx="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17" cy="7" r="1.2" />
    </svg>
  </a>
</template>

<style scoped>
.social-icon {
  display: inline-grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border: 1px solid rgba(255, 224, 161, 0.2);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.07);
  color: var(--accent);
  text-decoration: none;
}

.social-icon svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.9;
}
</style>
