<template>
  <div class="theme-navy" :class="{ light: !isDark }">
    <AppNav @goChat="$router.push('/sub/support?tab=chat')" />
    <AppFab />

    <main class="content">

      <!-- Hero -->
      <div class="ph">
        <div class="ph-ey">SYSTEM INTRODUCTION</div>
        <h1>시스템 <em>소개</em></h1>
        <p class="ph-sub">
          카메라 한 대로 차량을 자동 인식하고, 번호판·유입·유출 데이터를
          실시간으로 수집·분석·시각화하는 교통 흐름 관리 시스템입니다.
        </p>
      </div>

      <!-- 핵심 지표 -->
      <section class="kpi-row">
        <div class="kpi" v-for="k in kpis" :key="k.label">
          <div class="kpi-val">{{ k.val }}</div>
          <div class="kpi-label">{{ k.label }}</div>
          <div class="kpi-desc">{{ k.desc }}</div>
        </div>
      </section>

      <div class="pb">

        <!-- 주요 기능 -->
        <section class="sec">
          <div class="sec-label">KEY FEATURES</div>
          <h2 class="sh">주요 기능</h2>
          <p class="sec-desc">운영자가 실제로 사용하는 핵심 기능들입니다.</p>
          <div class="feat-grid">
            <div class="feat-card" v-for="f in features" :key="f.title">
              <div class="feat-num">{{ f.num }}</div>
              <div class="feat-title">{{ f.title }}</div>
              <div class="feat-desc">{{ f.desc }}</div>
            </div>
          </div>
        </section>

        <div class="divider"></div>

        <!-- 시스템 구성 -->
        <section class="sec">
          <div class="sec-label">SYSTEM ARCHITECTURE</div>
          <h2 class="sh">시스템 구성</h2>
          <p class="sec-desc">AI 감지부터 웹 대시보드까지 4개 레이어가 유기적으로 연동됩니다.</p>
          <div class="arch-grid">
            <div class="arch-card" v-for="(a, i) in arch" :key="a.title">
              <div class="arch-step">{{ String(i + 1).padStart(2, '0') }}</div>
              <div class="arch-tag">{{ a.tag }}</div>
              <div class="arch-title">{{ a.title }}</div>
              <div class="arch-desc">{{ a.desc }}</div>
              <div class="arch-tech">{{ a.tech }}</div>
            </div>
          </div>
        </section>


      </div>
    </main>

    <footer>
      <span class="fl">Traffic<em>AS</em></span>
      <span class="fr">© 2026 네바퀴 1조 · 스마트 모빌리티 DX Academy</span>
    </footer>
  </div>
</template>

<script setup>
import AppNav from '@/components/AppNav.vue'
import AppFab from '@/components/AppFab.vue'
import { useTheme } from '@/composables/useTheme'

const { isDark } = useTheme()

const kpis = [
  { val: '97%+',  label: '번호판 인식 정확도', desc: 'EasyOCR + 신뢰도 필터링 기반' },
  { val: '50ms',  label: '실시간 응답 속도',   desc: 'WebSocket 감지 → 화면 반영' },
  { val: '10초',  label: '중복 제거 윈도우',   desc: '동일 차량 재감지 자동 필터링' },
  { val: '24/7',  label: '무중단 모니터링',     desc: '연속 스트림 처리 및 자동 재연결' },
]

const features = [
  {
    num: '01',
    title: '실시간 차량 감지',
    desc: '카메라 영상에서 차량을 자동으로 인식하고 차종을 분류합니다. 초당 30프레임으로 처리합니다.',
  },
  {
    num: '02',
    title: '번호판 자동 인식',
    desc: 'OCR 기술로 번호판 정보를 자동 수집합니다. 인식 실패 시 null 처리로 데이터 품질을 유지합니다.',
  },
  {
    num: '03',
    title: '유입·유출 흐름 분석',
    desc: '구역별 IN/OUT 이벤트를 실시간으로 집계합니다. 중복 감지를 자동으로 제거합니다.',
  },
  {
    num: '04',
    title: '시간대별 통계 조회',
    desc: '시간대별 교통 밀도를 차트로 시각화합니다. 혼잡 패턴을 한눈에 파악할 수 있습니다.',
  },
  {
    num: '05',
    title: '차량 번호판 검색',
    desc: '특정 번호판으로 입출차 이력을 즉시 검색합니다. 시각·구역·방향 데이터를 함께 확인합니다.',
  },
  {
    num: '06',
    title: 'WebSocket 실시간 알림',
    desc: '감지 이벤트를 즉시 브로드캐스트합니다. 연결 장애 시 Polling으로 자동 전환됩니다.',
  },
]

const arch = [
  {
    tag: 'AI ENGINE',
    title: 'AI 감지 서버',
    desc: '카메라 영상을 분석해 차량 위치와 번호판을 인식합니다.',
    tech: 'Python · FastAPI · YOLOv8 · EasyOCR',
  },
  {
    tag: 'BACKEND',
    title: '데이터 처리 서버',
    desc: '감지 결과를 받아 흐름을 분석하고 REST API로 제공합니다.',
    tech: 'Java · Spring Boot · JPA · PostgreSQL',
  },
  {
    tag: 'FRONTEND',
    title: '관리 대시보드',
    desc: '실시간 현황과 통계를 웹 브라우저에서 바로 확인합니다.',
    tech: 'Vue.js 3 · Chart.js · WebSocket',
  },
  {
    tag: 'DATABASE',
    title: '데이터 저장소',
    desc: '모든 감지 이력과 흐름 데이터를 저장하고 빠르게 조회합니다.',
    tech: 'PostgreSQL · 인덱스 최적화 · 통계 캐시',
  },
]

