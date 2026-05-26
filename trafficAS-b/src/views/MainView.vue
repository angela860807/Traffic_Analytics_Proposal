<template>
  <div class="theme-navy" :class="{ light: !isDark }">
    <AppNav />
    <AppFab />

    <section class="hero">
      <div class="hero-in">
        <div class="hero-left">
          <div class="hero-tag">AI 기반 교통 데이터 솔루션</div>
          <h1>번호판 인식 데이터로<br />도시의 <em>교통 흐름</em>을 분석합니다.</h1>
          <p class="hero-sub">
            TAS는 AI 영상 분석과 실시간 데이터 처리 기술로<br />
            교통 흐름을 정확하게 이해하고, 더 안전한 도시를 만듭니다.
          </p>
          <div class="hero-btns">
            <RouterLink to="/sub/support?tab=chat" class="btn-a">데모 신청</RouterLink>
            <RouterLink to="/sub/intro" class="btn-g">시스템 소개</RouterLink>
          </div>
        </div>
        <div class="hero-right">
          <img src="/main1.png" alt="AI 교통 감지" class="hero-img" />
        </div>
      </div>
    </section>

    <section class="sec">
      <div class="sw">
        <div class="features-grid fu" ref="fuRef1">
          <RouterLink
            v-for="f in features"
            :key="f.title"
            to="/sub/intro"
            class="feat-card"
          >
            <div class="feat-head">
              <div class="feat-icon"><i :class="f.icon"></i></div>
              <div class="feat-title">{{ f.title }}</div>
            </div>
            <p class="feat-desc">{{ f.desc }}</p>
            <span class="feat-link">자세히 보기</span>
          </RouterLink>
        </div>
      </div>
    </section>

    <section class="sec bg2">
      <div class="sw">
        <div class="solution-row fu" ref="fuRef2">
          <div class="solution-left">
            <img
              src="/dashboard.png"
              alt="관리자 대시보드 미리보기"
              class="solution-img"
            />
          </div>
          <div class="solution-right">
            <div class="ey-tag">솔루션 개요</div>
            <h2>AI로 교통을 이해하고,<br /><em>도시의 미래</em>를 바꿉니다.</h2>
            <ul class="solution-list">
              <li v-for="item in solutionPoints" :key="item">
                <i class="bi bi-check-circle-fill"></i> {{ item }}
              </li>
            </ul>
            <RouterLink to="/sub/intro" class="btn-a sm">솔루션 자세히 보기</RouterLink>
          </div>
        </div>
      </div>
    </section>

    <section class="sec">
      <div class="sw">
        <div class="ey-tag">서비스 이용 프로세스</div>
        <h2 class="sec-title">서비스 이용 <em>프로세스</em></h2>
        <div class="process-row">
          <div v-for="(p, i) in processSteps" :key="p.num" class="process-step">
            <div class="process-icon-wrap">
              <div class="process-num">{{ p.num }}</div>
              <div class="process-icon">
                <component
                  v-if="p.lucide"
                  :is="p.lucide"
                  :size="36"
                  :stroke-width="1.8"
                />
                <i v-else :class="p.icon"></i>
              </div>
              <span v-if="i < processSteps.length - 1" class="process-line"></span>
            </div>
            <div class="process-title">{{ p.title }}</div>
            <p class="process-desc">{{ p.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="sec core-sec">
      <div class="sw">
        <div class="ey-tag">핵심 기능</div>
        <div class="core-row">
          <div v-for="c in coreFeatures" :key="c.title" class="core-item">
            <div class="core-icon">
              <component v-if="c.lucide" :is="c.lucide" :size="34" :stroke-width="1.6" />
              <i v-else :class="c.icon"></i>
            </div>
            <div class="core-text">
              <div class="core-title">{{ c.title }}</div>
              <p class="core-desc">{{ c.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="cta-wrap">
      <div class="sw">
        <div class="cta-card">
          <div class="cta-text">
            <h2>TAS로 더 안전한 교통 환경을 시작하세요.</h2>
            <p>데모 신청 또는 상담 문의를 통해 맞춤 솔루션을 경험해보세요.</p>
          </div>
          <div class="cta-btns">
            <RouterLink to="/sub/support?tab=chat" class="btn-w">데모 신청</RouterLink>
            <RouterLink to="/sub/support" class="btn-wg">문의하기</RouterLink>
          </div>
        </div>
      </div>
    </section>

    <AppFooter />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { RouterLink } from "vue-router";
import AppNav from "@/components/AppNav.vue";
import AppFab from "@/components/AppFab.vue";
import AppFooter from "@/components/AppFooter.vue";
import { useTheme } from "@/composables/useTheme";
import { Cctv, ScanText, BellRing, BarChart3, Network } from "lucide-vue-next";

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

const features = [
  {
    title: "정확한 인식",
    icon: "bi bi-bullseye",
    desc: "번호판을 높은 정확도로 인식하여 신뢰할 수 있는 데이터를 제공합니다.",
  },
  {
    title: "실시간 처리",
    icon: "bi bi-lightning-charge-fill",
    desc: "초저지연 영상 분석과 고효율 처리로 실시간으로 분석합니다.",
  },
  {
    title: "안정적 운영",
    icon: "bi bi-shield-check",
    desc: "무중단 모니터링으로 안정적인 시스템 운영을 보장합니다.",
  },
  {
    title: "데이터 기반 의사결정",
    icon: "bi bi-bar-chart-fill",
    desc: "교통 데이터와 시각화된 인사이트로 정확한 운영과 정책 결정을 지원합니다.",
  },
];

const solutionPoints = [
  "다중 카메라 통합 모니터링 및 이벤트 감지",
  "차량·번호판·차량 흐름 실시간 인식",
  "교통 흐름 분석 및 혼잡 예측",
  "직관적인 대시보드와 리포트 제공",
];

const processSteps = [
  {
    num: "01",
    lucide: Cctv,
    title: "데이터 수집",
    desc: "카메라를 통한 영상 데이터 수집 및 전송",
  },
  {
    num: "02",
    icon: "bi bi-cpu-fill",
    title: "AI 분석",
    desc: "AI 엔진의 객체 인식 및 교통 상황 분석",
  },
  {
    num: "03",
    icon: "bi bi-graph-up",
    title: "실시간 모니터링",
    desc: "대시보드에서 실시간 상태 확인 및 알림 수신",
  },
  {
    num: "04",
    icon: "bi bi-file-earmark-text",
    title: "의사결정 활용",
    desc: "분석 데이터 기반으로 정책 및 운영에 활용",
  },
];

const coreFeatures = [
  { title: "실시간 영상 분석", lucide: Cctv, desc: "다중 카메라 실시간 분석" },
  { title: "번호판 인식 (OCR)", lucide: ScanText, desc: "정확한 번호판 인식 및 검색" },
  { title: "이벤트 알림", lucide: BellRing, desc: "이상 상황 실시간 알림" },
  { title: "통계 및 리포트", lucide: BarChart3, desc: "다양한 통계 및 리포트 제공" },
  { title: "확장 가능한 아키텍처", lucide: Network, desc: "유연한 연동 및 확장 지원" },
];
</script>

<style scoped>
/* hero */
.hero {
  position: relative;
  background: var(--bg);
  overflow: hidden;
}
.hero-in {
  max-width: 1440px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 7fr); /* 3:7 */
  align-items: end;
}
.hero-left {
  position: relative;
  z-index: 2;
  align-self: center;
}
.hero-tag {
  display: inline-block;
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: var(--a);
  margin-bottom: 18px;
}
.hero h1 {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: clamp(34px, 3.4vw, 37px);
  font-weight: 800;
  letter-spacing: -1.4px;
  line-height: 1.3;
  color: var(--t);
  margin: 0 0 20px;
  word-break: keep-all;
}
/* em 컬러 살짝 밝게 */
.hero h1 em {
  color: #4f9cf9;
  font-style: normal;
}
.theme-navy:not(.light) .hero h1 em {
  color: #60a5fa;
}
.hero-sub {
  font-size: 17.5px;
  font-weight: 500;
  color: var(--t);
  opacity: 0.78;
  line-height: 1.8;
  margin: 0 0 32px;
  word-break: keep-all;
}
.hero-btns {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.hero-right {
  position: relative;
  align-self: stretch;
  margin-right: calc(60px - (50vw - 50%)); /* 화면 우측 끝까지 */
  overflow: hidden;
  min-height: 600px;
}
.hero-img {
  width: 100%;
  height: 100%;
  min-height: 600px;
  max-height: 720px;
  display: block;
  object-fit: cover;
  /* 톤다운 */
  filter: saturate(0.78) brightness(0.85);
  /* 좌측 페이드 */
  --hero-mask: linear-gradient(
    to right,
    transparent 0%,
    rgba(0, 0, 0, 0.02) 4%,
    rgba(0, 0, 0, 0.08) 8%,
    rgba(0, 0, 0, 0.18) 13%,
    rgba(0, 0, 0, 0.32) 18%,
    rgba(0, 0, 0, 0.5) 23%,
    rgba(0, 0, 0, 0.68) 28%,
    rgba(0, 0, 0, 0.84) 33%,
    rgba(0, 0, 0, 0.95) 38%,
    #000 42%,
    #000 100%
  );
  -webkit-mask-image: var(--hero-mask);
  mask-image: var(--hero-mask);
}

/* common */
.sec {
  padding: 80px 60px;
}
.sec.bg2 {
  background: var(--bg2);
}
/* 카드가 히어로 끝선에 살짝 걸치게 */
.hero + .sec {
  margin-top: -50px;
  padding-top: 0;
  padding-bottom: 60px;
  position: relative;
  z-index: 5;
}
.sw {
  max-width: 1440px;
  margin: 0 auto;
}
.ey-tag {
  display: inline-block;
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 16px;
  font-weight: 600;
  color: var(--a);
  margin-bottom: 12px;
}
.sec-title {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: clamp(26px, 2.6vw, 34px);
  font-weight: 800;
  letter-spacing: -0.8px;
  color: var(--t);
  margin: 0 0 44px;
}
.sec-title em {
  color: var(--a);
  font-style: normal;
}

/* features */
.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 55px;
}
.feat-card {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 14px;
  padding: 28px 26px;
  transition: all 0.22s;
  display: block;
  text-decoration: none;
  color: inherit;
}
.theme-navy.light .feat-card {
  background: #fff;
  box-shadow: 0 2px 14px rgba(15, 40, 90, 0.05);
}
.feat-card:hover {
  border-color: var(--ba);
  transform: translateY(-4px);
  box-shadow: 0 14px 36px rgba(96, 165, 250, 0.12);
}
.theme-navy.light .feat-card:hover {
  box-shadow: 0 14px 36px rgba(37, 99, 235, 0.1);
}
/* icon + title 한 줄 */
.feat-head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}
.feat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: rgba(96, 165, 250, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--a);
  font-size: 20px;
  flex-shrink: 0;
}
.theme-navy.light .feat-icon {
  background: rgba(37, 99, 235, 0.08);
}
.feat-title {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 19px;
  font-weight: 700;
  letter-spacing: -0.4px;
  color: var(--t);
}
.feat-desc {
  font-size: 15px;
  font-weight: 500;
  color: var(--t);
  opacity: 0.72;
  line-height: 1.7;
  margin: 0 0 18px;
  word-break: keep-all;
}
.feat-link {
  font-size: 14.5px;
  font-weight: 600;
  color: var(--a);
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: gap 0.18s;
}
.feat-card:hover .feat-link {
  gap: 8px;
}

/* solution */
.solution-row {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 80px;
  align-items: center;
}
.solution-right {
  padding-left: 40px;
}
.solution-img {
  width: 100%;
  height: auto;
  border-radius: 14px;
  display: block;
  box-shadow: 0 24px 60px rgba(15, 40, 90, 0.18), 0 4px 14px rgba(15, 40, 90, 0.06);
  transition: transform 0.4s, box-shadow 0.4s;
}
.solution-img:hover {
  transform: translateY(-4px);
  box-shadow: 0 32px 80px rgba(37, 99, 235, 0.2), 0 8px 20px rgba(15, 40, 90, 0.08);
}
.solution-right h2 {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: clamp(28px, 2.8vw, 38px);
  font-weight: 800;
  letter-spacing: -0.9px;
  line-height: 1.35;
  color: var(--t);
  margin: 0 0 26px;
  word-break: keep-all;
}
.solution-right h2 em {
  color: var(--a);
  font-style: normal;
}
.solution-list {
  list-style: none;
  padding: 0;
  margin: 0 0 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.solution-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 17px;
  color: var(--t);
  font-weight: 500;
}
.solution-list i {
  color: var(--a);
  font-size: 18px;
  flex-shrink: 0;
}

/* process */
.process-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
.process-step {
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
/* num을 icon 좌상단에 띄움 */
.process-icon-wrap {
  position: relative;
  display: inline-block;
  margin-bottom: 22px;
}
.process-num {
  position: absolute;
  top: -12px;
  left: -12px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--a);
  color: #fff;
  font-family: "Pretendard Variable", sans-serif;
  font-size: 13.5px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.28);
  z-index: 3;
}
.process-icon {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  background: rgba(96, 165, 250, 0.12);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--a);
  font-size: 32px;
  margin: 0;
  position: relative;
  z-index: 2;
}
/* step 연결선 */
.process-line {
  position: absolute;
  top: 50%;
  left: calc(100% + 14px);
  width: 16vw;
  max-width: 240px;
  min-width: 120px;
  height: 0;
  border-top: 2px dashed var(--a);
  opacity: 0.55;
  transform: translateY(-50%);
  z-index: 1;
}
.theme-navy.light .process-icon {
  background: rgba(37, 99, 235, 0.06);
}
.process-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--t);
  margin-bottom: 10px;
  text-align: center;
  width: 100%;
}
.process-desc {
  font-size: 15px;
  color: var(--t);
  opacity: 0.72;
  line-height: 1.7;
  font-weight: 500;
  margin: 0;
  word-break: keep-all;
  text-align: center;
  width: 100%;
  max-width: 200px;
}

