<template>
  <div class="theme-navy" :class="{ light: !isDark }">
    <AppNav @goChat="tab = 'chat'" />
    <AppFab />

    <main class="content">
      <!-- HERO -->
      <section class="hero">
        <div class="hero-in">
          <div class="hero-left">
            <div class="hero-tag">CUSTOMER SUPPORT</div>
            <h1>고객 <em>지원</em></h1>
            <p class="hero-sub">
              공지사항, Q&amp;A, 실시간 채팅으로 빠르게 도와드리겠습니다.<br />
              궁금한 점이 있으시면 언제든지 문의해주세요.
            </p>
            <div class="hero-channels">
              <div v-for="ch in channels" :key="ch.key" class="hch">
                <div class="hch-icon"><i :class="ch.icon"></i></div>
                <div class="hch-name">{{ ch.name }}</div>
                <div class="hch-desc">{{ ch.heroDesc }}</div>
              </div>
            </div>
          </div>
          <div class="hero-right">
            <img src="/support_headset_hero.png" alt="고객 지원 헤드셋" class="hero-img" />
          </div>
        </div>
      </section>

      <!-- MAIN: 사이드바 + 콘텐츠 -->
      <section class="sec">
        <div class="sw layout">
          <aside class="sidebar">
            <button
              v-for="ch in channels"
              :key="ch.key"
              class="sb-item"
              :class="{ on: tab === ch.key }"
              @click="ch.key === 'hours' ? null : (tab = ch.key)"
              :disabled="ch.key === 'hours'"
            >
              <div class="sb-icon"><i :class="ch.icon"></i></div>
              <div class="sb-body">
                <div class="sb-row">
                  <span class="sb-name">{{ ch.name }}</span>
                  <span v-if="ch.live" class="sb-badge live">Live</span>
                </div>
                <div class="sb-desc">{{ ch.sidebarDesc }}</div>
              </div>
            </button>
          </aside>

          <section class="panel">
            <div class="panel-inner">
              <BoardTab v-if="tab === 'board'" />
              <QnaTab v-if="tab === 'qna'" />
              <ChatTab v-if="tab === 'chat'" />
            </div>
          </section>
        </div>
      </section>

      <!-- VALUES -->
      <section class="sec values-sec">
        <div class="sw">
          <div class="values-head">
            <span class="values-line"></span>
            <h2>Traffic AS가 제공하는 가치</h2>
          </div>
          <div class="values-grid">
            <div v-for="v in values" :key="v.title" class="value-card">
              <div class="value-icon"><i :class="v.icon"></i></div>
              <div class="value-title">{{ v.title }}</div>
              <p class="value-desc">{{ v.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- CHAT CTA -->
      <section class="cta-wrap">
        <div class="sw">
          <div class="cta-card">
            <div class="cta-icon"><i class="bi bi-headset"></i></div>
            <div class="cta-text">
              <h3>도움이 필요하신가요?</h3>
              <p>실시간 채팅으로 운영팀과 바로 연결되어 빠르게 해결해 드리겠습니다.</p>
            </div>
            <button class="cta-btn" @click="tab = 'chat'">
              <i class="bi bi-chat-dots-fill"></i> 실시간 채팅 시작
            </button>
          </div>
        </div>
      </section>

      <AppFooter />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import AppNav from "@/components/AppNav.vue";
import AppFab from "@/components/AppFab.vue";
import AppFooter from "@/components/AppFooter.vue";
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
    icon: "bi bi-megaphone-fill",
    name: "공지사항",
    heroDesc: "최신 업데이트와\n중요한 소식을 확인하세요.",
    sidebarDesc: "공지사항, 사용 후기,\n중요한 소식을 공유하세요.",
    live: false,
  },
  {
    key: "qna",
    icon: "bi bi-patch-question-fill",
    name: "질문 & 답변",
    heroDesc: "기술적인 질문은 전문가가\n신속히 답변드립니다.",
    sidebarDesc: "기술적인 질문을 올리면\n전문 답변을 받습니다.",
    live: false,
  },
  {
    key: "chat",
    icon: "bi bi-chat-dots-fill",
    name: "실시간 채팅",
    heroDesc: "운영팀과 실시간으로\n즉시 소통하세요.",
    sidebarDesc: "운영팀과 실시간으로\n즉시 소통합니다.",
    live: true,
  },
  {
    key: "hours",
    icon: "bi bi-clock-fill",
    name: "운영 시간",
    heroDesc: "평일 09:00 - 18:00 (KST)\n주말 및 공휴일 휴무",
    sidebarDesc: "평일 09:00 - 18:00 (KST)\n* 주말 및 공휴일 휴무",
    live: false,
  },
];

