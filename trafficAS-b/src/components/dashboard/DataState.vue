<template>
  <!-- 로딩 -->
  <div v-if="state === 'loading'" class="ds-box ds-loading" role="status" aria-live="polite">
    <div class="ds-spin" aria-hidden="true"></div>
    <div class="ds-msg">{{ loadingText }}</div>
  </div>
  <!-- 에러 -->
  <div v-else-if="state === 'error'" class="ds-box ds-error" role="alert">
    <i class="bi bi-exclamation-triangle-fill" aria-hidden="true"></i>
    <div class="ds-msg">{{ errorText }}</div>
    <button v-if="canRetry" class="ds-retry" @click="$emit('retry')">
      <i class="bi bi-arrow-clockwise" aria-hidden="true"></i> 다시 시도
    </button>
  </div>
  <!-- 빈 -->
  <div v-else-if="state === 'empty'" class="ds-box ds-empty" role="status">
    <i :class="emptyIcon" aria-hidden="true"></i>
    <div class="ds-msg">{{ emptyText }}</div>
    <slot name="empty-action"></slot>
  </div>
  <!-- 정상 (slot) -->
  <slot v-else></slot>
</template>

<script setup>
defineProps({
  state: { type: String, default: "ok" }, // "loading" | "error" | "empty" | "ok"
  loadingText: { type: String, default: "데이터를 불러오는 중..." },
  errorText:   { type: String, default: "데이터를 불러오지 못했습니다." },
  emptyText:   { type: String, default: "표시할 데이터가 없습니다." },
  emptyIcon:   { type: String, default: "bi bi-inbox" },
  canRetry:    { type: Boolean, default: true },
});
defineEmits(["retry"]);
</script>

<style scoped>
.ds-box {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 10px; padding: 28px 16px; min-height: 140px;
  background: var(--tas-surface-2, #06101e);
  border: 1px dashed var(--tas-border, #1f3055);
  border-radius: var(--tas-radius, 10px);
  color: var(--tas-text-muted, rgba(228,238,255,.65));
  font-size: 12.5px;
}
.ds-msg { line-height: 1.5; text-align: center; }
.ds-loading .ds-spin {
  width: 24px; height: 24px;
  border: 2px solid var(--tas-border, #1f3055);
  border-top-color: var(--tas-brand, #60a5fa);
  border-radius: 50%;
  animation: ds-rot 0.8s linear infinite;
}
@keyframes ds-rot { to { transform: rotate(360deg); } }
.ds-error > i { font-size: 24px; color: var(--tas-danger, #f87171); }
.ds-empty > i { font-size: 26px; color: var(--tas-text-faint, rgba(228,238,255,.45)); }
.ds-retry {
  margin-top: 4px; padding: 6px 14px;
  background: var(--tas-brand-soft, rgba(96,165,250,.12));
  border: 1px solid var(--tas-brand, #60a5fa);
  color: var(--tas-brand, #60a5fa);
  border-radius: 5px; cursor: pointer;
  font-size: 12px; font-family: inherit; font-weight: 600;
  display: inline-flex; align-items: center; gap: 6px;
}
.ds-retry:hover { background: rgba(96,165,250,.18); }
</style>
