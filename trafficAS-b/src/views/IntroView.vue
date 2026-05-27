<template>
  <div class="theme-navy" :class="{ light: !isDark }">
    <AppNav />
    <AppFab />

    <main class="content">
      <section class="hero">
        <div class="hero-in">
          <div class="hero-left">
            <div class="hero-tag">SYSTEM INTRODUCTION</div>
            <h1>시스템 <em>소개</em></h1>
            <p class="hero-sub">
              Traffic AS는 카메라 기반 AI 영상 분석과 실시간 데이터 처리를 통해<br />
              교통 흐름을 정밀하게 이해하고, 더 안전하고 효율적인 도시를 만듭니다.
            </p>
          </div>
          <div class="hero-right">
            <!-- SVG 폴백 → PNG -->
            <img
              :src="heroImg"
              alt="시스템 구조 일러스트"
              class="hero-img"
              @error="heroImg = '/system_road_network_illustration.png'"
            />
          </div>
        </div>
      </section>

      <section class="sec">
        <div class="sw">
          <div class="sec-head">
            <h2>시스템 아키텍처</h2>
            <p>카메라부터 대시보드까지, 실시간으로 연결된 통합 구조</p>
          </div>
          <div class="arch-row">
            <template v-for="(a, i) in architecture" :key="a.num">
              <div class="arch-card">
                <div class="arch-head">
                  <span class="arch-num">{{ a.num }}</span>
                  <div class="arch-titles">
                    <div class="arch-en">{{ a.en }}</div>
                    <div class="arch-ko">{{ a.ko }}</div>
                  </div>
                </div>
                <div class="arch-body">
                  <div class="arch-icon">
                    <img
                      v-if="a.svg && !a.svgBroken"
                      :src="a.svg"
                      :alt="a.en"
                      class="arch-svg"
                      @error="a.svgBroken = true"
                    />
                    <component v-else :is="a.lucide" :size="64" :stroke-width="1.3" />
                  </div>
                  <ul class="arch-list">
                    <li v-for="p in a.points" :key="p">
                      <span class="dot">•</span>{{ p }}
                    </li>
                  </ul>
                </div>
              </div>
              <div v-if="i < architecture.length - 1" class="arch-arrow">
                <ChevronRight :size="32" :stroke-width="2" />
              </div>
            </template>
          </div>
        </div>
      </section>

      <section class="sec">
        <div class="sw">
          <div class="sec-head">
            <h2>데이터 라이프사이클</h2>
            <p>영상이 가치 있는 인사이트로 전환되기까지의 전체 흐름</p>
          </div>
          <div class="lc-row">
            <template v-for="(s, i) in lifecycle" :key="s.title">
              <div class="lc-step">
                <div class="lc-icon">
                  <component :is="s.lucide" :size="32" :stroke-width="1.8" />
                </div>
                <div class="lc-title">{{ s.title }}</div>
                <p class="lc-desc">{{ s.desc }}</p>
              </div>
              <span v-if="i < lifecycle.length - 1" class="lc-line"></span>
            </template>
          </div>
        </div>
      </section>

      <section class="sec">
        <div class="sw">
          <div class="sec-head">
            <h2>핵심 모듈</h2>
            <p>Traffic AS의 주요 기능 모듈로 교통 데이터를 가치로 극대화합니다.</p>
          </div>
          <div class="mod-row">
            <div v-for="m in modules" :key="m.num" class="mod-card">
              <div class="mod-num">{{ m.num }}</div>
              <div class="mod-title">{{ m.title }}</div>
              <div class="mod-graphic">
                <component :is="m.lucide" :size="72" :stroke-width="1.4" />
              </div>
              <p class="mod-desc">{{ m.desc }}</p>
              <div class="mod-tags">
                <span v-for="t in m.tags" :key="t" class="mod-tag">{{ t }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="sec">
        <div class="sw">
          <div class="sec-head">
            <h2>연동 및 배포</h2>
            <p>다양한 환경과 시스템에 유연하게 통합할 수 있습니다.</p>
          </div>
          <div class="deploy-row">
            <div class="deploy-box">
              <div class="deploy-h">
                연동 <span class="deploy-h-en">(Integration)</span>
              </div>
              <div class="deploy-grid">
                <div v-for="ig in integrations" :key="ig.title" class="deploy-item">
                  <div class="deploy-icon">
                    <component :is="ig.lucide" :size="26" :stroke-width="1.7" />
                  </div>
                  <div class="deploy-title">{{ ig.title }}</div>
                  <div class="deploy-desc">{{ ig.desc }}</div>
                </div>
              </div>
            </div>
            <div class="deploy-arrow"><ChevronRight :size="26" :stroke-width="2" /></div>
            <div class="deploy-box">
              <div class="deploy-h">
                배포 <span class="deploy-h-en">(Deployment)</span>
              </div>
              <div class="deploy-grid">
                <div v-for="d in deployments" :key="d.title" class="deploy-item">
                  <div class="deploy-icon">
                    <component :is="d.lucide" :size="26" :stroke-width="1.7" />
                  </div>
                  <div class="deploy-title">{{ d.title }}</div>
                  <div class="deploy-desc">{{ d.desc }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="impact-sec">
        <div class="sw">
          <div class="impact-head">
            <h2>비즈니스 임팩트</h2>
            <p>Traffic AS가 제공하는 핵심 성과 지표</p>
          </div>
          <div class="impact-row">
            <div v-for="k in kpis" :key="k.title" class="kpi-card">
              <div class="kpi-icon">
                <component :is="k.lucide" :size="28" :stroke-width="1.7" />
              </div>
              <div class="kpi-title">{{ k.title }}</div>
              <div class="kpi-value">{{ k.value }}</div>
              <div class="kpi-desc">{{ k.desc }}</div>
            </div>
          </div>
        </div>
      </section>

      <AppFooter />
    </main>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import AppNav from "@/components/AppNav.vue";
import AppFab from "@/components/AppFab.vue";
import AppFooter from "@/components/AppFooter.vue";
import { useTheme } from "@/composables/useTheme";
import {
  Cctv,
  Camera,
  BrainCircuit,
  Database,
  LayoutDashboard,
  Car,
  ScanText,
  ArrowLeftRight,
  BellRing,
  Plug,
  Radio,
  Code2,
  FileDown,
  Cloud,
  Server,
  Network,
  Crosshair,
  Zap,
  Bot,
  TrendingUp,
  ShieldCheck,
  Infinity,
  ChevronRight,
} from "lucide-vue-next";

const { isDark } = useTheme();

/* SVG 있으면 우선, 없으면 PNG */
const heroImg = ref("/illustrations/hero.svg");

const architecture = reactive([
  {
    num: "01",
    en: "Camera / Edge AI",
    ko: "카메라 / 엣지 AI",
    points: ["다중 카메라 영상 수집", "Edge AI 전처리 및 압축", "네트워크 최적화 전송"],
    svg: "/illustrations/arch-camera.svg",
    svgBroken: false,
    lucide: Cctv,
  },
  {
    num: "02",
    en: "AI Detection Engine",
    ko: "AI 감지 엔진",
    points: ["차량 감지 및 추적", "번호판 인식 (OCR)", "객체 분류 및 이벤트 검출"],
    svg: "/illustrations/arch-ai.svg",
    svgBroken: false,
    lucide: BrainCircuit,
  },
  {
    num: "03",
    en: "Data Platform",
    ko: "데이터 플랫폼",
    points: ["실시간 스트리밍 처리", "시계열 데이터 저장", "통계 / 집계 / 분석 엔진"],
    svg: "/illustrations/arch-database.svg",
    svgBroken: false,
    lucide: Database,
  },
  {
    num: "04",
    en: "Dashboard / API",
    ko: "대시보드 / API",
    points: ["실시간 대시보드", "리포트 및 통계", "외부 시스템 API 연동"],
    svg: "/illustrations/arch-dashboard.svg",
    svgBroken: false,
    lucide: LayoutDashboard,
  },
]);

const lifecycle = [
  { title: "수집", desc: "카메라로 도로 영상을 지속적으로 수집합니다.", lucide: Camera },
  { title: "감지", desc: "AI가 차량과 번호판을 정확하게 감지합니다.", lucide: Car },
  {
    title: "분석",
    desc: "유입/유출, 차량 흐름 등 교통 데이터를 분석합니다.",
    lucide: BrainCircuit,
  },
  { title: "저장", desc: "분석 결과를 안전하게 저장하고 관리합니다.", lucide: Database },
  {
    title: "활용",
    desc: "대시보드, 알림, API로 다양한 채널에 제공합니다.",
    lucide: LayoutDashboard,
  },
];

const modules = [
  {
    num: "01",
    title: "차량 감지",
    desc: "YOLO 기반 실시간 차량 감지 및 추적\n차종/차선/속도/이벤트 정보 제공",
    tags: ["실시간 감지", "다중 객체 추적", "차종 분류"],
    lucide: Car,
  },
  {
    num: "02",
    title: "번호판 OCR",
    desc: "OCR 엔진을 통한 고정밀 번호판 인식\n(국·영문, 다양한 환경 지원)",
    tags: ["고정밀 OCR", "국내 번호판 지원", "오인식 보정"],
    lucide: ScanText,
  },
  {
    num: "03",
    title: "유입·유출 분석",
    desc: "구역별 IN/OUT 이벤트 및 체류 시간,\n혼잡도, 교통량 통계 분석",
    tags: ["IN/OUT 분석", "체류 시간", "혼잡도 지표"],
    lucide: ArrowLeftRight,
  },
  {
    num: "04",
    title: "알림 / 이벤트",
    desc: "이벤트 조건 설정 및 실시간 알림 전송\n(이상 정체, 역주행, 정차 감지 등)",
    tags: ["이벤트 룰", "실시간 알림", "이력 관리"],
    lucide: BellRing,
  },
];

const integrations = [
  { title: "REST API", desc: "JSON 기반 API 제공", lucide: Plug },
  { title: "WebSocket", desc: "실시간 이벤트 스트리밍", lucide: Radio },
  { title: "SDK / Agent", desc: "언어별 SDK 제공", lucide: Code2 },
  { title: "데이터 Export", desc: "CSV / Parquet 지원", lucide: FileDown },
];

const deployments = [
  { title: "Cloud", desc: "AWS / Azure / GCP", lucide: Cloud },
  { title: "On-premise", desc: "고객사 자체 인프라", lucide: Server },
  { title: "Hybrid", desc: "클라우드 + 온프레미스", lucide: Network },
];

const kpis = [
  { title: "정확한 감지율", value: "97%+", desc: "차량 감지 정확도", lucide: Crosshair },
  { title: "실시간 처리 속도", value: "50ms", desc: "프레임당 처리 속도", lucide: Zap },
  { title: "분석 자동화율", value: "90%", desc: "수동 분석 시간 절감", lucide: Bot },
  {
    title: "운영 효율성",
    value: "40%+",
    desc: "교통 관리 비용 절감",
    lucide: TrendingUp,
  },
  {
    title: "데이터 신뢰성",
    value: "99.9%",
    desc: "데이터 안정성 보장",
    lucide: ShieldCheck,
  },
  { title: "확장성", value: "무제한", desc: "카메라 및 지역 확장", lucide: Infinity },
];
</script>

<style scoped>
.content {
  padding-top: 69px;
  background: var(--bg);
}

/* hero */
.hero {
  background: var(--bg);
  border-bottom: 1px solid var(--b);
  overflow: hidden;
}
.hero-in {
  max-width: 1440px;
  margin: 0 auto;
  padding: 32px 60px;
  display: grid;
  grid-template-columns: minmax(0, 0.55fr) minmax(0, 2.4fr);
  gap: 0;
  align-items: stretch;
  height: 360px;
  overflow: hidden;
}
.hero-tag {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: var(--a);
  margin-bottom: 14px;
}
.hero h1 {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: clamp(28px, 3vw, 40px);
  font-weight: 800;
  letter-spacing: -1.2px;
  line-height: 1.15;
  color: var(--t);
  margin: 0 0 14px;
}
.hero h1 em {
  color: var(--a);
  font-style: normal;
}
.hero-sub {
  font-size: 14px;
  font-weight: 500;
  color: var(--t);
  opacity: 0.78;
  line-height: 1.65;
  margin: 0;
  word-break: keep-all;
}
.hero-left {
  align-self: center;
}
.hero-right {
  position: relative;
  /* 상/하 padding 흡수 + 우측 풀블리드 */
  margin-top: -33px;
  margin-bottom: -33px;
  margin-left: 0;
  margin-right: min(-60px, calc(660px - 50vw));
  align-self: stretch;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.hero-img {
  width: 100%;
  height: 100%;
  max-height: 100%;
  object-fit: cover;
  object-position: center center;
  display: block;
  /* 좌측 페이드 */
  --hero-mask: linear-gradient(
    to right,
    transparent 0%,
    rgba(0, 0, 0, 0.08) 5%,
    rgba(0, 0, 0, 0.25) 12%,
    rgba(0, 0, 0, 0.55) 18%,
    rgba(0, 0, 0, 0.82) 24%,
    #000 30%,
    #000 100%
  );
  -webkit-mask-image: var(--hero-mask);
  mask-image: var(--hero-mask);
}

/* common */
.sec {
  padding: 80px 60px;
}
.sw {
  max-width: 1440px;
  margin: 0 auto;
}
.sec-head {
  margin-bottom: 36px;
}
.sec-head h2 {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.6px;
  color: var(--t);
  margin: 0 0 8px;
}
.sec-head p {
  font-size: 15px;
  color: var(--t);
  opacity: 0.75;
  margin: 0;
}

/* architecture */
.arch-row {
  display: grid;
  grid-template-columns: 1fr 36px 1fr 36px 1fr 36px 1fr;
  gap: 4px;
  align-items: stretch;
}
.arch-card {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 16px;
  padding: 26px 22px 24px;
  display: flex;
  flex-direction: column;
}
.theme-navy.light .arch-card {
  background: #fff;
  box-shadow: 0 2px 14px rgba(15, 40, 90, 0.04);
}
.arch-head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 36px;
}
.arch-num {
  flex-shrink: 0;
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 22px;
  font-weight: 800;
  color: var(--a);
  letter-spacing: -0.5px;
  line-height: 1;
  padding-top: 2px;
}
.arch-titles {
  flex: 1;
  min-width: 0;
}
.arch-en {
  font-size: 16.5px;
  font-weight: 700;
  color: var(--t);
  letter-spacing: -0.2px;
  margin-bottom: 4px;
}
.arch-ko {
  font-size: 14px;
  color: var(--t);
  opacity: 0.78;
  font-weight: 500;
}
/* icon 좌 / 리스트 우 */
.arch-body {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  margin-top: auto;
}
.arch-icon {
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--a);
  opacity: 0.9;
}
.arch-svg {
  width: 100%;
  max-width: 110px;
  height: auto;
  display: block;
}
.arch-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.arch-list li {
  font-size: 13px;
  color: var(--t);
  opacity: 0.78;
  font-weight: 500;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  line-height: 1.5;
  word-break: keep-all;
}
.arch-list .dot {
  color: var(--a);
  font-size: 14px;
  line-height: 1.35;
  flex-shrink: 0;
}
.arch-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--a);
}

