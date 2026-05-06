<template>
  <div class="theme-navy" :class="{ light: !isDark }">
    <AppNav />
    <AppFab />

    <div class="hero">
      <div class="hfb"></div>
      <video class="hvid" autoplay muted loop playsinline poster="/hero-poster.jpg">
        <source src="/hero-main.mp4" type="video/mp4" />
        <source src="/hero-alt.mp4" type="video/mp4" />
        <source src="/hero-banner.mp4" type="video/mp4" />
      </video>
      <div class="hdim"></div>
      <div class="hacc"></div>
      <div class="hcopy">
        <div class="ey">스마트 모빌리티 DX ACADEMY · 네바퀴 1조</div>
        <h1>차량이 움직이는<br />모든 순간을<br /><em>포착합니다.</em></h1>
        <p class="hdesc">
          YOLO 기반 실시간 차량 감지와 번호판 OCR로 교통 흐름을 분석합니다.
        </p>
      </div>
      <HeroStats :stats="stats" variant="navy" />
    </div>

    <!-- 시스템 소개 + 비디오 3개 -->
    <section class="sec bg2">
      <div class="sw">
        <div class="ey-tag">SYSTEM INTRO</div>
        <h2>시스템 <em>소개</em></h2>
        <p class="desc">
          AI 차량 감지부터 데이터 집계까지, TrafficAS의 핵심 기술 구조를 소개합니다.
        </p>
        <div class="vintro fu" ref="fuRef1">
          <div class="vstack">
            <div class="vmain">
              <video autoplay muted loop playsinline>
                <source src="/hero-main.mp4" type="video/mp4" />
                <source src="/hero-banner.mp4" type="video/mp4" />
              </video>
              <div class="vovl">
                <span class="vbg"><span class="vdot in"></span>YOLO DETECTING</span>
                <span class="vcnt"
                  >{{ stats[0]?.display }}<span class="vu">대</span></span
                >
              </div>
            </div>
            <div class="vrow">
              <div class="vsm">
                <video autoplay muted loop playsinline>
                  <source src="/detect-video.mp4" type="video/mp4" />
                </video>
                <div class="vslbl">
                  <span class="vdot in" style="animation-delay: 0.3s"></span>INCIDENT
                </div>
              </div>
              <div class="vsm">
                <video autoplay muted loop playsinline>
                  <source src="/classify-video.mp4" type="video/mp4" />
                  <source src="/hero-alt.mp4" type="video/mp4" />
                </video>
                <div class="vslbl"><span class="vdot"></span>CLASSIFY</div>
              </div>
            </div>
          </div>
          <div class="vright">
            <div class="vi" v-for="item in introItems" :key="item.num">
              <div class="vi-n">{{ item.num }}</div>
              <div class="vi-t">{{ item.title }}</div>
              <div class="vi-d">{{ item.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- FEATURES -->
    <section class="sec">
      <div class="sw">
        <div class="ey-tag">CORE FEATURES</div>
        <h2>핵심 <em>기능</em></h2>
        <p class="desc">실시간 AI 감지부터 데이터 집계까지.</p>
        <div class="fg fu" ref="fuRef2">
          <div class="fc" v-for="f in features" :key="f.tag">
            <div class="ft">{{ f.tag }}</div>
            <div class="ftt">{{ f.title }}</div>
            <div class="fd">{{ f.desc }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <div class="cta-wrap">
      <div class="cta-in">
        <div>
          <h2>더 자세히 알아보시겠어요?</h2>
          <p class="desc" style="margin-bottom: 0">
            사용법, DB 구조, 게시판·Q&A·실시간 채팅까지 서브 페이지에서 확인하세요.
          </p>
        </div>
        <div class="cta-btns">
          <RouterLink to="/sub" class="btn-a">→ 서브 페이지 보기</RouterLink>
        </div>
      </div>
    </div>

    <div class="sbar">
      <div
        class="sw"
        style="display: flex; align-items: center; gap: 36px; flex-wrap: wrap"
      >
        <span class="slbl">TECH STACK</span>
        <div class="chips">
          <span class="chip" v-for="c in stack" :key="c">{{ c }}</span>
        </div>
      </div>
    </div>

    <footer>
      <span class="fl">Traffic<em>AS</em></span>
      <span class="fr">© 2025 네바퀴 1조 · 스마트 모빌리티 DX Academy</span>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { RouterLink } from "vue-router";
import AppNav from "@/components/AppNav.vue";
import AppFab from "@/components/AppFab.vue";
import HeroStats from "@/components/HeroStats.vue";
import { useStats } from "@/composables/useStats";
import { useTheme } from "@/composables/useTheme";

const { stats } = useStats();
const { isDark } = useTheme();
const fuRef1 = ref(null);
const fuRef2 = ref(null);

onMounted(() => {
  const obs = new IntersectionObserver(
    (entries) =>
      entries.forEach((e) => {
        if (e.isIntersecting) e.target.classList.add("v");
      }),
    { threshold: 0.1 }
  );
  [fuRef1.value, fuRef2.value].forEach((el) => el && obs.observe(el));
});

const introItems = [
  {
    num: "01 — AI ENGINE",
    title: "YOLOv8n 실시간 감지",
    desc: "초당 30프레임으로 차량 감지. 세단·SUV·트럭·버스 분류 및 신뢰도 반환.",
  },
  {
    num: "02 — OCR MODULE",
    title: "EasyOCR 번호판 인식",
    desc: "번호판 영역 크롭 후 OCR 인식. 96.2% 이상 정확도.",
  },
];
const features = [
  {
    tag: "01 — DETECT",
    title: "YOLOv8 차량 감지",
    desc: "초당 30프레임 실시간 감지. 다중 차량 동시 추적.",
  },
  {
    tag: "02 — OCR",
    title: "번호판 인식",
    desc: "EasyOCR 기반. 96% 이상 정확도 입·출차 자동 식별.",
  },
  {
    tag: "03 — ANALYTICS",
    title: "유입·유출 분석",
    desc: "구역별 실시간 집계. 시간대별 밀도 시각화.",
  },
  {
    tag: "04 — REALTIME",
    title: "WebSocket 실시간",
    desc: "50ms 이내 응답. FastAPI → Vue.js 즉시 렌더링.",
  },
];
const stack = [
  "FastAPI",
  "YOLOv8n",
  "EasyOCR",
  "Spring Boot",
  "Vue.js 3",
  "PostgreSQL",
  "WebSocket",
  "Docker",
];
</script>

<style scoped>
.hero {
  position: relative;
  height: 100vh;
  min-height: 700px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}
.hvid {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}
.hfb {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: radial-gradient(
      ellipse 75% 55% at 62% 32%,
      rgba(10, 40, 90, 0.55),
      transparent 55%
    ),
    linear-gradient(162deg, #020b18, #05152a 50%, #020b18);
}
.hfb::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(96, 165, 250, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(96, 165, 250, 0.03) 1px, transparent 1px);
  background-size: 52px 52px;
}
.hdim {
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(
      to right,
      #020b18 0%,
      rgba(2, 11, 24, 0.7) 12%,
      rgba(2, 11, 24, 0.2) 28%,
      transparent 45%
    ),
    linear-gradient(
      to left,
      #020b18 0%,
      rgba(2, 11, 24, 0.7) 12%,
      rgba(2, 11, 24, 0.2) 28%,
      transparent 45%
    ),
    linear-gradient(
      to top,
      #020b18 0%,
      rgba(2, 11, 24, 0.55) 18%,
      rgba(2, 11, 24, 0.08) 50%,
      rgba(2, 11, 24, 0.25) 100%
    );
}
.light .hfb {
  background: linear-gradient(162deg, #dde8f4, #e8eff8 50%, #dde8f4);
}
.light .hfb::before {
  background-image: linear-gradient(rgba(37, 99, 235, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(37, 99, 235, 0.03) 1px, transparent 1px);
}
.light .hdim {
  background: linear-gradient(
      to right,
      rgba(241, 245, 251, 0.72) 0%,
      rgba(241, 245, 251, 0.18) 12%,
      transparent 28%
    ),
    linear-gradient(
      to left,
      rgba(241, 245, 251, 0.72) 0%,
      rgba(241, 245, 251, 0.18) 12%,
      transparent 28%
    ),
    linear-gradient(
      to top,
      rgba(241, 245, 251, 0.82) 0%,
      rgba(241, 245, 251, 0.18) 10%,
      transparent 24%
    );
}
.hacc {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  z-index: 2;
  background: linear-gradient(to bottom, transparent, var(--a), transparent);
}
.hcopy {
  position: absolute;
  top: 50%;
  left: 60px;
  transform: translateY(-52%);
  z-index: 2;
  max-width: 600px;
}
.ey {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--a);
  opacity: 0.7;
  margin-bottom: 22px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.ey::before {
  content: "";
  width: 22px;
  height: 1px;
  background: var(--a);
  opacity: 0.5;
}
h1 {
  font-family: "Syne", sans-serif;
  font-size: clamp(40px, 5vw, 90px);
  font-weight: 800;
  line-height: 1.25;
  letter-spacing: -3.5px;
  color: var(--t);
  margin-bottom: 24px;
}
h1 em {
  color: var(--a);
  font-style: normal;
}
.hdesc {
  font-size: 15px;
  font-weight: 300;
  color: var(--t2);
  line-height: 1.82;
  max-width: 440px;
}
.sec {
  padding: 88px 60px;
  border-top: 1px solid var(--b);
}
.bg2 {
  background: var(--bg2);
}
.sw {
  max-width: 1440px;
  margin: 0 auto;
}
.ey-tag {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--a);
  opacity: 0.6;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.ey-tag::before {
  content: "";
  width: 14px;
  height: 1px;
  background: var(--a);
  opacity: 0.5;
}
h2 {
  font-family: "Syne", sans-serif;
  font-size: clamp(26px, 3.5vw, 44px);
  font-weight: 800;
  letter-spacing: -1.5px;
  margin-bottom: 10px;
  color: var(--t);
}
h2 em {
  color: var(--a);
  font-style: normal;
}
.desc {
  font-size: 14px;
  font-weight: 300;
  color: var(--t2);
  line-height: 1.85;
  max-width: 540px;
  margin-bottom: 48px;
}
/* 비디오 3개 레이아웃 */
.vintro {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: start;
}
.vstack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.vmain {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--b);
  position: relative;
}
.vmain video {
  width: 100%;
  aspect-ratio: 16/9;
  object-fit: cover;
  display: block;
}
.vovl {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(2, 11, 24, 0.85), transparent);
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}
.vbg {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.1em;
  color: var(--a);
  display: flex;
  align-items: center;
  gap: 5px;
}
.vcnt {
  font-family: "Syne", sans-serif;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -1px;
  color: #fff;
}
.vu {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin-left: 3px;
}
.vrow {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.vsm {
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--b);
  position: relative;
}
.vsm video {
  width: 100%;
  aspect-ratio: 16/9;
  object-fit: cover;
  display: block;
}
.vslbl {
  position: absolute;
  top: 7px;
  left: 8px;
  font-family: "IBM Plex Mono", monospace;
  font-size: 8px;
  letter-spacing: 0.1em;
  color: var(--a);
  background: rgba(0, 0, 0, 0.45);
  padding: 2px 7px;
  border-radius: 2px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.vdot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--a);
  animation: livePulse 1.5s ease-in-out infinite;
}
.vdot.in {
  background: var(--in);
}
.vright {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.vi {
  padding: 20px 0;
  border-bottom: 1px solid var(--b);
  transition: padding-left 0.2s;
}
.vi:hover {
  padding-left: 6px;
}
.vi:last-child {
  border-bottom: none;
}
.vi-n {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.14em;
  color: var(--a);
  opacity: 0.55;
  margin-bottom: 6px;
}
.vi-t {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 5px;
  color: var(--t);
}
.vi-d {
  font-size: 13px;
  color: var(--t2);
  line-height: 1.75;
  font-weight: 300;
}
/* FEATURES */
.fg {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.fc {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 8px;
  padding: 28px 22px;
  transition: all 0.22s;
  cursor: default;
}
.fc:hover {
  border-color: var(--ba);
  transform: translateY(-3px);
}
.ft {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.14em;
  color: var(--a);
  opacity: 0.5;
  margin-bottom: 9px;
}
.ftt {
  font-family: "Syne", sans-serif;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.3px;
  margin-bottom: 8px;
  color: var(--t);
}
.fd {
  font-size: 12px;
  color: var(--t2);
  line-height: 1.75;
  font-weight: 300;
}
/* CTA / STACK / TEAM / FOOTER */
.cta-wrap {
  border-top: 1px solid var(--b);
  background: var(--bg2);
}
.cta-in {
  max-width: 1440px;
  margin: 0 auto;
  padding: 60px 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
  flex-wrap: wrap;
}
.cta-btns {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.btn-a {
  display: inline-flex;
  align-items: center;
  padding: 12px 24px;
  background: var(--a);
  color: var(--bg);
  font-family: "Syne", sans-serif;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  border-radius: 6px;
  transition: opacity 0.2s, transform 0.15s;
}
.btn-a:hover {
  opacity: 0.87;
  transform: translateY(-1px);
}
.btn-g {
  display: inline-flex;
  align-items: center;
  padding: 12px 24px;
  border: 1px solid var(--b);
  color: var(--t2);
  font-size: 12px;
  letter-spacing: 0.04em;
  border-radius: 6px;
  transition: all 0.2s;
}
.btn-g:hover {
  border-color: var(--ba);
  color: var(--a);
}
.sbar {
  padding: 28px 60px;
  border-top: 1px solid var(--b);
  background: var(--bg2);
}
.slbl {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--t3);
  white-space: nowrap;
}
.chips {
  display: flex;
  gap: 7px;
  flex-wrap: wrap;
}
.chip {
  font-family: "IBM Plex Mono", monospace;
  font-size: 10px;
  padding: 5px 12px;
  border: 1px solid var(--b);
  border-radius: 5px;
  color: var(--t2);
  transition: all 0.2s;
}
.chip:hover {
  border-color: var(--ba);
  color: var(--a);
}
footer {
  border-top: 1px solid var(--b);
  padding: 26px 60px;
  background: var(--bg2);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.fl {
  font-family: "Syne", sans-serif;
  font-size: 15px;
  font-weight: 800;
  letter-spacing: -0.3px;
  color: var(--t);
}
.fl em {
  color: var(--a);
  font-style: normal;
}
.fr {
  font-family: "IBM Plex Mono", monospace;
  font-size: 10px;
  color: var(--t3);
}
@media (max-width: 768px) {
  .sec,
  .cta-in,
  .sbar,
  footer {
    padding-left: 24px;
    padding-right: 24px;
  }
  .hcopy {
    left: 24px;
  }
  .vintro,
  .vrow,
  .fg {
    grid-template-columns: 1fr;
  }
}
</style>
