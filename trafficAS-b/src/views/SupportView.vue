<template>
  <div class="theme-navy" :class="{ light: !isDark }">
    <AppNav @goChat="tab = 'chat'" />
    <AppFab />

    <main class="content">
      <!-- Header -->
      <div class="ph">
        <div class="ph-ey">CUSTOMER SUPPORT</div>
        <h1>고객 <em>지원</em></h1>
        <p class="ph-sub">게시판, Q&A, 실시간 채팅으로 도움을 드립니다.</p>
      </div>

      <div class="layout">
        <!-- Sidebar -->
        <aside class="sidebar">
          <nav class="sb-nav">
            <button
              class="sb-item"
              v-for="ch in channels"
              :key="ch.key"
              :class="{ on: tab === ch.key }"
              @click="tab = ch.key"
            >
              <div class="sb-item-top">
                <span class="sb-tag">{{ ch.tag }}</span>
                <span class="sb-badge" :class="{ live: ch.live }">{{ ch.badge }}</span>
              </div>
              <div class="sb-name">{{ ch.name }}</div>
              <div class="sb-desc">{{ ch.desc }}</div>
            </button>
          </nav>

          <div class="sb-footer">
            <div class="st-row">
              <span class="st-dot"></span>
              <span class="st-text">6명 접속 중</span>
              <span class="st-sep">·</span>
              <span class="st-meta">실시간</span>
            </div>
            <div class="st-copy">© 2026 네바퀴 1조 · 스마트 모빌리티 DX Academy</div>
          </div>
        </aside>

        <!-- Content Panel -->
        <section class="panel">
          <div class="panel-head">
            <div class="ph-info">
              <span class="ph-tag">{{ active?.tag }}</span>
              <span class="ph-name">{{ active?.name }}</span>
            </div>
            <div class="ph-desc">{{ active?.desc }}</div>
          </div>
          <div class="panel-body" :class="{ 'chat-mode': tab === 'chat' }">
            <BoardTab v-if="tab === 'board'" />
            <QnaTab v-if="tab === 'qna'" />
            <ChatTab v-if="tab === 'chat'" />
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import AppNav from "@/components/AppNav.vue";
import AppFab from "@/components/AppFab.vue";
import BoardTab from "@/components/BoardTab.vue";
import QnaTab from "@/components/QnaTab.vue";
import ChatTab from "@/components/ChatTab.vue";
import { useTheme } from "@/composables/useTheme";

const { isDark } = useTheme();
const route = useRoute();
const tab = ref("board");

const channels = [
  {
    key: "board",
    tag: "BOARD",
    name: "게시판",
    desc: "공지사항, 사용 후기, 활용 사례를 공유합니다.",
    badge: "6",
    live: false,
  },
  {
    key: "qna",
    tag: "Q&A",
    name: "질문 & 답변",
    desc: "기술적인 질문을 올리고 전문 답변을 받습니다.",
    badge: "5",
    live: false,
  },
  {
    key: "chat",
    tag: "LIVE CHAT",
    name: "실시간 채팅",
    desc: "운영팀과 실시간으로 즉시 소통합니다.",
    badge: "Live",
    live: true,
  },
];

const active = computed(() => channels.find((c) => c.key === tab.value));

onMounted(() => {
  if (route.query.tab) tab.value = route.query.tab;
});
watch(
  () => route.query.tab,
  (v) => {
    if (v) tab.value = v;
  }
);
</script>