/* lifecycle */
.lc-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 4px;
}
.lc-step {
  flex: 1;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.lc-icon {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  background: rgba(96, 165, 250, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--a);
  margin-bottom: 14px;
}
.theme-navy.light .lc-icon {
  background: rgba(37, 99, 235, 0.06);
}
.lc-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--t);
  margin-bottom: 10px;
}
.lc-desc {
  font-size: 13.5px;
  color: var(--t);
  opacity: 0.78;
  font-weight: 500;
  line-height: 1.6;
  max-width: 170px;
  margin: 0;
  word-break: keep-all;
}
.lc-line {
  flex-shrink: 0;
  width: 60px;
  height: 0;
  border-top: 2px dashed var(--a);
  opacity: 0.45;
  margin-top: 42px;
}

/* modules */
.mod-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}
.mod-card {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 14px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.theme-navy.light .mod-card {
  background: #fff;
  box-shadow: 0 2px 14px rgba(15, 40, 90, 0.04);
}
.mod-num {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--a);
  margin-bottom: 8px;
}
.mod-title {
  font-size: 19px;
  font-weight: 800;
  color: var(--t);
  letter-spacing: -0.4px;
  margin-bottom: 20px;
}
.mod-graphic {
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--a);
  margin-bottom: 18px;
}
.mod-desc {
  font-size: 13.5px;
  color: var(--t);
  opacity: 0.8;
  font-weight: 500;
  line-height: 1.65;
  white-space: pre-line;
  margin: 0 0 16px;
}
.mod-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  justify-content: center;
}
.mod-tag {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--a);
  background: rgba(96, 165, 250, 0.12);
  padding: 5px 11px;
  border-radius: 100px;
}
.theme-navy.light .mod-tag {
  background: rgba(37, 99, 235, 0.08);
}