/* core features */
.core-sec {
  padding-top: 40px;
  padding-bottom: 40px;
}
.core-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  border-top: 1px solid var(--b);
  border-bottom: 1px solid var(--b);
  padding: 30px 0;
}
.core-item {
  padding: 16px 18px;
  display: flex;
  align-items: center;
  gap: 16px;
  text-align: left;
  border-right: 1px solid var(--b);
}
.core-item:last-child {
  border-right: none;
}
.core-icon {
  width: 44px;
  height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--a);
  flex-shrink: 0;
}
.core-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.core-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--t);
  margin-bottom: 6px;
  letter-spacing: -0.3px;
}
.core-desc {
  font-size: 14.5px;
  color: var(--t);
  opacity: 0.7;
  line-height: 1.6;
  font-weight: 500;
  margin: 0;
}

/* cta */
.cta-wrap {
  padding: 30px 60px 80px;
}
.cta-card {
  max-width: 1440px;
  margin: 0 auto;
  background: linear-gradient(135deg, var(--a), #2563eb);
  border-radius: 16px;
  padding: 44px 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
  flex-wrap: wrap;
  box-shadow: 0 20px 50px rgba(37, 99, 235, 0.25);
}
.cta-text h2 {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: clamp(22px, 2.2vw, 28px);
  font-weight: 800;
  letter-spacing: -0.6px;
  color: #fff;
  margin: 0 0 8px;
}
.cta-text p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.92);
  margin: 0;
}
.cta-btns {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* buttons */
.btn-a,
.btn-g,
.btn-w,
.btn-wg {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 14px 28px;
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 15.5px;
  font-weight: 700;
  letter-spacing: -0.2px;
  border-radius: 8px;
  transition: all 0.18s;
  text-decoration: none;
}
.btn-a {
  background: var(--a);
  color: #fff;
  border: 1px solid var(--a);
}
.btn-a:hover {
  opacity: 0.92;
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(96, 165, 250, 0.3);
}
.btn-a.sm {
  padding: 12px 24px;
  font-size: 15px;
}
.btn-g {
  background: transparent;
  color: var(--t);
  border: 1px solid var(--b);
}
.btn-g:hover {
  border-color: var(--a);
  color: var(--a);
}
.btn-w {
  background: #fff;
  color: var(--a);
  border: 1px solid #fff;
}
.btn-w:hover {
  background: rgba(255, 255, 255, 0.92);
}
.btn-wg {
  background: transparent;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.5);
}
.btn-wg:hover {
  border-color: #fff;
  background: rgba(255, 255, 255, 0.12);
}

.fu {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s, transform 0.6s;
}
.fu.v {
  opacity: 1;
  transform: none;
}

/* responsive */
@media (max-width: 1200px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .core-row {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 900px) {
  .hero-in {
    grid-template-columns: 1fr;
    gap: 40px;
    padding: 60px 24px;
  }
  .hero-right {
    margin-right: 0;
  }
  .hero-img {
    max-height: 320px;
    mask-image: none;
    -webkit-mask-image: none;
  }
  .hero + .sec {
    margin-top: 0;
    padding-top: 50px;
  }

  .solution-row {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  .process-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 768px) {
  .sec,
  .cta-wrap {
    padding-left: 24px;
    padding-right: 24px;
  }
  .sec {
    padding-top: 60px;
    padding-bottom: 60px;
  }
  .features-grid,
  .core-row,
  .process-row {
    grid-template-columns: repeat(2, 1fr);
  }
  /* 2-col 우측 항목 보더 제거 */
  .core-item:nth-child(2n) {
    border-right: none;
  }
  .cta-card {
    flex-direction: column;
    align-items: flex-start;
    padding: 32px 24px;
  }
}
</style>