<style scoped>
.content {
  padding-top: 62px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Header (사용법/시스템소개와 동일) ── */
.ph {
  padding: 64px 60px 52px;
  border-bottom: 1px solid var(--b);
  background: var(--bg2);
  flex-shrink: 0;
}
.ph-ey {
  font-family: "JetBrains Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.22em;
  color: var(--a);
  opacity: 0.6;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.ph-ey::before {
  content: "";
  width: 14px;
  height: 1px;
  background: var(--a);
  opacity: 0.5;
}
h1 {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: clamp(36px, 5vw, 68px);
  font-weight: 800;
  letter-spacing: -3px;
  color: var(--t);
  line-height: 0.95;
  margin-bottom: 16px;
}
h1 em {
  color: var(--a);
  font-style: normal;
}
.ph-sub {
  font-size: 13px;
  color: var(--t2);
  font-weight: 300;
  line-height: 1.85;
  max-width: 600px;
  margin-bottom: 20px;
  margin-top: 16px;
}

.layout {
  flex: 1;
  display: flex;
  min-height: 0;
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  width: 272px;
  flex-shrink: 0;
  border-right: 1px solid var(--b);
  background: var(--bg2);
  display: flex;
  flex-direction: column;
  padding: 24px 24px 28px;
  overflow-y: auto;
}

/* Nav items */
.sb-nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.sb-item {
  width: 100%;
  text-align: left;
  background: transparent;
  border: 1px solid var(--b);
  border-radius: 8px;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  border-left: 2px solid transparent;
}
.sb-item:hover {
  background: rgba(255, 255, 255, 0.03);
  border-color: var(--ba);
}
.sb-item.on {
  background: rgba(96, 165, 250, 0.05);
  border-color: rgba(96, 165, 250, 0.25);
  border-left-color: var(--a);
}

.sb-item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 5px;
}
.sb-tag {
  font-family: "JetBrains Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.12em;
  color: var(--a);
  opacity: 0.55;
}
.sb-item.on .sb-tag {
  opacity: 1;
}

.sb-badge {
  font-family: "JetBrains Mono", monospace;
  font-size: 9px;
  background: rgba(96, 165, 250, 0.1);
  color: var(--a);
  padding: 1px 7px;
  border-radius: 100px;
}
.sb-badge.live {
  background: rgba(52, 211, 153, 0.12);
  color: #34d399;
}

.sb-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--t);
  margin-bottom: 3px;
}
.sb-desc {
  font-size: 11px;
  color: var(--t3);
  font-weight: 300;
  line-height: 1.55;
}

/* Sidebar footer */
.sb-footer {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid var(--b);
}
.st-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}
.st-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #34d399;
  flex-shrink: 0;
  animation: livePulse 1.5s ease-in-out infinite;
}
.st-text {
  font-family: "JetBrains Mono", monospace;
  font-size: 10px;
  color: #34d399;
}
.st-sep {
  font-size: 10px;
  color: var(--t3);
}
.st-meta {
  font-family: "JetBrains Mono", monospace;
  font-size: 10px;
  color: var(--t3);
}
.st-copy {
  font-family: "JetBrains Mono", monospace;
  font-size: 9px;
  color: var(--t3);
  opacity: 0.5;
  line-height: 1.5;
}

/* ── Content Panel ── */
.panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.panel-head {
  padding: 20px 36px;
  border-bottom: 1px solid var(--b);
  background: var(--bg2);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.ph-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ph-tag {
  font-family: "JetBrains Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.14em;
  color: var(--a);
  opacity: 0.6;
}
.ph-name {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--t);
}
.ph-desc {
  font-size: 11px;
  color: var(--t3);
  font-weight: 300;
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 28px 36px;
}
.panel-body.chat-mode {
  padding: 0;
  overflow: hidden;
}
.panel-body::-webkit-scrollbar {
  width: 3px;
}
.panel-body::-webkit-scrollbar-thumb {
  background: var(--b);
  border-radius: 2px;
}

@media (max-width: 768px) {
  .content {
    height: auto;
    overflow: auto;
  }
  .ph {
    padding: 40px 20px 32px;
  }
  .layout {
    flex-direction: column;
    min-height: 0;
    overflow: auto;
  }
  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--b);
    padding: 20px;
  }
  .sb-nav {
    flex-direction: row;
    overflow-x: auto;
    gap: 8px;
  }
  .sb-item {
    min-width: 160px;
  }
  .sb-footer {
    display: none;
  }
  .panel-body {
    padding: 20px;
  }
  .panel-body.chat-mode {
    padding: 0;
  }
}
</style>
