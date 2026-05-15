<template>
  <div class="theme-navy" :class="{ light: !isDark }">
    <AppNav />
    <AppFab />

    <main class="content">
      <!-- HERO -->
      <section class="hero">
        <div class="hero-in">
          <div class="hero-left">
            <div class="hero-tag">ANNOUNCEMENTS</div>
            <h1>공지<em>사항</em></h1>
            <p class="hero-sub">
              최신 업데이트와 중요한 소식을 확인하세요.<br />
              운영 시간 안내와 함께 빠르고 정확한 정보를 제공합니다.
            </p>
            <div class="hero-channels">
              <div class="hch">
                <div class="hch-icon"><i class="bi bi-megaphone-fill"></i></div>
                <div class="hch-name">공지사항</div>
                <div class="hch-desc">최신 업데이트와{{ '\n' }}중요한 소식을 확인하세요.</div>
              </div>
              <div class="hch">
                <div class="hch-icon"><i class="bi bi-clock-fill"></i></div>
                <div class="hch-name">운영 시간</div>
                <div class="hch-desc">평일 09:00 - 18:00 (KST){{ '\n' }}주말 및 공휴일 휴무</div>
              </div>
            </div>
          </div>
          <div class="hero-right">
            <img src="/sub3.png" alt="공지사항" class="hero-img" />
          </div>
        </div>
      </section>

      <!-- MAIN: 게시판 -->
      <section class="sec">
        <div class="sw">
          <section class="panel">
            <div class="panel-inner">
              <BoardTab />
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

      <AppFooter />
    </main>
  </div>
</template>

<script setup>
import AppNav from "@/components/AppNav.vue";
import AppFab from "@/components/AppFab.vue";
import AppFooter from "@/components/AppFooter.vue";
import BoardTab from "@/components/BoardTab.vue";
import { useTheme } from "@/composables/useTheme";

const { isDark } = useTheme();

const values = [
  { icon: "bi bi-clock-history",         title: "빠른 응답",      desc: "실시간 모니터링으로 신속하게 확인하고 빠르게 답변합니다." },
  { icon: "bi bi-person-badge-fill",     title: "전문 기술 지원", desc: "교통 AI & 백엔드 전문가가 정확한 기술 지원을 제공합니다." },
  { icon: "bi bi-chat-square-dots-fill", title: "다양한 채널",    desc: "게시판, 공지사항으로 편리하게 정보를 전달합니다." },
  { icon: "bi bi-shield-lock-fill",      title: "안전한 서비스",  desc: "보안과 개인정보 보호를 최우선으로 안심하고 이용할 수 있습니다." },
];
</script>

<style scoped>
.content { padding-top: 68px; background: var(--bg); }

/* ───── HERO ───── */
.hero { background: var(--bg2); border-bottom: 1px solid var(--b); }
.hero-in {
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px 60px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr);
  gap: 0;
  align-items: center;
  height: 340px;
  max-height: 340px;
  overflow: hidden;
}
.hero-left { align-self: center; min-width: 0; }
.hero-tag {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 13px; font-weight: 600;
  letter-spacing: 0.14em;
  color: var(--a);
  margin-bottom: 10px;
}
.hero h1 {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: clamp(28px, 2.8vw, 38px);
  font-weight: 800; letter-spacing: -1.1px; line-height: 1.2;
  color: var(--t); margin: 0 0 12px;
}
.hero h1 em { color: var(--a); font-style: normal; }
.hero-sub {
  font-size: 13.5px; font-weight: 500;
  color: var(--t); opacity: 0.78;
  line-height: 1.65; margin: 0 0 18px;
  word-break: keep-all;
}
.hero-channels {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;
  max-width: 520px;
}
.hch { text-align: left; }
.hch-icon {
  width: 38px; height: 38px; border-radius: 10px;
  background: rgba(96, 165, 250, 0.12);
  display: inline-flex; align-items: center; justify-content: center;
  color: var(--a); font-size: 16px;
  margin-bottom: 8px;
}
.theme-navy.light .hch-icon { background: rgba(37, 99, 235, 0.1); }
.hch-name {
  font-size: 13.5px; font-weight: 700; color: var(--t);
  margin-bottom: 4px;
}
.hch-desc {
  font-size: 11.5px; color: var(--t); opacity: 0.62;
  line-height: 1.5; white-space: pre-line;
}

/* 우측 이미지 — 헤더 끝선부터 히어로 박스 끝선까지 세로 가득 */
.hero-right {
  position: relative;
  margin: -24px calc(60px - (50vw - 50%)) -24px 0;  /* 히어로 상하 패딩(24px) 무효화 */
  align-self: stretch;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  min-width: 0;
}
.hero-img {
  width: 100%;
  height: 100%;
  max-height: 100%;
  object-fit: contain;
  object-position: center center;
  display: block;
  --hero-mask: linear-gradient(to right,
    transparent 0%,
    rgba(0,0,0,0.5) 4%,
    rgba(0,0,0,0.9) 8%,
    #000 12%,
    #000 100%);
  -webkit-mask-image: var(--hero-mask);
  mask-image: var(--hero-mask);
}

/* ───── 공통 SECTION ───── */
.sec { padding: 60px 60px; }
.sw { max-width: 1440px; margin: 0 auto; }

/* ───── 게시판 패널 ───── */
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
.panel-inner :deep(> *) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.panel-inner :deep(.tbl) { flex: 1; min-height: 0; }

/* ───── VALUES ───── */
.values-sec { padding-top: 20px; padding-bottom: 80px; }
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

/* ───── RESPONSIVE ───── */
@media (max-width: 1100px) {
  .values-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .hero-in {
    grid-template-columns: 1fr;
    height: auto;
    padding: 50px 24px;
    gap: 30px;
  }
  .hero-right { margin-right: 0; }
  .hero-img { margin-left: 0; mask-image: none; -webkit-mask-image: none; max-height: 260px; }
  .sec { padding-left: 24px; padding-right: 24px; }
}
</style>
