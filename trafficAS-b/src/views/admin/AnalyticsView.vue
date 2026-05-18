<template>
  <div class="an-shell">
    <header class="top">
      <h1>
        Traffic AS <span class="t-sub">교통분석팀</span>
      </h1>
      <div class="t-right">
        <DeptSwitcher />
        <div class="t-avatar">MA</div>
        <div class="t-user">교통분석팀 매니저 <i class="bi bi-chevron-down"></i></div>
      </div>
    </header>

    <div class="body">
      <aside class="filter">
        <RouterLink to="/" class="brand">
          <span class="dot"></span> Traffic <em>AS</em>
        </RouterLink>
        <nav class="snav">
          <button v-for="m in analysisMenu" :key="m.id" class="snav-i" :class="{ on: anaTab === m.id }" @click="anaTab = m.id">
            <i :class="m.icon"></i>{{ m.label }}
          </button>
        </nav>
        <div class="f-block">
          <h3>비교 설정</h3>
          <div class="f-sec">
            <div class="f-lab">비교 기준</div>
            <select class="f-sel" v-model="compareBase">
              <option value="prev">전일</option>
              <option value="prevWeek">전주 동일 요일</option>
              <option value="avg7">최근 7일 평균</option>
            </select>
          </div>
          <div class="f-sec">
            <div class="f-lab">기간 선택</div>
            <div class="seg-row">
              <button v-for="p in periods" :key="p.id" class="seg" :class="{ on: period === p.id }" @click="period = p.id">{{ p.label }}</button>
            </div>
            <div class="date-r">{{ dateRange }} <i class="bi bi-calendar3"></i></div>
          </div>
          <div class="f-sec">
            <div class="f-lab">시간대</div>
            <select class="f-sel" v-model="timeSlot">
              <option value="all">전체 시간</option>
              <option value="am">오전 (06~12시)</option>
              <option value="pm">오후 (12~18시)</option>
              <option value="rush">출퇴근 (07~09, 17~19)</option>
              <option value="night">야간 (22~05시)</option>
            </select>
          </div>
        </div>

        <div class="f-block">
          <h3>권한 및 작업</h3>
          <div class="auth-grid">
            <button class="auth-btn bl" @click="opMsg = '통계 조회 실행'"><i class="bi bi-bar-chart"></i>통계 조회</button>
            <button class="auth-btn bl" @click="opMsg = '기간 비교 실행'"><i class="bi bi-calendar3"></i>기간 비교</button>
            <button class="auth-btn gr" @click="opMsg = '리포트 생성 시작'"><i class="bi bi-file-earmark-text"></i>리포트 생성</button>
            <button class="auth-btn pl" @click="opMsg = 'CSV 내보내기 완료'"><i class="bi bi-download"></i>CSV 내보내기</button>
          </div>
          <div v-if="opMsg" class="op-msg">{{ opMsg }}</div>
        </div>

        <SideWeather />

        <div class="data-up">
          <div class="du-l">데이터 업데이트</div>
          <div class="du-r">{{ dataUpdated }} <i class="bi bi-arrow-clockwise"></i></div>
        </div>
      </aside>

      <div class="content">
        <section class="metrics">
          <div class="mt-card">
            <div class="mt-lab">평균속도</div>
            <div class="mt-val">{{ metrics.avgSpeed }}<span class="mt-u">km/h</span></div>
            <div class="mt-spark"><svg viewBox="0 0 80 24" class="sp"><polyline points="0,16 10,14 20,18 30,12 40,14 50,10 60,12 70,8 80,10" fill="none" stroke="#60a5fa" stroke-width="1.5"/></svg></div>
            <div class="mt-d">전일 대비 <span class="dn">▼ {{ metrics.speedDelta }}%</span></div>
          </div>
          <div class="mt-card">
            <div class="mt-lab">혼잡 구간</div>
            <div class="mt-val">{{ metrics.congSections }}<span class="mt-u">개</span></div>
            <div class="mt-spark"><svg viewBox="0 0 80 24" class="sp"><polyline points="0,8 10,12 20,10 30,14 40,12 50,16 60,14 70,18 80,16" fill="none" stroke="#ef4444" stroke-width="1.5"/></svg></div>
            <div class="mt-d">전일 대비 <span class="up-r">▲ {{ metrics.congDelta }}</span></div>
          </div>
          <div class="mt-card">
            <div class="mt-lab">피크시간 악화</div>
            <div class="mt-val or">{{ metrics.recurringJam }}<span class="mt-u">구간</span></div>
            <div class="mt-spark"><svg viewBox="0 0 80 24" class="sp"><polyline points="0,12 10,16 20,14 30,18 40,14 50,16 60,12 70,14 80,16" fill="none" stroke="#fbbf24" stroke-width="1.5"/></svg></div>
            <div class="mt-d">전일 대비 <span class="up-r">▲ 1</span></div>
          </div>
          <div class="mt-card">
            <div class="mt-lab">보고서 예약</div>
            <div class="mt-val">{{ metrics.changeDelta }}<span class="mt-u">건</span></div>
            <div class="mt-d">예정 보고서</div>
          </div>
          <div class="mt-card mt-time">
            <div class="mt-lab">기준 시간</div>
            <div class="mt-time-v">2025-05-15 (목) 08:00 <i class="bi bi-calendar3"></i></div>
            <div class="mt-d">데이터 기준 5분 전</div>
          </div>
        </section>

        <section class="row-cmp">
          <div class="cmp-area">
            <div class="cmp-h">
              <h3>구간 성능 비교 <i class="bi bi-info-circle"></i></h3>
            </div>
            <div class="cmp-grid">
              <div class="cm-chart">
                <h4>구간별 속도 비교 <span class="cm-u">(km/h)</span></h4>
                <div class="cm-legend">
                  <span><span class="lg-dot bl"></span> 금일 (05/15)</span>
                  <span><span class="lg-dot gy"></span> 전일 (05/14)</span>
                  <span><span class="lg-dot gr"></span> 평균 (최근 7일)</span>
                </div>
                <div class="chart-frame">
                  <div class="y-axis"><span>100</span><span>80</span><span>60</span><span>40</span><span>20</span><span>0</span></div>
                  <svg viewBox="0 0 360 180" class="line-svg" preserveAspectRatio="none">
                    <line v-for="y in [30,60,90,120,150]" :key="y" :y1="y" :y2="y" x1="0" x2="360" stroke="#1f3055" stroke-dasharray="2 4"/>
                    <rect x="180" y="50" width="120" height="120" fill="#ef4444" opacity="0.1"/>
                    <text x="222" y="100" fill="#f87171" font-size="10" font-weight="700">혼잡 구간</text>
                    <polyline :points="cmpLines.today" fill="none" stroke="#60a5fa" stroke-width="2"/>
                    <polyline :points="cmpLines.prev" fill="none" stroke="#9ca3af" stroke-width="2" stroke-dasharray="4 4"/>
                    <polyline :points="cmpLines.avg" fill="none" stroke="#10b981" stroke-width="2"/>
                    <circle v-for="(p,i) in cmpDots" :key="i" :cx="p.x" :cy="p.y" r="2.5" fill="#60a5fa"/>
                  </svg>
                </div>
                <div class="cm-x">
                  <span>구리IC</span><span>독립IC</span><span>강변IC</span><span>마사IC</span>
                  <span>일산IC</span><span>원효대교</span><span>한남IC</span>
                </div>
              </div>

              <div class="cm-chart">
                <h4>시간대별 속도 추이 <span class="cm-u">(km/h)</span></h4>
                <div class="cm-legend">
                  <span><span class="lg-dot bl"></span> 금일 (05/15)</span>
                  <span><span class="lg-dot gy"></span> 전일 (05/14)</span>
                  <span><span class="lg-dot gr"></span> 평균 (최근 7일)</span>
                </div>
                <div class="chart-frame">
                  <div class="y-axis"><span>100</span><span>80</span><span>60</span><span>40</span><span>20</span><span>0</span></div>
                  <svg viewBox="0 0 360 180" class="line-svg" preserveAspectRatio="none">
                    <line v-for="y in [30,60,90,120,150]" :key="y" :y1="y" :y2="y" x1="0" x2="360" stroke="#1f3055" stroke-dasharray="2 4"/>
                    <rect x="120" y="100" width="180" height="80" fill="#ef4444" opacity="0.1"/>
                    <text x="170" y="148" fill="#f87171" font-size="10" font-weight="700">피크 시간대 속도 저하</text>
                    <polyline points="0,70 30,65 60,68 90,72 120,140 150,130 180,120 210,125 240,110 270,90 300,70 330,55 360,50" fill="none" stroke="#60a5fa" stroke-width="2"/>
                    <polyline points="0,85 30,80 60,82 90,100 120,135 150,125 180,115 210,120 240,100 270,90 300,75 330,68 360,60" fill="none" stroke="#9ca3af" stroke-width="2" stroke-dasharray="4 4"/>
                    <polyline points="0,90 30,88 60,90 90,108 120,128 150,120 180,112 210,116 240,105 270,92 300,80 330,72 360,65" fill="none" stroke="#10b981" stroke-width="2"/>
                  </svg>
                </div>
                <div class="cm-x">
                  <span>00시</span><span>04시</span><span>08시</span><span>12시</span>
                  <span>16시</span><span>20시</span><span>24시</span>
                </div>
              </div>
            </div>
          </div>

          <aside class="insight">
            <h3><i class="bi bi-clipboard-data" style="color:#2563eb"></i> 분석 인사이트</h3>
            <div class="ins-card" v-for="(ins, i) in aiInsights" :key="i">
              <i :class="ins.icon" :style="{ color: ins.color }"></i>
              <div>
                <div class="ic-t">{{ ins.title }}</div>
                <div class="ic-d">{{ ins.detail }}</div>
              </div>
            </div>
            <button class="ai-detail-btn">상세 리포트 보기 <i class="bi bi-arrow-right"></i></button>
          </aside>
        </section>

        <section class="row-mid">
          <div class="card jam-map-card">
            <h3>도로 구간 혼잡 현황 <i class="bi bi-info-circle"></i></h3>
            <div ref="jamMapEl" class="jam-leaflet"></div>
            <div class="jm-legend">
              <span class="jl-label">평균 속도 (km/h)</span>
              <div class="jl-bar"></div>
              <div class="jl-ticks"><span>20</span><span>40</span><span>60</span><span>80</span></div>
            </div>
          </div>

          <div class="card kpi-tbl-card">
            <h3>구간 주요 지표</h3>
            <table class="tbl-kpi">
              <thead><tr><th>구간</th><th>평균 속도 (km/h)</th><th>전일 대비</th><th>혼잡 시간(최대)</th><th>혼잡도</th></tr></thead>
              <tbody>
                <tr v-for="r in segKpis" :key="r.name">
                  <td>{{ r.name }}</td><td class="mono">{{ r.speed }}</td>
                  <td><span :class="r.dTone">{{ r.delta }}</span></td>
                  <td class="mono">{{ r.peak }}</td>
                  <td><span class="cg-tag" :class="r.cgTone">{{ r.cg }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="row-bot">
          <div class="card resv-card">
            <h3>보고서 예약 현황</h3>
            <table class="tbl-resv">
              <thead><tr><th>보고서명</th><th>주기</th><th>다음 실행</th><th>수신자</th><th>상태</th></tr></thead>
              <tbody>
                <tr v-for="r in reservations" :key="r.id">
                  <td>{{ r.name }}</td><td>{{ r.cycle }}</td><td class="mono">{{ r.next }}</td>
                  <td class="mono">{{ r.to }}</td>
                  <td><span class="resv-st" :class="r.tone">{{ r.st }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="card saved-card">
            <h3>저장된 분석 목록</h3>
            <table class="tbl-saved">
              <thead><tr><th>분석명</th><th>분석 유형</th><th>기준 기간</th><th>생성일</th><th>생성자</th></tr></thead>
              <tbody>
                <tr v-for="s in savedAnalyses" :key="s.id">
                  <td>{{ s.name }}</td><td>{{ s.type }}</td>
                  <td class="mono">{{ s.range }}</td><td class="mono">{{ s.created }}</td>
                  <td>{{ s.by }}</td>
                </tr>
              </tbody>
            </table>
            <button class="more-btn">더 보기 ↓</button>
          </div>
        </section>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { RouterLink } from "vue-router";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { loadOSMRoads, renderOSMRoads } from "@/composables/useOSMRoads";
import DeptSwitcher from "@/components/dashboard/DeptSwitcher.vue";
import SideWeather from "@/components/dashboard/SideWeather.vue";

const roads = [
  { id: "gangbyeon", label: "강변복로 (구리 → 한남)",     subs: ["구리IC", "토평IC", "강일IC", "미사IC", "암사IC", "천호대교", "한남IC"] },
  { id: "olympic",   label: "올림픽대로 (가양 → 여의도)", subs: ["가양IC", "성산IC", "양화대교", "여의도"] },
  { id: "naebu",     label: "내부순환로 (월계 → 성수)",   subs: ["월계IC", "정릉", "홍지문", "성수JC"] },
];

const sectQuery = ref("");
const activeRoad = ref("gangbyeon");
const period = ref("7d");
const timeSlot = ref("all");
const cmpTab = ref("speed");

const periods = [
  { id: "today", label: "오늘" },
  { id: "yest",  label: "어제" },
  { id: "7d",    label: "최근 7일" },
  { id: "30d",   label: "최근 30일" },
];

const filteredRoads = computed(() => {
  const q = sectQuery.value.trim().toLowerCase();
  if (!q) return roads;
  return roads.filter(r => r.label.toLowerCase().includes(q));
});

const activeRoadObj = computed(() => roads.find(r => r.id === activeRoad.value) || roads[0]);
const activeRoadLabel = computed(() => activeRoadObj.value.label);
const activeSubs = computed(() => activeRoadObj.value.subs);

const periodLabel = computed(() => periods.find(p => p.id === period.value)?.label || "");

const dateRange = computed(() => {
  const map = {
    today: "2026-05-17 ~ 2026-05-17",
    yest:  "2026-05-16 ~ 2026-05-16",
    "7d":  "2026-05-11 ~ 2026-05-17",
    "30d": "2026-04-18 ~ 2026-05-17",
  };
  return map[period.value];
});

const baseMetrics = {
  gangbyeon: { avgSpeed: 42, speedDelta: 6,  congSections: 12, congDelta: 2, changeDelta: 8, recurringJam: 4 },
  olympic:   { avgSpeed: 56, speedDelta: 3,  congSections:  6, congDelta: 1, changeDelta: 4, recurringJam: 2 },
  naebu:     { avgSpeed: 38, speedDelta: 9,  congSections: 14, congDelta: 3, changeDelta: 11,recurringJam: 5 },
};
const periodMult = { today: 1, yest: 1.05, "7d": 0.95, "30d": 0.9 };
const slotMult = { all: 1, am: 1.1, pm: 0.9, rush: 0.7, night: 1.25 };

const metrics = computed(() => {
  const b = baseMetrics[activeRoad.value];
  const k = periodMult[period.value] * slotMult[timeSlot.value];
  return {
    avgSpeed:     Math.round(b.avgSpeed * k),
    speedDelta:   b.speedDelta,
    congSections: Math.max(1, Math.round(b.congSections / k)),
    congDelta:    b.congDelta,
    changeDelta:  b.changeDelta,
    recurringJam: b.recurringJam,
  };
});

const cmpVariants = {
  "gangbyeon-speed": { today: "20,60 80,45 140,60 200,90 260,130 320,110 340,95", prev: "20,75 80,70 140,75 200,80 260,85 320,90 340,90", avg: "20,80 80,75 140,80 200,85 260,90 320,95 340,95" },
  "gangbyeon-time":  { today: "20,120 80,135 140,120 200,90 260,50 320,75 340,90", prev: "20,105 80,110 140,105 200,100 260,95 320,90 340,90", avg: "20,100 80,105 140,100 200,95 260,90 320,85 340,85" },
  "olympic-speed":   { today: "20,40 80,38 140,42 200,55 260,70 320,60 340,50", prev: "20,55 80,50 140,55 200,60 260,65 320,60 340,55", avg: "20,60 80,55 140,60 200,65 260,70 320,65 340,60" },
  "olympic-time":    { today: "20,130 80,135 140,128 200,100 260,75 320,90 340,110", prev: "20,115 80,120 140,115 200,110 260,105 320,110 340,115", avg: "20,110 80,115 140,110 200,105 260,100 320,105 340,110" },
  "naebu-speed":     { today: "20,80 80,70 140,90 200,115 260,140 320,130 340,120", prev: "20,90 80,85 140,95 200,100 260,105 320,100 340,95", avg: "20,95 80,90 140,100 200,105 260,110 320,105 340,100" },
  "naebu-time":      { today: "20,100 80,110 140,90 200,60 260,30 320,55 340,75", prev: "20,90 80,95 140,90 200,85 260,80 320,85 340,90", avg: "20,85 80,90 140,85 200,80 260,75 320,80 340,85" },
};

const cmpLines = computed(() => cmpVariants[`${activeRoad.value}-${cmpTab.value}`]);

const cmpDots = computed(() =>
  cmpLines.value.today.split(" ").map(p => {
    const [x, y] = p.split(",");
    return { x: Number(x), y: Number(y) };
  })
);

const aiInsights = [
  { icon: "bi bi-exclamation-circle-fill", color: "#dc2626", title: "피크시간 악화 구간 증가", detail: "출근 시간대 혼잡 악화 구간이 전일 대비 1개 증가했습니다." },
  { icon: "bi bi-exclamation-triangle-fill", color: "#b45309", title: "특정 구간 속도 저하", detail: "일산IC → 원효대교 구간 속도가 전일 대비 12% 감소했습니다." },
  { icon: "bi bi-check-circle-fill", color: "#059669", title: "전반적 흐름 개선", detail: "전체 평균 속도는 전일 대비 6% 개선되었습니다." },
  { icon: "bi bi-info-circle-fill", color: "#2563eb", title: "사고 영향 감소", detail: "사고 다발 구간의 영향이 전일 대비 18% 감소했습니다." },
];

const analysisMenu = [
  { id: "dashboard", icon: "bi bi-grid-1x2",            label: "대시보드" },
  { id: "section",   icon: "bi bi-bezier2",             label: "구간 분석" },
  { id: "cross",     icon: "bi bi-diagram-3",           label: "교차로 분석" },
  { id: "time",      icon: "bi bi-clock",               label: "시간대 분석" },
  { id: "incident",  icon: "bi bi-exclamation-triangle",label: "사고·이벤트 분석" },
  { id: "report",    icon: "bi bi-file-earmark-text",   label: "보고서 관리" },
  { id: "settings",  icon: "bi bi-gear",                label: "설정" },
];
const anaTab = ref("dashboard");
const compareBase = ref("prev");
const opMsg = ref("");
const dataUpdated = ref("2025-05-15  08:00");

const jamPoints = [
  { name: "구리IC",   x:  60, y: 124, ly: -12, speed: "48km/h", color: "#34d399" },
  { name: "독립IC",   x: 150, y: 124, ly: -12, speed: "52km/h", color: "#34d399" },
  { name: "강변IC",   x: 240, y: 130, ly: -12, speed: "61km/h", color: "#34d399" },
  { name: "마사IC",   x: 340, y: 138, ly: 18,  speed: "42km/h", color: "#34d399" },
  { name: "일산IC",   x: 430, y: 148, ly: -12, speed: "23km/h", color: "#ef4444" },
  { name: "원효대교", x: 510, y: 162, ly: 18,  speed: "27km/h", color: "#fb923c" },
  { name: "한남IC",   x: 565, y: 178, ly: 18,  speed: "55km/h", color: "#34d399" },
];

const segKpis = [
  { name: "구리IC",   speed: 48, delta: "▼ 3",  dTone: "dn",   peak: "08시", cg: "보통", cgTone: "yl" },
  { name: "독립IC",   speed: 52, delta: "▲ 2",  dTone: "up",   peak: "08시", cg: "보통", cgTone: "yl" },
  { name: "강변IC",   speed: 61, delta: "▲ 4",  dTone: "up",   peak: "09시", cg: "보통", cgTone: "yl" },
  { name: "마사IC",   speed: 42, delta: "▼ 6",  dTone: "dn",   peak: "08시", cg: "주의", cgTone: "or" },
  { name: "일산IC",   speed: 23, delta: "▼ 9",  dTone: "dn",   peak: "08시", cg: "혼잡", cgTone: "rd" },
  { name: "원효대교", speed: 27, delta: "▼ 11", dTone: "dn",   peak: "18시", cg: "혼잡", cgTone: "rd" },
  { name: "한남IC",   speed: 55, delta: "▼ 2",  dTone: "dn",   peak: "18시", cg: "보통", cgTone: "yl" },
];

const reservations = [
  { id: 1, name: "일일 교통흐름 리포트",   cycle: "매일 08:00",   next: "2025-05-16 08:00",                to: "admin@trafficas.com", st: "예약", tone: "ok" },
  { id: 2, name: "주간 구간 성능 리포트", cycle: "매주 월 09:00", next: "2025-05-19 09:00",                to: "team@trafficas.com",  st: "예약", tone: "ok" },
  { id: 3, name: "월간 교통 분석 리포트", cycle: "매월 1일 10:00", next: "2025-06-01 10:00",                to: "mgmt@trafficas.com",  st: "예약", tone: "ok" },
  { id: 4, name: "사고 영향 분석 리포트", cycle: "이벤트 발생 시", next: "—",                                 to: "ops@trafficas.com",   st: "대기", tone: "wait" },
];

const savedAnalyses = [
  { id: 1, name: "일산IC 혼잡 원인 분석",       type: "구간 분석",  range: "2025-05-09 ~ 2025-05-15", created: "2025-05-15 07:45", by: "김분석" },
  { id: 2, name: "출근시간 속도 저하 구간 분석", type: "시간대 분석", range: "2025-05-09 ~ 2025-05-15", created: "2025-05-14 18:30", by: "김분석" },
  { id: 3, name: "주요 교차로 지체 분석",       type: "교차로 분석", range: "2025-05-01 ~ 2025-05-14", created: "2025-05-14 09:15", by: "이분석" },
  { id: 4, name: "5월 2주차 종합 리포트",       type: "종합 분석",  range: "2025-05-09 ~ 2025-05-15", created: "2025-05-13 17:10", by: "김분석" },
];

function resetFilters() {
  sectQuery.value = "";
  activeRoad.value = "gangbyeon";
  period.value = "7d";
  timeSlot.value = "all";
  cmpTab.value = "speed";
}

// === Leaflet 혼잡도 지도 ===
const jamMapEl = ref(null);
let jamMap = null;

const ICs = [
  { name: "구리IC",   lat: 37.5996, lng: 127.1387, speed: 48, color: "#34d399" },
  { name: "독립IC",   lat: 37.5751, lng: 127.1080, speed: 52, color: "#34d399" },
  { name: "강변IC",   lat: 37.5566, lng: 127.0890, speed: 61, color: "#34d399" },
  { name: "마사IC",   lat: 37.5470, lng: 127.0700, speed: 42, color: "#34d399" },
  { name: "일산IC",   lat: 37.5378, lng: 127.0460, speed: 23, color: "#ef4444" },
  { name: "원효대교", lat: 37.5318, lng: 127.0210, speed: 27, color: "#fb923c" },
  { name: "한남IC",   lat: 37.5258, lng: 126.9967, speed: 55, color: "#34d399" },
];

function speedToColor(s) {
  if (s < 30) return "#ef4444";
  if (s < 40) return "#fb923c";
  if (s < 60) return "#fbbf24";
  return "#34d399";
}

onMounted(async () => {
  if (!jamMapEl.value) return;
  await new Promise(r => setTimeout(r, 50));
  try {
    jamMap = L.map(jamMapEl.value, {
      center: [37.5566, 127.0700],
      zoom: 11,
      minZoom: 9,
      maxZoom: 18,
      zoomControl: true,
      attributionControl: false,
    });
    const vworld = L.tileLayer(
      "https://xdworld.vworld.kr/2d/midnight/202002/{z}/{x}/{y}.png",
      { maxZoom: 19, maxNativeZoom: 18 }
    );
    const cartoDark = L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
      { maxZoom: 19, maxNativeZoom: 19, subdomains: "abcd" }
    );
    vworld.on("tileerror", () => {
      jamMap.removeLayer(vworld);
      cartoDark.addTo(jamMap);
    });
    vworld.addTo(jamMap);

    // OSM Overpass에서 강변북로 일대 motorway/trunk만 → 가벼움
    const ways = await loadOSMRoads(
      "osm-roads-analytics-gangbyeon-v2",
      "37.51,126.97,37.60,127.14",
      ["motorway", "trunk"]
    );
    if (ways && ways.length > 0) {
      renderOSMRoads(jamMap, ways);
    }

    // IC 마커
    ICs.forEach(ic => {
      const html = `<div style="
        width:10px;height:10px;border-radius:50%;
        background:${ic.color};border:2px solid #0f1d34;
        box-shadow:0 0 0 2px ${ic.color}66;
      "></div>`;
      const marker = L.marker([ic.lat, ic.lng], {
        icon: L.divIcon({ className: "ic-pin", html, iconSize: [10, 10] }),
      }).addTo(jamMap);
      marker.bindTooltip(`<strong>${ic.name}</strong> · ${ic.speed} km/h`, {
        direction: "top", offset: [0, -4], className: "ic-tip", permanent: false,
      });
    });

    setTimeout(() => jamMap?.invalidateSize(), 200);
  } catch (e) {
    console.warn("[Analytics jam map]", e.message);
  }
});

onBeforeUnmount(() => {
  if (jamMap) { jamMap.remove(); jamMap = null; }
});
</script>

<style scoped>
.an-shell { min-height: 100vh; }
.top { padding: 16px 24px; border-bottom: 1px solid #1a2a45; }
.top h1 { display: flex; align-items: center; gap: 8px; }
.brand-link { display: inline-flex; align-items: center; gap: 8px; color: inherit; text-decoration: none; cursor: pointer; }
.brand-link:hover { opacity: 0.85; }
.top .dot { width: 7px; height: 7px; border-radius: 50%; background: #60a5fa; box-shadow: 0 0 8px #60a5fa; }
.t-sub { font-weight: 500; opacity: .8; }
.t-right { display: flex; align-items: center; gap: 10px; }
.btn-pri { background: #3b82f6; color: #fff; border: 0; border-radius: 6px; padding: 8px 14px; font-size: 13px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }

.body { display: flex; min-height: calc(100vh - 60px); }
.filter { width: 220px; background: #06101e; border-right: 1px solid #1a2a45; padding: 20px 16px; flex-shrink: 0; display: flex; flex-direction: column; gap: 20px; }
.filter h3 { font-size: 14px; font-weight: 700; margin: 0 0 6px; }
.f-lab { font-size: 12px; font-weight: 600; opacity: .85; margin-bottom: 8px; }
.f-search { position: relative; margin-bottom: 8px; }
.f-search i { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); opacity: .55; font-size: 12px; }
.f-search input { width: 100%; background: #0a1424; border: 1px solid #1f3055; color: #e4eeff; padding: 6px 26px 6px 10px; border-radius: 5px; font-size: 12px; }
.ck-list { display: flex; flex-direction: column; gap: 6px; }
.ck { display: flex; align-items: center; gap: 6px; font-size: 12.5px; cursor: pointer; }
.ck input { accent-color: #60a5fa; }
.sub-list { display: flex; flex-direction: column; gap: 4px; padding: 4px 0 4px 24px; border-left: 1px dashed #1f3055; margin-left: 8px; }
.empty-q { font-size: 11px; opacity: .5; padding: 6px 4px; }

.filter { width: 240px; }
.f-block { margin-bottom: 20px; padding-bottom: 18px; border-bottom: 1px solid #1a2a45; }
.f-block:last-of-type { border-bottom: 0; }
.anav { display: flex; flex-direction: column; gap: 2px; }
.anav-i { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 6px; color: rgba(228,238,255,.55); font-size: 12.5px; border: 0; background: none; cursor: pointer; font-family: inherit; text-align: left; }
.anav-i:hover { background: rgba(96,165,250,.06); color: #e4eeff; }
.anav-i.on { background: rgba(96,165,250,.15); color: #60a5fa; font-weight: 600; }
.anav-i i { width: 16px; }
.auth-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.auth-btn { display: flex; align-items: center; justify-content: center; gap: 5px; padding: 9px 6px; border: 0; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer; font-family: inherit; color: #fff; }
.auth-btn.bl { background: #3b82f6; }
.auth-btn:nth-child(2).bl { background: rgba(59,130,246,.18); color: #60a5fa; border: 1px solid rgba(59,130,246,.35); }
.auth-btn.gr { background: #10b981; }
.auth-btn.pl { background: #8b5cf6; }
.auth-btn i { font-size: 12px; }
.op-msg { margin-top: 8px; font-size: 11px; color: #34d399; text-align: center; }
.data-up { margin-top: auto; padding-top: 12px; font-size: 10.5px; opacity: .6; }
.du-l { margin-bottom: 2px; }
.du-r { font-family: "JetBrains Mono", monospace; display: flex; justify-content: space-between; align-items: center; }
.t-avatar { width: 30px; height: 30px; border-radius: 50%; background: #3b82f6; color: #fff; font-size: 11px; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; }

.row-mid { display: grid; grid-template-columns: 1.1fr 1fr; gap: 14px; }
.jam-map-card, .kpi-tbl-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.jam-map-card h3, .kpi-tbl-card h3 { font-size: 14px; font-weight: 700; margin: 0 0 12px; }
.jam-map-card { position: relative; }
.jam-leaflet { width: 100%; height: 280px; border-radius: 8px; overflow: hidden; background: #06101e; }
.jam-leaflet :deep(.leaflet-container) { background: #06101e; }
.jam-leaflet :deep(.leaflet-control-zoom a) { background: rgba(8,16,32,.85); color: #e4eeff; border-color: #1f3055; }
.jam-leaflet :deep(.ic-tip), .jam-leaflet :deep(.osm-road-tip) { background: rgba(8,16,32,.92); border: 1px solid #1f3055; color: #e4eeff; font-size: 11px; padding: 4px 8px; line-height: 1.55; }
.jm-legend { display: flex; align-items: center; gap: 8px; margin-top: 10px; font-size: 10.5px; opacity: .8; }
.jl-label { white-space: nowrap; }
.jl-bar { flex: 1; height: 8px; max-width: 200px; border-radius: 2px;
  background: linear-gradient(90deg, #ef4444 0%, #fb923c 33%, #fbbf24 66%, #34d399 100%); }
.jl-ticks { display: flex; justify-content: space-between; max-width: 200px; flex: 1; font-family: "JetBrains Mono", monospace; }
.tbl-kpi { width: 100%; border-collapse: collapse; font-size: 12px; }
.tbl-kpi th, .tbl-kpi td { padding: 8px 6px; text-align: center; border-bottom: 1px solid #1a2a45; }
.tbl-kpi th { font-weight: 600; opacity: .55; font-size: 11px; }
.tbl-kpi .mono { font-family: "JetBrains Mono", monospace; }
.tbl-kpi .up { color: #34d399; }
.tbl-kpi .dn { color: #f87171; }
.cg-tag { padding: 2px 8px; border-radius: 100px; font-size: 10.5px; font-weight: 700; }
.cg-tag.yl { background: rgba(245,158,11,.18); color: #fbbf24; }
.cg-tag.or { background: rgba(251,146,60,.2); color: #fb923c; }
.cg-tag.rd { background: rgba(239,68,68,.18); color: #f87171; }

.row-bot { display: grid; grid-template-columns: 1fr 1.5fr; gap: 14px; }
.resv-card, .saved-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.resv-card h3, .saved-card h3 { font-size: 14px; font-weight: 700; margin: 0 0 12px; }
.tbl-resv, .tbl-saved { width: 100%; border-collapse: collapse; font-size: 11.5px; }
.tbl-resv th, .tbl-resv td, .tbl-saved th, .tbl-saved td { padding: 8px 6px; text-align: left; border-bottom: 1px solid #1a2a45; }
.tbl-resv th, .tbl-saved th { font-weight: 600; opacity: .55; font-size: 10.5px; }
.tbl-resv .mono, .tbl-saved .mono { font-family: "JetBrains Mono", monospace; opacity: .85; }
.resv-st { padding: 2px 8px; border-radius: 100px; font-size: 10px; font-weight: 700; }
.resv-st.ok { background: rgba(96,165,250,.18); color: #60a5fa; }
.resv-st.wait { background: rgba(245,158,11,.18); color: #fbbf24; }
.more-btn { width: 100%; margin-top: 10px; background: rgba(96,165,250,.06); border: 1px solid rgba(96,165,250,.2); color: #60a5fa; padding: 7px; border-radius: 5px; font-size: 11.5px; cursor: pointer; }
.sb { font-size: 11.5px; opacity: .7; padding-left: 10px; position: relative; }
.sb::before { content: ""; position: absolute; left: 0; top: 50%; width: 6px; height: 6px; border-radius: 50%; border: 1px solid #60a5fa; transform: translateY(-50%); }
.seg-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px; margin-bottom: 8px; }
.seg { background: #0a1424; border: 1px solid #1f3055; color: rgba(228,238,255,.7); padding: 5px; font-size: 11px; border-radius: 4px; cursor: pointer; }
.seg.on { background: #3b82f6; border-color: #3b82f6; color: #fff; }
.date-r { font-size: 11px; opacity: .7; display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: #0a1424; border: 1px solid #1f3055; border-radius: 4px; }
.f-sel { width: 100%; background: #0a1424; border: 1px solid #1f3055; color: #e4eeff; padding: 6px 10px; border-radius: 5px; font-size: 12.5px; }
.reset { margin-top: auto; background: rgba(96,165,250,.08); border: 1px solid rgba(96,165,250,.25); color: #60a5fa; padding: 8px; border-radius: 5px; cursor: pointer; font-size: 12px; }

.content { flex: 1; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; min-width: 0; }
.metrics { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
.mt-time .mt-time-v { font-size: 14px; font-weight: 700; padding: 4px 0; }
.mt-time .mt-time-v i { opacity: .55; margin-left: 4px; }
.mt-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 14px; display: grid; grid-template-columns: 1fr auto; grid-template-rows: auto auto auto; gap: 4px 12px; }
.mt-lab { grid-column: 1; font-size: 12px; opacity: .75; }
.mt-val { grid-column: 1; font-size: 26px; font-weight: 800; }
.mt-val.gr { color: #34d399; }
.mt-val.or { color: #fbbf24; }
.mt-u { font-size: 13px; font-weight: 500; opacity: .65; margin-left: 2px; }
.mt-spark { grid-column: 2; grid-row: 1 / 3; align-self: center; width: 80px; }
.sp { width: 100%; height: 24px; }
.mt-d { grid-column: 1 / -1; font-size: 11px; opacity: .65; padding-top: 4px; border-top: 1px solid #1a2a45; margin-top: 4px; }
.mt-d .up-r { color: #f87171; }
.mt-d .dn { color: #f87171; }

.row-cmp { display: grid; grid-template-columns: 1fr 260px; gap: 14px; }
.cmp-area { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.cmp-h { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.cmp-h h3 { font-size: 14px; font-weight: 700; margin: 0; }
.seg-sub { font-size: 12px; opacity: .55; font-weight: 400; margin-left: 4px; }
.cmp-tabs { display: flex; gap: 4px; background: #06101e; border: 1px solid #1f3055; border-radius: 6px; padding: 2px; }
.ct { background: none; border: 0; color: rgba(228,238,255,.6); font-size: 11.5px; padding: 5px 12px; border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; }
.ct.on { background: rgba(96,165,250,.15); color: #60a5fa; }
.cmp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.cm-chart h4 { font-size: 12px; font-weight: 600; margin: 0 0 8px; }
.cm-legend { display: flex; flex-wrap: wrap; gap: 10px; font-size: 10.5px; opacity: .8; margin-bottom: 8px; }
.lg-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; }
.lg-dot.bl { background: #60a5fa; }
.lg-dot.gy { background: #9ca3af; }
.lg-dot.gr { background: #10b981; }
.lg-dot.bl-d { background: #3b82f6; opacity: .5; }
.lg-dot.gr-d { background: #10b981; opacity: .5; }
.line-svg { width: 100%; height: 180px; }
.chart-frame { display: flex; gap: 6px; align-items: stretch; }
.y-axis { display: flex; flex-direction: column; justify-content: space-between; font-size: 9.5px; opacity: .5; padding: 2px 0; width: 22px; text-align: right; }
.chart-frame .line-svg { flex: 1; }
.cm-u { font-size: 10.5px; opacity: .55; font-weight: 400; }
.cm-chart h4 { display: flex; align-items: baseline; gap: 4px; }
.cm-x { display: flex; justify-content: space-between; font-size: 9.5px; opacity: .55; padding: 4px 0 0; }

.insight { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 14px; }
.insight h3 { font-size: 13px; font-weight: 700; margin: 0 0 8px; display: flex; align-items: center; gap: 6px; }
.ins-card { display: flex; gap: 10px; padding: 10px 0; border-bottom: 1px solid #1a2a45; }
.ins-card:last-of-type { border-bottom: 0; }
.ins-card > i { font-size: 16px; padding-top: 1px; flex-shrink: 0; }
.ic-t { font-size: 12.5px; font-weight: 700; margin-bottom: 3px; }
.ic-d { font-size: 11px; opacity: .7; line-height: 1.5; }
.ai-detail-btn { width: 100%; margin-top: 12px; background: rgba(96,165,250,.1); border: 1px solid rgba(96,165,250,.3); color: #60a5fa; padding: 9px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
.insight h3.mt { margin-top: 14px; }
.insight h4 { font-size: 12px; opacity: .75; margin: 0 0 8px; font-weight: 500; }
.ins { display: flex; gap: 8px; padding: 8px 0; font-size: 11.5px; line-height: 1.55; border-bottom: 1px solid #1a2a45; }
.ins:last-of-type { border-bottom: 0; }
.ins-ic { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.rec { font-size: 11.5px; padding: 6px 0; display: flex; align-items: flex-start; gap: 6px; line-height: 1.5; }
.rec i { color: #60a5fa; padding-top: 2px; }
.rep-d { display: flex; align-items: center; gap: 8px; padding: 8px; background: rgba(96,165,250,.06); border-radius: 6px; }
.rep-d > i { font-size: 22px; color: #60a5fa; }
.rep-d > div { flex: 1; min-width: 0; }
.rep-t { font-size: 12px; font-weight: 700; }
.rep-s { font-size: 10.5px; opacity: .65; }
.rep-dl { background: rgba(96,165,250,.15); border: 0; color: #60a5fa; width: 26px; height: 26px; border-radius: 4px; cursor: pointer; }

.row-bot { display: grid; grid-template-columns: 1fr 1.2fr; gap: 14px; }
.flow-card, .deep-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.flow-card h3, .deep-card h3 { font-size: 14px; font-weight: 700; margin: 0 0 12px; }
.flow-grid { display: grid; grid-template-columns: 1fr 100px 1fr; gap: 10px; align-items: center; }
.fc { padding: 6px; }
.fc-h { font-size: 12px; margin-bottom: 6px; }
.fc-lg { font-size: 10.5px; opacity: .75; margin-bottom: 6px; display: flex; gap: 8px; }
.flow-svg { width: 100%; height: 120px; }
.fc-x { display: flex; justify-content: space-between; font-size: 9.5px; opacity: .55; padding-top: 4px; }
.fc-mid { display: flex; flex-direction: column; gap: 6px; font-size: 11px; padding: 0 8px; }
.m-row { display: flex; align-items: center; gap: 6px; opacity: .8; }
.m-row .d { width: 6px; height: 6px; border-radius: 50%; border: 1px solid #60a5fa; }

.b-red { background: rgba(239,68,68,.18); color: #f87171; font-size: 10.5px; font-weight: 700; padding: 1px 8px; border-radius: 4px; margin-left: 4px; }
.deep-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 14px; }
.dl-h { font-size: 12px; font-weight: 700; margin-bottom: 10px; }
.dl-i { display: flex; gap: 10px; padding: 8px 0; align-items: flex-start; }
.dl-i i { font-size: 16px; padding-top: 2px; }
.dl-i > div { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.dl-i strong { font-size: 12.5px; }
.dl-i span { font-size: 11px; opacity: .7; line-height: 1.45; }
.deep-right { display: flex; flex-direction: column; gap: 10px; }
.dr-c h4 { font-size: 11px; font-weight: 600; margin: 0 0 4px; opacity: .85; }
.dr-u { font-size: 10px; opacity: .55; font-weight: 400; margin-left: 2px; }
.sp-c { width: 100%; height: 80px; }
.dr-x { display: flex; justify-content: space-between; font-size: 9.5px; opacity: .55; }
</style>
