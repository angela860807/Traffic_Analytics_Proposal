<template>
  <Teleport to="body">
    <Transition name="guide-fade">
      <div v-if="modelValue" class="guide-root" @click.self="close">
        <!-- 강조 박스: 타겟 좌표를 따라가는 사각형(구멍 뚫기 방식) -->
        <div
          v-if="targetRect"
          class="guide-spot"
          :style="spotStyle"
        ></div>
        <!-- 타겟 없을 때는 전체 어둡게 -->
        <div v-else class="guide-mask-full"></div>

        <!-- 말풍선 -->
        <div
          class="guide-tip"
          :class="['guide-tip-' + tipPos]"
          :style="tipStyle"
          @click.stop
        >
          <div class="guide-tip-head">
            <span class="guide-tip-step">{{ stepIdx + 1 }} / {{ steps.length }}</span>
            <span class="guide-tip-title">{{ currentStep.title }}</span>
            <button class="guide-tip-x" @click="close" aria-label="닫기">
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
          <div class="guide-tip-body">
            <p v-for="(line, i) in descLines" :key="i">{{ line }}</p>
          </div>
          <div class="guide-tip-foot">
            <div class="guide-dots">
              <span
                v-for="(s, i) in steps"
                :key="i"
                class="guide-dot"
                :class="{ on: i === stepIdx }"
                @click="goTo(i)"
              ></span>
            </div>
            <div class="guide-btns">
              <button
                class="guide-btn ghost"
                :disabled="stepIdx === 0"
                @click="prev"
              >
                <i class="bi bi-chevron-left"></i> 이전
              </button>
              <button
                v-if="stepIdx < steps.length - 1"
                class="guide-btn primary"
                @click="next"
              >
                다음 <i class="bi bi-chevron-right"></i>
              </button>
              <button v-else class="guide-btn primary" @click="close">
                <i class="bi bi-check2"></i> 완료
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from "vue";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  steps: { type: Array, required: true },
  /* 단계 변경 시 호출자가 탭/메뉴를 바꾸도록 콜백 — selector 잡기 전에 실행됨 */
  onStepEnter: { type: Function, default: null },
});
const emit = defineEmits(["update:modelValue"]);

const stepIdx = ref(0);
const targetRect = ref(null);
const tipPos = ref("bottom");

const currentStep = computed(() => props.steps[stepIdx.value] || {});
const descLines = computed(() => {
  const d = currentStep.value.description || "";
  return Array.isArray(d) ? d : d.split("\n").filter((x) => x.trim());
});

const PADDING = 8;
const TIP_GAP = 14;
const TIP_W = 360;

const spotStyle = computed(() => {
  if (!targetRect.value) return {};
  const r = targetRect.value;
  return {
    top: r.top - PADDING + "px",
    left: r.left - PADDING + "px",
    width: r.width + PADDING * 2 + "px",
    height: r.height + PADDING * 2 + "px",
  };
});

const tipStyle = computed(() => {
  if (!targetRect.value) {
    return {
      top: "50%",
      left: "50%",
      transform: "translate(-50%, -50%)",
    };
  }
  const r = targetRect.value;
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const spaceBelow = vh - (r.top + r.height);
  const spaceAbove = r.top;
  const spaceRight = vw - (r.left + r.width);
  const spaceLeft = r.left;

  let pos = "bottom";
  if (spaceBelow > 240) pos = "bottom";
  else if (spaceAbove > 240) pos = "top";
  else if (spaceRight > TIP_W + 40) pos = "right";
  else if (spaceLeft > TIP_W + 40) pos = "left";
  else pos = "bottom";
  tipPos.value = pos;

  let top, left;
  if (pos === "bottom") {
    top = r.top + r.height + TIP_GAP;
    left = r.left + r.width / 2 - TIP_W / 2;
  } else if (pos === "top") {
    top = r.top - TIP_GAP - 220;
    left = r.left + r.width / 2 - TIP_W / 2;
  } else if (pos === "right") {
    top = r.top;
    left = r.left + r.width + TIP_GAP;
  } else {
    top = r.top;
    left = r.left - TIP_W - TIP_GAP;
  }
  left = Math.max(16, Math.min(left, vw - TIP_W - 16));
  top = Math.max(16, Math.min(top, vh - 240));
  return {
    top: top + "px",
    left: left + "px",
    width: TIP_W + "px",
  };
});

async function applyStep() {
  const step = props.steps[stepIdx.value];
  if (!step) return;
  /* 단계 진입 콜백 — 호출자가 탭/메뉴/사이드바를 먼저 바꿀 수 있음 */
  if (props.onStepEnter) {
    try {
      await props.onStepEnter(step, stepIdx.value);
    } catch {}
  }
  await nextTick();
  /* DOM 갱신·차트 렌더링 등 위해 한 프레임 더 대기 */
  await new Promise((r) => requestAnimationFrame(() => r()));
  await new Promise((r) => setTimeout(r, 50));

  if (!step.selector) {
    targetRect.value = null;
    return;
  }
  const el = document.querySelector(step.selector);
  if (!el) {
    targetRect.value = null;
    return;
  }
  /* 화면 안으로 스크롤 */
  try {
    el.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });
  } catch {}
  await new Promise((r) => setTimeout(r, 280));
  measure(el);
}

function measure(el) {
  const r = el.getBoundingClientRect();
  targetRect.value = {
    top: r.top,
    left: r.left,
    width: r.width,
    height: r.height,
  };
}

