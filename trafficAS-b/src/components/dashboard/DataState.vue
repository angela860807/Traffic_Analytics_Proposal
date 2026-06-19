<template>
  <div v-if="state === 'loading'" class="ds-state" role="status" aria-live="polite">
    <span class="ds-spinner" aria-hidden="true"></span>
    <span>{{ loadingText }}</span>
  </div>

  <div v-else-if="state === 'error'" class="ds-state ds-error" role="alert">
    <strong>{{ errorTitle }}</strong>
    <span>{{ errorText }}</span>
    <button type="button" class="ds-retry" @click="$emit('retry')">
      {{ retryText }}
    </button>
  </div>

  <div v-else-if="state === 'empty'" class="ds-state ds-empty">
    <span>{{ emptyText }}</span>
  </div>

  <slot v-else />
</template>

<script setup>
defineEmits(['retry'])

defineProps({
  state: {
    type: String,
    default: 'ok',
    validator: (value) => ['loading', 'error', 'empty', 'ok'].includes(value),
  },
  loadingText: {
    type: String,
    default: '\uBD88\uB7EC\uC624\uB294 \uC911',
  },
  errorTitle: {
    type: String,
    default: '\uB370\uC774\uD130\uB97C \uBD88\uB7EC\uC624\uC9C0 \uBABB\uD588\uC2B5\uB2C8\uB2E4',
  },
  errorText: {
    type: String,
    default: '\uC7A0\uC2DC \uD6C4 \uB2E4\uC2DC \uC2DC\uB3C4\uD574\uC8FC\uC138\uC694.',
  },
  emptyText: {
    type: String,
    default: '\uAC80\uC0C9 \uACB0\uACFC\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4.',
  },
  retryText: {
    type: String,
    default: '\uB2E4\uC2DC \uC2DC\uB3C4',
  },
})
</script>

<style scoped>
.ds-state {
  display: flex;
  min-height: 72px;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 18px;
  color: #4a5b78;
  font-size: 13px;
  text-align: center;
}

.ds-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #d9e3f3;
  border-top-color: #2563eb;
  border-radius: 999px;
  animation: ds-spin 0.8s linear infinite;
}

.ds-error {
  flex-direction: column;
  color: #b91c1c;
}

.ds-empty {
  color: #6b7a92;
}

.ds-retry {
  border: 1px solid #fecaca;
  border-radius: 6px;
  background: #fff;
  color: #b91c1c;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 10px;
  cursor: pointer;
}

.ds-retry:hover {
  background: #fef2f2;
}

@keyframes ds-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