</script>

<style scoped>
.content { padding-top: 62px; min-height: 100vh; }

/* ── Hero ── */
.ph {
  padding: 64px 60px 52px;
  border-bottom: 1px solid var(--b);
  background: var(--bg2);
}
.ph-ey {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px; letter-spacing: .22em;
  color: var(--a); opacity: .6;
  margin-bottom: 10px;
  display: flex; align-items: center; gap: 8px;
}
.ph-ey::before {
  content: ''; width: 14px; height: 1px;
  background: var(--a); opacity: .5;
}
h1 {
  font-family: 'Syne', sans-serif;
  font-size: clamp(36px, 5vw, 68px); font-weight: 800;
  letter-spacing: -3px; color: var(--t); line-height: .95; margin-bottom: 16px;
}
h1 em { color: var(--a); font-style: normal; }
.ph-sub {
  font-size: 13px; color: var(--t2); font-weight: 300;
  line-height: 1.85; max-width: 600px; margin-bottom: 20px; margin-top: 16px;
}

/* ── Body ── */
.pb { padding: 0 60px 60px; max-width: 1280px; }
.sec { padding-top: 52px; }
.sec-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px; letter-spacing: .2em;
  color: var(--a); opacity: .55; margin-bottom: 8px;
}
.sh {
  font-family: 'Syne', sans-serif;
  font-size: 20px; font-weight: 700;
  letter-spacing: -.4px; color: var(--t); margin-bottom: 6px;
}
.sec-desc {
  font-size: 13px; color: var(--t2);
  font-weight: 300; line-height: 1.8; margin-bottom: 28px;
}
.divider { height: 1px; background: var(--b); margin-top: 8px; }

/* ── KPI ── */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border-top: 1px solid var(--b);
  border-bottom: 1px solid var(--b);
  background: var(--bg2);
}
.kpi {
  padding: 36px 48px;
  border-right: 1px solid var(--b);
  transition: background .2s;
}
.kpi:last-child { border-right: none; }
.kpi:hover { background: rgba(96,165,250,.03); }
.kpi-val {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 30px; font-weight: 700;
  letter-spacing: -1px; color: var(--a);
  line-height: 1; margin-bottom: 8px;
}
.kpi-label {
  font-size: 12px; font-weight: 700;
  color: var(--t); margin-bottom: 5px;
  white-space: nowrap;
}
.kpi-desc {
  font-size: 10px; color: var(--t3);
  font-weight: 300; line-height: 1.6;
}

/* ── Features ── */
.feat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.feat-card {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 8px;
  padding: 24px 22px;
  transition: border-color .22s, transform .2s;
}
.feat-card:hover { border-color: var(--ba); transform: translateY(-2px); }
.feat-num {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px; letter-spacing: .1em;
  color: var(--a); opacity: .45; margin-bottom: 10px;
}
.feat-title {
  font-size: 14px; font-weight: 700;
  color: var(--t); margin-bottom: 8px;
}
.feat-desc {
  font-size: 12px; color: var(--t2);
  line-height: 1.75; font-weight: 300;
}

/* ── Architecture ── */
.arch-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  border: 1px solid var(--b);
  border-radius: 10px;
  overflow: hidden;
}
.arch-card {
  padding: 28px 24px;
  border-right: 1px solid var(--b);
  transition: background .2s;
  position: relative;
}
.arch-card:last-child { border-right: none; }
.arch-card:hover { background: rgba(96,165,250,.03); }
.arch-step {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 28px; font-weight: 700;
  color: var(--a); opacity: .08;
  letter-spacing: -1px; line-height: 1;
  margin-bottom: 14px; user-select: none;
}
.arch-tag {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px; letter-spacing: .14em;
  color: var(--a); opacity: .6; margin-bottom: 8px;
}
.arch-title {
  font-size: 14px; font-weight: 700;
  color: var(--t); margin-bottom: 8px;
}
.arch-desc {
  font-size: 12px; color: var(--t2);
  line-height: 1.7; font-weight: 300; margin-bottom: 14px;
}
.arch-tech {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px; color: var(--a);
  opacity: .45; line-height: 1.6;
}


/* ── Footer ── */
footer {
  border-top: 1px solid var(--b); padding: 26px 60px;
  background: var(--bg2); display: flex;
  align-items: center; justify-content: space-between;
}
.fl { font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 800; letter-spacing: -.3px; color: var(--t); }
.fl em { color: var(--a); font-style: normal; }
.fr { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--t3); }

@media (max-width: 1100px) {
  .kpi-row { grid-template-columns: repeat(2, 1fr); }
  .kpi { padding: 28px 32px; }
  .feat-grid { grid-template-columns: repeat(2, 1fr); }
  .arch-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .ph, .pb { padding-left: 20px; padding-right: 20px; }
  .kpi-row { grid-template-columns: 1fr 1fr; }
  .kpi { padding: 20px 20px; }
  .kpi-val { font-size: 26px; }
  .kpi-label { white-space: normal; }
  .feat-grid { grid-template-columns: 1fr; }
  .arch-grid { grid-template-columns: 1fr; }
}
</style>
