<template>
  <div class="ds-wrap" ref="rootRef">
    <button class="ds-btn" @click.stop="open = !open"
      :aria-expanded="open" aria-haspopup="menu" aria-label="다른 부서 대시보드로 이동">
      <i class="bi bi-grid-3x3-gap-fill" aria-hidden="true"></i>
      <span>부서 이동</span>
      <i class="bi bi-chevron-down ds-chev" :class="{ on: open }" aria-hidden="true"></i>
    </button>
    <div v-if="open" class="ds-pop" role="menu">
      <div class="ds-h">다른 부서 대시보드</div>
      <RouterLink v-for="d in depts" :key="d.to"
        :to="d.to" class="ds-i" :class="{ cur: route.path === d.to }"
        role="menuitem" :aria-current="route.path === d.to ? 'page' : undefined"
        @click="open = false">
        <i :class="d.icon"></i>
        <div class="ds-body">
          <div class="ds-t">{{ d.name }}</div>
          <div class="ds-s">{{ d.desc }}</div>
        </div>
        <span v-if="route.path === d.to" class="ds-cur">현재</span>
        <i v-else class="bi bi-arrow-right ds-arr"></i>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { RouterLink, useRoute } from "vue-router";

const route = useRoute();
const open = ref(false);
const rootRef = ref(null);

const depts = [
  { to: "/admin/super",     name: "경영전략본부",   desc: "전사 통합 · KPI · 보고", icon: "bi bi-shield-lock-fill" },
  { to: "/admin/control",   name: "교통정보센터",   desc: "실시간 관제 · 이벤트", icon: "bi bi-broadcast" },
  { to: "/admin/review",    name: "단속관리팀",     desc: "위반 검토 · 판정",     icon: "bi bi-card-text" },
  { to: "/admin/analytics", name: "교통분석팀",     desc: "구간 분석 · 보고서",   icon: "bi bi-bar-chart-line" },
  { to: "/admin/ops",       name: "시설운영팀",     desc: "카메라 · 서버 · 망",   icon: "bi bi-hdd-stack" },
];

const onDocClick = (e) => {
  if (!open.value) return;
  if (rootRef.value && !rootRef.value.contains(e.target)) open.value = false;
};
const onKey = (e) => {
  if (e.key === "Escape" && open.value) open.value = false;
};
onMounted(() => {
  document.addEventListener("click", onDocClick);
  document.addEventListener("keydown", onKey);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocClick);
  document.removeEventListener("keydown", onKey);
});
</script>

<style scoped>
.ds-wrap { position: relative; }
.ds-btn {
  display: inline-flex; align-items: center; gap: 8px;
  background: #0f1d34; border: 1px solid #1f3055; color: #e4eeff;
  font-size: 12.5px; padding: 7px 12px; border-radius: 6px; cursor: pointer;
  font-family: inherit; font-weight: 600;
}
.ds-btn:hover { background: rgba(96,165,250,.08); border-color: rgba(96,165,250,.35); }
.ds-btn > i:first-child { color: #60a5fa; font-size: 13px; }
.ds-chev { font-size: 10px; opacity: .6; transition: transform .15s; }
.ds-chev.on { transform: rotate(180deg); }

.ds-pop {
  position: absolute; top: calc(100% + 6px); right: 0; z-index: 100;
  min-width: 320px;
  background: #0f1d34; border: 1px solid #1f3055; border-radius: 8px;
  box-shadow: 0 12px 32px rgba(0,0,0,.45); padding: 8px;
}
.ds-h { font-size: 10.5px; font-weight: 700; opacity: .55;
  padding: 6px 10px; text-transform: uppercase; letter-spacing: .04em; }
.ds-i {
  display: flex; align-items: center; gap: 10px; padding: 9px 10px;
  border-radius: 6px; color: #e4eeff; text-decoration: none; cursor: pointer;
  transition: background .15s;
}
.ds-i:hover { background: rgba(96,165,250,.08); }
.ds-i.cur { background: rgba(96,165,250,.06); }
.ds-i > i:first-child { font-size: 16px; color: #60a5fa; width: 18px; text-align: center; }
.ds-body { flex: 1; min-width: 0; }
.ds-t { font-size: 12.5px; font-weight: 700; }
.ds-s { font-size: 10.5px; opacity: .55; margin-top: 1px; }
.ds-arr { font-size: 11px; opacity: .4; }
.ds-cur { font-size: 10px; font-weight: 700; padding: 2px 7px;
  background: rgba(52,211,153,.15); color: #34d399; border-radius: 100px; }
.ds-sep { height: 1px; background: #1f3055; margin: 6px 4px; }
.ds-i.sm .ds-t { font-size: 12px; }
</style>