/* integration & deployment */
.deploy-row {
  display: grid;
  grid-template-columns: 1fr 32px 1fr;
  gap: 12px;
  align-items: stretch;
}
.deploy-box {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 14px;
  padding: 22px;
}
.theme-navy.light .deploy-box {
  background: #fff;
  box-shadow: 0 2px 14px rgba(15, 40, 90, 0.04);
}
.deploy-h {
  font-size: 17px;
  font-weight: 700;
  color: var(--t);
  margin-bottom: 18px;
}
.deploy-h-en {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--t);
  opacity: 0.65;
  margin-left: 6px;
}
.deploy-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
.deploy-item {
  border: 1px solid var(--b);
  border-radius: 10px;
  padding: 16px 12px;
  text-align: center;
}
.deploy-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--a);
  margin-bottom: 10px;
}
.deploy-title {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--t);
  margin-bottom: 4px;
}
.deploy-desc {
  font-size: 12.5px;
  color: var(--t);
  opacity: 0.72;
  font-weight: 500;
}
.deploy-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--a);
  opacity: 0.6;
}
/* deploy 박스 3-col */
.deploy-row .deploy-box:last-of-type .deploy-grid {
  grid-template-columns: repeat(3, 1fr);
}

/* impact (dark banner) */
.impact-sec {
  position: relative;
  background: #0a1a2f;
  padding: 60px 60px;
  overflow: hidden;
}
/* grid line pattern */
.impact-sec::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(96, 165, 250, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(96, 165, 250, 0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  pointer-events: none;
  mask-image: radial-gradient(ellipse 75% 60% at 50% 40%, #000 50%, transparent 100%);
  -webkit-mask-image: radial-gradient(
    ellipse 75% 60% at 50% 40%,
    #000 50%,
    transparent 100%
  );
}
.impact-sec > * {
  position: relative;
  z-index: 1;
}
.impact-head {
  margin-bottom: 32px;
}
.impact-head h2 {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.6px;
  color: #fff;
  margin: 0 0 8px;
}
.impact-head p {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}
.impact-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px;
}
.kpi-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 22px 18px;
  text-align: center;
  transition: all 0.22s;
  cursor: default;
}
.kpi-card:hover {
  background: rgba(96, 165, 250, 0.08);
  border-color: rgba(96, 165, 250, 0.4);
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(96, 165, 250, 0.18);
}
.kpi-card:hover .kpi-icon {
  background: rgba(96, 165, 250, 0.25);
  transform: scale(1.05);
}
.kpi-card:hover .kpi-value {
  color: #93c5fd;
}
.kpi-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(96, 165, 250, 0.15);
  color: #60a5fa;
  margin-bottom: 12px;
  transition: all 0.22s;
}
.kpi-value {
  transition: color 0.22s;
}
.kpi-title {
  font-size: 14.5px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 10px;
}
.kpi-value {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 36px;
  font-weight: 800;
  letter-spacing: -1.3px;
  line-height: 1;
  color: #fff;
  margin-bottom: 12px;
}
.kpi-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  line-height: 1.55;
  word-break: keep-all;
}

/* responsive */
@media (max-width: 1100px) {
  .arch-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .arch-arrow {
    display: none;
  }
  .lc-row {
    flex-wrap: wrap;
    gap: 24px;
  }
  .lc-line {
    display: none;
  }
  .lc-step {
    flex: 0 0 calc(33% - 16px);
  }
  .mod-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .deploy-row {
    grid-template-columns: 1fr;
  }
  .deploy-arrow {
    display: none;
  }
  .impact-row {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 768px) {
  .hero-in {
    grid-template-columns: 1fr;
    padding: 50px 24px;
    gap: 30px;
  }
  .sec,
  .impact-sec {
    padding-left: 24px;
    padding-right: 24px;
  }
  .deploy-grid {
    grid-template-columns: repeat(2, 1fr) !important;
  }
  .impact-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