let raf = null;
function tick() {
  const step = props.steps[stepIdx.value];
  if (step?.selector) {
    const el = document.querySelector(step.selector);
    if (el) measure(el);
    else targetRect.value = null;
  }
  raf = requestAnimationFrame(tick);
}

function next() {
  if (stepIdx.value < props.steps.length - 1) {
    stepIdx.value++;
  }
}
function prev() {
  if (stepIdx.value > 0) stepIdx.value--;
}
function goTo(i) {
  stepIdx.value = i;
}
function close() {
  emit("update:modelValue", false);
}

function onKey(e) {
  if (!props.modelValue) return;
  if (e.key === "Escape") close();
  else if (e.key === "ArrowRight") next();
  else if (e.key === "ArrowLeft") prev();
}

watch(
  () => props.modelValue,
  (v) => {
    if (v) {
      stepIdx.value = 0;
      document.body.style.overflow = "hidden";
      applyStep();
      raf = requestAnimationFrame(tick);
    } else {
      document.body.style.overflow = "";
      if (raf) cancelAnimationFrame(raf);
      targetRect.value = null;
    }
  }
);

watch(stepIdx, () => {
  if (props.modelValue) applyStep();
});

onMounted(() => {
  window.addEventListener("keydown", onKey);
  window.addEventListener("resize", () => applyStep());
});
onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKey);
  if (raf) cancelAnimationFrame(raf);
  document.body.style.overflow = "";
});
</script>

<style scoped>
.guide-root {
  position: fixed;
  inset: 0;
  z-index: 99999;
  pointer-events: auto;
}
.guide-mask-full {
  position: absolute;
  inset: 0;
  background: rgba(8, 16, 32, 0.62);
}
/* 강조 박스: 거대한 box-shadow로 외곽을 어둡게 만들어 '구멍' 효과 */
.guide-spot {
  position: absolute;
  border-radius: 10px;
  box-shadow: 0 0 0 9999px rgba(8, 16, 32, 0.62);
  outline: 2px solid #60a5fa;
  outline-offset: 0;
  pointer-events: none;
  transition: top 0.18s, left 0.18s, width 0.18s, height 0.18s;
  animation: guide-pulse 1.6s ease-in-out infinite;
}
@keyframes guide-pulse {
  0%, 100% { outline-color: #60a5fa; }
  50% { outline-color: #93c5fd; }
}

.guide-tip {
  position: absolute;
  background: #ffffff;
  color: #0f1c33;
  border-radius: 14px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.45), 0 4px 14px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(96, 165, 250, 0.3);
  z-index: 2;
  pointer-events: auto;
  overflow: hidden;
  transition: top 0.22s, left 0.22s;
}
.guide-tip-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #2563eb, #60a5fa);
  color: #fff;
}
.guide-tip-step {
  font-family: "IBM Plex Mono", monospace;
  font-size: 12px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.22);
  padding: 3px 8px;
  border-radius: 6px;
  letter-spacing: 0.04em;
}
.guide-tip-title {
  flex: 1;
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.2px;
}
.guide-tip-x {
  background: rgba(255, 255, 255, 0.18);
  border: none;
  color: #fff;
  width: 26px;
  height: 26px;
  border-radius: 6px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}
.guide-tip-x:hover {
  background: rgba(255, 255, 255, 0.3);
}
.guide-tip-body {
  padding: 16px 18px 6px;
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 13.5px;
  line-height: 1.65;
  color: #2c3a52;
}
.guide-tip-body p {
  margin: 0 0 8px;
  word-break: keep-all;
}
.guide-tip-body p:last-child {
  margin-bottom: 0;
}
.guide-tip-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px 14px;
  border-top: 1px solid #eef2f9;
  background: #f8fafc;
  gap: 10px;
}
.guide-dots {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}
.guide-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #cbd5e1;
  cursor: pointer;
  transition: background 0.15s, transform 0.15s;
}
.guide-dot:hover {
  transform: scale(1.3);
}
.guide-dot.on {
  background: #2563eb;
  width: 18px;
  border-radius: 4px;
}
.guide-btns {
  display: flex;
  gap: 6px;
}
.guide-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 7px 12px;
  border-radius: 7px;
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
}
.guide-btn.ghost {
  background: #fff;
  color: #475569;
  border-color: #d8dfeb;
}
.guide-btn.ghost:hover:not(:disabled) {
  background: #f1f5f9;
  border-color: #94a3b8;
}
.guide-btn.ghost:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.guide-btn.primary {
  background: #2563eb;
  color: #fff;
}
.guide-btn.primary:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.35);
}

/* 다크 모드 자동 대응 */
@media (prefers-color-scheme: dark) {
  .guide-tip {
    background: #0f1c33;
    color: #e4eeff;
    border-color: rgba(96, 165, 250, 0.4);
  }
  .guide-tip-body {
    color: #cbd5e1;
  }
  .guide-tip-foot {
    background: #0a1426;
    border-top-color: rgba(255, 255, 255, 0.08);
  }
  .guide-btn.ghost {
    background: #1a2740;
    color: #cbd5e1;
    border-color: rgba(255, 255, 255, 0.12);
  }
  .guide-btn.ghost:hover:not(:disabled) {
    background: #243454;
  }
  .guide-dot {
    background: #475569;
  }
}

/* 트랜지션 */
.guide-fade-enter-active,
.guide-fade-leave-active {
  transition: opacity 0.22s;
}
.guide-fade-enter-from,
.guide-fade-leave-to {
  opacity: 0;
}
</style>