const values = [
  { icon: "bi bi-clock-history",    title: "빠른 응답",      desc: "실시간 모니터링으로 신속하게 확인하고 빠르게 답변합니다." },
  { icon: "bi bi-person-badge-fill", title: "전문 기술 지원", desc: "교통 AI & 백엔드 전문가가 정확한 기술 지원을 제공합니다." },
  { icon: "bi bi-chat-square-dots-fill", title: "다양한 채널", desc: "게시판, Q&A, 실시간 채팅으로 편리하게 문의하세요." },
  { icon: "bi bi-shield-lock-fill", title: "안전한 서비스",  desc: "보안과 개인정보 보호를 최우선으로 안심하고 이용할 수 있습니다." },
];

onMounted(() => {
  if (route.query.tab) tab.value = route.query.tab;
});
watch(
  () => route.query.tab,
  (v) => { if (v) tab.value = v; }
);
</script>

<style scoped>
.content { padding-top: 68px; background: var(--bg); }

/* ───── HERO ───── */
.hero { background: var(--bg2); border-bottom: 1px solid var(--b); }
.hero-in {
  max-width: 1440px;
  margin: 0 auto;
  padding: 70px 60px 60px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.1fr);
  gap: 0;
  align-items: stretch;
  height: 480px;          /* 박스 사이즈 고정 — 이미지 커져도 박스 안 늘어남 */
  box-sizing: content-box;
}
.hero-left { align-self: center; }
.hero-tag {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 16px; font-weight: 600;
  letter-spacing: 0.16em;
  color: var(--a);
  margin-bottom: 18px;
}
.hero h1 {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: clamp(40px, 4.4vw, 60px);
  font-weight: 800; letter-spacing: -1.8px; line-height: 1.15;
  color: var(--t); margin: 0 0 22px;
}
.hero h1 em { color: var(--a); font-style: normal; }
.hero-sub {
  font-size: 16.5px; font-weight: 500;
  color: var(--t); opacity: 0.78;
  line-height: 1.75; margin: 0 0 36px;
  word-break: keep-all;
}
.hero-channels {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
  max-width: 680px;
}
.hch { text-align: left; }
.hch-icon {
  width: 46px; height: 46px; border-radius: 12px;
  background: rgba(96, 165, 250, 0.12);
  display: inline-flex; align-items: center; justify-content: center;
  color: var(--a); font-size: 20px;
  margin-bottom: 12px;
}
.theme-navy.light .hch-icon { background: rgba(37, 99, 235, 0.1); }
.hch-name {
  font-size: 14.5px; font-weight: 700; color: var(--t);
  margin-bottom: 4px;
}
.hch-desc {
  font-size: 12px; color: var(--t); opacity: 0.62;
  line-height: 1.5; white-space: pre-line;
}
/* 우측 이미지 — 화면 우측 끝까지 */
.hero-right {
  position: relative;
  margin-right: calc(60px - (50vw - 50%));
  align-self: stretch;
  display: flex;
  align-items: stretch;
  justify-content: center;
  overflow: visible;
}
.hero-img {
  width: auto;
  height: 100%;            /* 고정 박스 높이에 맞춰 채움 */
  max-height: 100%;
  max-width: 100%;
  object-fit: contain;
  flex-shrink: 0;
  display: block;
  margin-left: -80px;
  filter: drop-shadow(0 20px 40px rgba(15, 40, 90, 0.18));
  --hero-mask: linear-gradient(to right,
    transparent 0%,
    rgba(0,0,0,0.4) 4%,
    rgba(0,0,0,0.85) 8%,
    #000 12%,
    #000 100%);
  -webkit-mask-image: var(--hero-mask);
  mask-image: var(--hero-mask);
}

/* ───── 공통 SECTION ───── */
.sec { padding: 60px 60px; }
.sw { max-width: 1440px; margin: 0 auto; }

/* ───── 사이드바 + 콘텐츠 레이아웃 ───── */
.layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 32px;
  align-items: start;
}
.sidebar {
  display: flex; flex-direction: column; gap: 14px;
}
.sb-item {
  width: 100%;
  text-align: left;
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 14px;
  padding: 18px 18px;
  cursor: pointer;
  transition: all 0.18s;
  display: flex; align-items: flex-start; gap: 14px;
}
.theme-navy.light .sb-item { background: #fff; box-shadow: 0 2px 12px rgba(15, 40, 90, 0.04); }
.sb-item:hover {
  border-color: var(--ba);
  transform: translateY(-1px);
}
.sb-item.on {
  border-color: var(--a);
  box-shadow: 0 6px 24px rgba(37, 99, 235, 0.15);
}
.theme-navy.light .sb-item.on { box-shadow: 0 6px 24px rgba(37, 99, 235, 0.12); }
.sb-item[disabled] { cursor: default; }
.sb-icon {
  width: 40px; height: 40px; border-radius: 10px;
  background: rgba(96, 165, 250, 0.12);
  display: inline-flex; align-items: center; justify-content: center;
  color: var(--a); font-size: 18px;
  flex-shrink: 0;
}
.theme-navy.light .sb-icon { background: rgba(37, 99, 235, 0.08); }
.sb-body { flex: 1; min-width: 0; }
.sb-row {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 6px;
}
.sb-name {
  font-size: 15.5px; font-weight: 700;
  color: var(--t);
}
.sb-badge.live {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11.5px; font-weight: 700;
  background: rgba(52, 211, 153, 0.14);
  color: #34d399;
  padding: 2px 8px; border-radius: 100px;
}
.sb-badge.live::before {
  content: "";
  width: 5px; height: 5px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 6px #34d399;
}
.sb-desc {
  font-size: 12.5px; color: var(--t); opacity: 0.6;
  line-height: 1.55; white-space: pre-line;
}

.panel {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 16px;
  padding: 32px 36px;
  min-height: 720px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.theme-navy.light .panel { background: #fff; box-shadow: 0 4px 20px rgba(15, 40, 90, 0.04); }
.panel-inner {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
/* 게시판/Q&A/채팅 자식 컴포넌트가 박스를 가득 채우도록 */
.panel-inner :deep(> *) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.panel-inner :deep(.tbl) { flex: 1; min-height: 0; }

/* ───── VALUES ───── */
.values-sec { padding-top: 20px; }
.values-head {
  display: flex; align-items: center; gap: 14px;
  margin-bottom: 28px;
}
.values-line {
  width: 36px; height: 2px;
  background: var(--a);
  display: block;
}
.values-head h2 {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 22px; font-weight: 800;
  letter-spacing: -0.5px;
  color: var(--t); margin: 0;
}
.values-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;
}
.value-card {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 14px;
  padding: 28px 24px;
  transition: all 0.2s;
}
.theme-navy.light .value-card { background: #fff; box-shadow: 0 2px 14px rgba(15, 40, 90, 0.04); }
.value-card:hover {
  border-color: var(--ba);
  transform: translateY(-3px);
  box-shadow: 0 14px 32px rgba(96, 165, 250, 0.12);
}
.value-icon {
  width: 56px; height: 56px; border-radius: 50%;
  background: rgba(96, 165, 250, 0.12);
  display: inline-flex; align-items: center; justify-content: center;
  color: var(--a); font-size: 24px;
  margin-bottom: 18px;
}
.theme-navy.light .value-icon { background: rgba(37, 99, 235, 0.08); }
.value-title {
  font-size: 17px; font-weight: 700;
  color: var(--t); margin-bottom: 8px;
}
.value-desc {
  font-size: 14px; font-weight: 500;
  color: var(--t); opacity: 0.7;
  line-height: 1.65;
  margin: 0;
  word-break: keep-all;
}

/* ───── CTA ───── */
.cta-wrap { padding: 30px 60px 80px; }
.cta-card {
  background: rgba(96, 165, 250, 0.06);
  border: 1px solid rgba(96, 165, 250, 0.18);
  border-radius: 18px;
  padding: 28px 36px;
  display: flex; align-items: center; gap: 24px;
}
.theme-navy.light .cta-card {
  background: rgba(37, 99, 235, 0.05);
  border-color: rgba(37, 99, 235, 0.15);
}
.cta-icon {
  width: 64px; height: 64px; border-radius: 50%;
  background: rgba(96, 165, 250, 0.18);
  display: inline-flex; align-items: center; justify-content: center;
  color: var(--a); font-size: 28px;
  flex-shrink: 0;
}
.theme-navy.light .cta-icon { background: rgba(37, 99, 235, 0.12); }
.cta-text { flex: 1; min-width: 0; }
.cta-text h3 {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 20px; font-weight: 800;
  letter-spacing: -0.4px;
  color: var(--t); margin: 0 0 6px;
}
.cta-text p {
  font-size: 14.5px; font-weight: 500;
  color: var(--t); opacity: 0.72;
  margin: 0;
}
.cta-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 14px 24px;
  background: var(--a);
  color: #fff;
  border: 0;
  border-radius: 10px;
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 15px; font-weight: 700;
  cursor: pointer;
  transition: opacity 0.18s, transform 0.18s;
  white-space: nowrap;
  flex-shrink: 0;
}
.cta-btn:hover {
  opacity: 0.92;
  transform: translateY(-2px);
}

/* ───── RESPONSIVE ───── */
@media (max-width: 1100px) {
  .hero-channels { grid-template-columns: repeat(2, 1fr); }
  .layout { grid-template-columns: 1fr; }
  .values-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .hero-in { grid-template-columns: 1fr; padding: 50px 24px; gap: 30px; }
  .hero-channels { grid-template-columns: repeat(2, 1fr); }
  .sec, .cta-wrap { padding-left: 24px; padding-right: 24px; }
  .cta-card { flex-direction: column; align-items: flex-start; padding: 24px; }
}
</style>
