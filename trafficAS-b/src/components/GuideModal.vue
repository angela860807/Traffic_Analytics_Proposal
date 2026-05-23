<template>
  <Teleport to="body">
    <div v-if="open" class="guide-backdrop" @click.self="$emit('close')">
      <section class="guide-modal" role="dialog" aria-modal="true" :aria-labelledby="titleId">
        <header class="guide-header">
          <div>
            <div class="guide-kicker mono">{{ guide?.department }}</div>
            <h2 :id="titleId">{{ guide?.title }}</h2>
          </div>
          <button class="guide-close" type="button" aria-label="가이드 닫기" @click="$emit('close')">×</button>
        </header>

        <div class="guide-body">
          <p class="guide-summary">{{ guide?.summary }}</p>

          <div class="guide-section">
            <h3>확인 항목</h3>
            <ul>
              <li v-for="item in guide?.checkpoints" :key="item">{{ item }}</li>
            </ul>
          </div>

          <div class="guide-section">
            <h3>운영 기준</h3>
            <ul>
              <li v-for="item in guide?.actions" :key="item">{{ item }}</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
const props = defineProps({
  open: Boolean,
  guide: {
    type: Object,
    default: null,
  },
})

defineEmits(['close'])

const titleId = `guide-title-${Math.random().toString(36).slice(2)}`
</script>

<style scoped>
.guide-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(0,0,0,.68);
  backdrop-filter: blur(8px);
}
.guide-modal {
  width: min(620px, 94vw);
  max-height: min(760px, 88vh);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: var(--bg2);
  border: 1px solid var(--b);
  border-radius: 10px;
  box-shadow: 0 24px 80px rgba(0,0,0,.38);
}
.guide-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 20px 16px;
  border-bottom: 1px solid var(--b);
}
.guide-kicker {
  font-size: 9px;
  letter-spacing: 1.6px;
  color: var(--a);
  margin-bottom: 6px;
}
.guide-header h2 {
  margin: 0;
  font-size: 19px;
  line-height: 1.25;
  color: var(--t);
}
.guide-close {
  border: 1px solid var(--b);
  background: var(--card);
  color: var(--t2);
  width: 30px;
  height: 30px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}
.guide-close:hover {
  color: var(--danger);
  border-color: rgba(224,82,96,.35);
}
.guide-body {
  overflow-y: auto;
  padding: 18px 20px 20px;
}
.guide-summary {
  margin: 0 0 16px;
  color: var(--t2);
  font-size: 13px;
  line-height: 1.7;
}
.guide-section {
  padding: 14px 0;
  border-top: 1px solid var(--b);
}
.guide-section h3 {
  margin: 0 0 10px;
  font-size: 12px;
  color: var(--t);
  letter-spacing: .04em;
}
.guide-section ul {
  margin: 0;
  padding-left: 18px;
}
.guide-section li {
  color: var(--t2);
  font-size: 12px;
  line-height: 1.7;
  margin: 4px 0;
}
.mono {
  font-family: 'IBM Plex Mono', monospace;
}
</style>
