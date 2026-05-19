<template>
  <div class="an-shell">
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

        <div class="side-mk">
          <div class="smk-h">핵심 지표</div>
          <div class="smk-i bl">
            <span class="smk-l">평균속도</span>
            <span class="smk-v">{{ metrics.avgSpeed }}<small>km/h</small></span>
            <span class="smk-d dn">▼ {{ metrics.speedDelta }}%</span>
          </div>
          <div class="smk-i rd">
            <span class="smk-l">혼잡 구간</span>
            <span class="smk-v">{{ metrics.congSections }}<small>개</small></span>
            <span class="smk-d up-r">▲ {{ metrics.congDelta }}</span>
          </div>
          <div class="smk-i or">
            <span class="smk-l">피크시간 악화</span>
            <span class="smk-v">{{ metrics.recurringJam }}<small>구간</small></span>
            <span class="smk-d up-r">▲ 1</span>
          </div>
          <div class="smk-i gr">
            <span class="smk-l">보고서 예약</span>
            <span class="smk-v">{{ metrics.changeDelta }}<small>건</small></span>
          </div>
        </div>

        <SideWeather />

        <div class="data-up">
          <div class="du-l">데이터 업데이트</div>
          <div class="du-r">{{ dataUpdated }} <i class="bi bi-arrow-clockwise"></i></div>
        </div>
      </aside>

      <div class="content">
        <header class="top">
          <h1><a class="t-main" @click="goHome">교통분석팀</a></h1>
          <div class="t-right">
            <span class="hdr-time"><i class="bi bi-clock"></i> 마지막 업데이트 <strong>{{ dataUpdated }}</strong></span>
            <button class="km-toggle" :class="{ on: autoRefresh }" @click="autoRefresh = !autoRefresh" :aria-pressed="autoRefresh">
              <span class="km-dot"></span>
              <span class="km-lab">자동 새로고침</span>
              <span class="km-state">{{ autoRefresh ? 'ON' : 'OFF' }}</span>
            </button>
            <DeptSwitcher />
            <div class="t-user"><i class="bi bi-person-circle"></i> 교통분석팀 매니저 <i class="bi bi-chevron-down"></i></div>
          </div>
        </header>

        <section class="insight-strip" v-if="anaTab === 'dashboard'">
          <div class="is-h"><i class="bi bi-clipboard-data"></i> 분석 인사이트</div>
          <div class="is-list">
            <div class="is-card" v-for="(ins, i) in aiInsights" :key="i">
              <i :class="ins.icon" :style="{ color: ins.color }"></i>
              <div>
                <div class="is-t">{{ ins.title }}</div>
                <div class="is-d">{{ ins.detail }}</div>
              </div>
            </div>
          </div>
          <button class="is-more">상세 <i class="bi bi-arrow-right"></i></button>
        </section>

        <section class="row-cmp" v-if="anaTab === 'dashboard'">
          <div class="cmp-area">
            <div class="cmp-h">
              <h3>구간 성능 비교 <i class="bi bi-info-circle"></i></h3>
            </div>
            <div class="cmp-grid">
              <div class="cm-chart">
                <div class="cm-head">
                  <h4>구간별 속도 비교 <span class="cm-u">(km/h)</span></h4>
                  <div class="cm-legend-ext">
                    <span><span class="lg-dot bl"></span>금일</span>
                    <span><span class="lg-dot gy"></span>전일</span>
                    <span><span class="lg-dot gr"></span>최근 7일 평균</span>
                  </div>
                </div>
                <div ref="cmpChartEl" class="cm-echart"></div>
              </div>

              <div class="cm-chart">
                <div class="cm-head">
                  <h4>시간대별 속도 추이 <span class="cm-u">(km/h)</span></h4>
                  <div class="cm-legend-ext">
                    <span><span class="lg-dot bl"></span>금일</span>
                    <span><span class="lg-dot gy"></span>전일</span>
                    <span><span class="lg-dot gr"></span>최근 7일 평균</span>
                  </div>
                </div>
                <div ref="hourChartEl" class="cm-echart"></div>
              </div>
            </div>
          </div>

        </section>

        <!-- 구간 분석 탭 -->
        <section v-if="anaTab === 'section'" class="tab-panel">
          <div class="tp-h">
            <h2><i class="bi bi-bezier2"></i> 구간 분석</h2>
            <span class="tp-sub">{{ segKpis.length }}개 구간</span>
          </div>
          <table class="tp-tbl">
            <thead>
              <tr><th>구간</th><th>평균 속도</th><th>전일 대비</th><th>피크 시간</th><th>혼잡도</th></tr>
            </thead>
            <tbody>
              <tr v-for="r in segKpis" :key="r.name">
                <td><strong>{{ r.name }}</strong></td>
                <td class="mono"><strong>{{ r.speed }}</strong> km/h</td>
                <td><span :class="r.dTone" class="mono">{{ r.delta }}</span></td>
                <td class="mono">{{ r.peak }}</td>
                <td><span class="cg-tag" :class="r.cgTone">{{ r.cg }}</span></td>
              </tr>
            </tbody>
          </table>
        </section>

        <!-- 교차로 분석 탭 -->
        <section v-if="anaTab === 'cross'" class="tab-panel">
          <div class="tp-h"><h2><i class="bi bi-diagram-3"></i> 교차로 분석</h2><span class="tp-sub">3개 주요 교차로</span></div>
          <div class="tp-grid">
            <div class="tp-card" v-for="x in [
              { name: '강남대로 × 테헤란로', wait: 87, level: '혼잡', tone: 'rd', vol: 4820 },
              { name: '한남대교 북단',      wait: 62, level: '주의', tone: 'or', vol: 3940 },
              { name: '여의도 환승센터',   wait: 38, level: '원활', tone: 'gr', vol: 2110 },
            ]" :key="x.name">
              <div class="tpc-name">{{ x.name }}</div>
              <div class="tpc-row"><span>평균 대기</span><strong class="mono">{{ x.wait }}초</strong></div>
              <div class="tpc-row"><span>혼잡도</span><span class="cg-tag" :class="x.tone">{{ x.level }}</span></div>
              <div class="tpc-row"><span>통행량 (시간)</span><strong class="mono">{{ x.vol.toLocaleString() }}대</strong></div>
            </div>
          </div>
        </section>

        <!-- 시간대 분석 탭 -->
        <section v-if="anaTab === 'time'" class="tab-panel">
          <div class="tp-h"><h2><i class="bi bi-clock"></i> 시간대 분석</h2><span class="tp-sub">24시간 평균 속도</span></div>
          <table class="tp-tbl">
            <thead><tr><th>시간대</th><th>평균 속도</th><th>혼잡 구간</th><th>특징</th></tr></thead>
            <tbody>
              <tr><td><strong>출근 (07~09)</strong></td><td class="mono"><strong>34</strong> km/h</td><td><span class="cg-tag rd">혼잡</span> 12</td><td>강변·올림픽 정체</td></tr>
              <tr><td><strong>오전 (09~12)</strong></td><td class="mono"><strong>56</strong> km/h</td><td><span class="cg-tag or">주의</span> 4</td><td>점진적 해소</td></tr>
              <tr><td><strong>오후 (12~17)</strong></td><td class="mono"><strong>58</strong> km/h</td><td><span class="cg-tag yl">보통</span> 2</td><td>안정</td></tr>
              <tr><td><strong>퇴근 (17~20)</strong></td><td class="mono"><strong>28</strong> km/h</td><td><span class="cg-tag rd">혼잡</span> 15</td><td>전 구간 정체</td></tr>
              <tr><td><strong>야간 (22~05)</strong></td><td class="mono"><strong>72</strong> km/h</td><td><span class="cg-tag gr">원활</span> 0</td><td>최저 통행량</td></tr>
            </tbody>
          </table>
        </section>

        <!-- 사고·이벤트 분석 탭 -->
        <section v-if="anaTab === 'incident'" class="tab-panel">
          <div class="tp-h"><h2><i class="bi bi-exclamation-triangle"></i> 사고·이벤트 분석</h2><span class="tp-sub">최근 24시간</span></div>
          <table class="tp-tbl">
            <thead><tr><th>발생 시각</th><th>구간</th><th>유형</th><th>지속</th><th>영향</th><th>상태</th></tr></thead>
            <tbody>
              <tr><td class="mono">14:24</td><td>강변북로 한남TG</td><td>차량 정체 (사고)</td><td class="mono">8분</td><td><span class="cg-tag rd">혼잡 +12</span></td><td><span class="cg-tag rd">진행</span></td></tr>
              <tr><td class="mono">11:08</td><td>올림픽대로 가양</td><td>차량 고장</td><td class="mono">22분</td><td><span class="cg-tag or">평균 -18%</span></td><td><span class="cg-tag gr">복구</span></td></tr>
              <tr><td class="mono">08:42</td><td>내부순환 정릉</td><td>출근 정체</td><td class="mono">1시간 14분</td><td><span class="cg-tag rd">평균 -32%</span></td><td><span class="cg-tag gr">복구</span></td></tr>
            </tbody>
          </table>
        </section>

        <!-- 보고서 관리 탭 -->
        <section v-if="anaTab === 'report'" class="tab-panel">
          <div class="tp-h"><h2><i class="bi bi-file-earmark-text"></i> 보고서 관리</h2></div>
          <div class="tp-2col">
            <div>
              <h3 class="tp-sec">보고서 예약 현황</h3>
              <table class="tp-tbl">
                <thead><tr><th>보고서명</th><th>주기</th><th>다음 실행</th><th>상태</th></tr></thead>
                <tbody>
                  <tr v-for="r in reservations" :key="r.id">
                    <td><strong>{{ r.name }}</strong></td><td>{{ r.cycle }}</td><td class="mono">{{ r.next }}</td>
                    <td><span class="cg-tag" :class="r.tone === 'ok' ? 'gr' : 'or'">{{ r.st }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div>
              <h3 class="tp-sec">저장된 분석 목록</h3>
              <table class="tp-tbl">
                <thead><tr><th>분석명</th><th>유형</th><th>기간</th><th>생성</th></tr></thead>
                <tbody>
                  <tr v-for="s in savedAnalyses" :key="s.id">
                    <td><strong>{{ s.name }}</strong></td><td>{{ s.type }}</td>
                    <td class="mono">{{ s.range }}</td><td class="mono">{{ s.created }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <!-- 설정 탭 -->
        <section v-if="anaTab === 'settings'" class="tab-panel">
          <div class="tp-h"><h2><i class="bi bi-gear"></i> 설정</h2></div>
          <div class="tp-set">
            <div class="tps-row"><label>기본 비교 기준</label>
              <select v-model="compareBase">
                <option value="prev">전일</option><option value="prevWeek">전주 동일 요일</option><option value="avg7">최근 7일 평균</option>
              </select>
            </div>
            <div class="tps-row"><label>기본 시간대 필터</label>
              <select v-model="timeSlot">
                <option value="all">전체</option><option value="am">오전</option><option value="pm">오후</option><option value="rush">출퇴근</option><option value="night">야간</option>
              </select>
            </div>
            <div class="tps-row"><label>자동 새로고침</label><input type="checkbox" v-model="autoRefresh" /></div>
            <div class="tps-row"><label>리포트 자동 발행</label><input type="checkbox" /></div>
          </div>
        </section>

        <section class="row-mid" v-if="anaTab === 'dashboard'">
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
            <div class="kpi-head">
              <h3>구간 주요 지표</h3>
              <a class="ch-link" @click="anaTab = 'section'">전체 보기 ›</a>
            </div>
            <table class="tbl-kpi">
              <thead><tr><th>구간</th><th>평균(km/h)</th><th>전일 대비</th><th>피크</th><th>혼잡도</th></tr></thead>
              <tbody>
                <tr v-for="r in segKpis" :key="r.name">
                  <td>{{ r.name }}</td><td class="mono">{{ r.speed }}</td>
                  <td><span :class="r.dTone" class="mono">{{ r.delta }}</span></td>
                  <td class="mono">{{ r.peak }}</td>
                  <td><span class="cg-tag" :class="r.cgTone">{{ r.cg }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>


      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from "vue";
import { RouterLink } from "vue-router";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import echarts from "@/composables/echartsSetup";
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
const autoRefresh = ref(true);
function goHome() {
  anaTab.value = "dashboard";
  window.scrollTo({ top: 0, behavior: "smooth" });
}
const compareBase = ref("prev");
const opMsg = ref("");
const dataUpdated = ref("2025-05-15  08:00");

const jamPoints = [
  { name: "구리IC",   x:  60, y: 124, ly: -12, speed: "48km/h", color: "#fbbf24" },
  { name: "독립IC",   x: 150, y: 124, ly: -12, speed: "52km/h", color: "#fbbf24" },
  { name: "강변IC",   x: 240, y: 130, ly: -12, speed: "61km/h", color: "#34d399" },
  { name: "마사IC",   x: 340, y: 138, ly: 18,  speed: "42km/h", color: "#fbbf24" },
  { name: "일산IC",   x: 430, y: 148, ly: -12, speed: "23km/h", color: "#ef4444" },
  { name: "원효대교", x: 510, y: 162, ly: 18,  speed: "27km/h", color: "#ef4444" },
  { name: "한남IC",   x: 565, y: 178, ly: 18,  speed: "55km/h", color: "#fbbf24" },
];

const segKpis = [
  { name: "강변IC",   speed: 61, delta: "▲ 4",  dTone: "up",   peak: "09시", cg: "원활", cgTone: "gr" },
  { name: "일산IC",   speed: 23, delta: "▼ 9",  dTone: "dn",   peak: "08시", cg: "혼잡", cgTone: "rd" },
  { name: "원효대교", speed: 27, delta: "▼ 11", dTone: "dn",   peak: "18시", cg: "혼잡", cgTone: "rd" },
];

const reservations = [
  { id: 1, name: "일일 교통흐름 리포트",   cycle: "매일 08:00",   next: "2025-05-16 08:00", to: "admin@trafficas.com", st: "예약", tone: "ok" },
  { id: 2, name: "주간 구간 성능 리포트", cycle: "매주 월 09:00", next: "2025-05-19 09:00", to: "team@trafficas.com",  st: "예약", tone: "ok" },
];

const savedAnalyses = [
  { id: 1, name: "일산IC 혼잡 원인 분석",       type: "구간 분석",  range: "2025-05-09 ~ 2025-05-15", created: "2025-05-15 07:45", by: "김분석" },
  { id: 2, name: "출근시간 속도 저하 구간 분석", type: "시간대 분석", range: "2025-05-09 ~ 2025-05-15", created: "2025-05-14 18:30", by: "김분석" },
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
  { name: "구리IC",   lat: 37.5996, lng: 127.1387, speed: 48, color: "#fbbf24" },
  { name: "독립IC",   lat: 37.5751, lng: 127.1080, speed: 52, color: "#fbbf24" },
  { name: "강변IC",   lat: 37.5566, lng: 127.0890, speed: 61, color: "#34d399" },
  { name: "마사IC",   lat: 37.5470, lng: 127.0700, speed: 42, color: "#fbbf24" },
  { name: "일산IC",   lat: 37.5378, lng: 127.0460, speed: 23, color: "#ef4444" },
  { name: "원효대교", lat: 37.5318, lng: 127.0210, speed: 27, color: "#ef4444" },
  { name: "한남IC",   lat: 37.5258, lng: 126.9967, speed: 55, color: "#fbbf24" },
];

function speedToColor(s) {
  if (s < 30) return "#ef4444";
  if (s < 40) return "#fb923c";
  if (s < 60) return "#fbbf24";
  return "#34d399";
}

// === ECharts: 구간별 속도 비교 + 시간대별 속도 추이 ===
const cmpChartEl = ref(null);
const hourChartEl = ref(null);
let cmpChart = null;
let hourChart = null;

const cmpData = {
  cats: ["구리IC", "독립IC", "강변IC", "마사IC", "일산IC", "원효대교", "한남IC"],
  today: [48, 52, 61, 42, 23, 27, 55],
  prev:  [52, 54, 60, 45, 32, 35, 58],
  avg:   [54, 56, 62, 48, 38, 42, 60],
};
const hourData = {
  cats: ["00시", "04시", "08시", "12시", "16시", "20시", "24시"],
  today: [80, 78, 32, 58, 70, 88, 92],
  prev:  [78, 76, 40, 62, 68, 82, 88],
  avg:   [75, 74, 45, 60, 65, 80, 85],
};

function lineSeries(name, data, color, dashed = false) {
  return {
    name,
    type: "line",
    data,
    smooth: 0.35,
    symbol: "circle",
    symbolSize: 7,
    lineStyle: {
      width: dashed ? 2 : 3,
      color,
      type: dashed ? "dashed" : "solid",
      shadowBlur: dashed ? 0 : 10,
      shadowColor: color + "55",
    },
    itemStyle: { color, borderColor: "#fff", borderWidth: 1.5 },
    emphasis: { focus: "series", scale: 1.4 },
    areaStyle: dashed
      ? undefined
      : {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: color + "55" },
            { offset: 1, color: color + "00" },
          ]),
        },
    animationDuration: 1100,
    animationEasing: "cubicOut",
  };
}

function buildOption(d, redBandRange) {
  return {
    grid: { left: 50, right: 18, top: 14, bottom: 38 },
    legend: { show: false },
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(12,31,64,0.95)",
      borderWidth: 0,
      padding: [8, 12],
      textStyle: {
        color: "#fff",
        fontSize: 12.5,
        fontFamily: "Inter, Pretendard, sans-serif",
      },
      axisPointer: {
        type: "line",
        lineStyle: { color: "#94a3b8", type: "dashed", width: 1 },
      },
    },
    xAxis: {
      type: "category",
      data: d.cats,
      boundaryGap: false,
      axisLine: { lineStyle: { color: "#c9d4e3" } },
      axisTick: { show: false },
      axisLabel: {
        color: "#4a5b78",
        fontSize: 12,
        fontWeight: 600,
        fontFamily: "Inter, Pretendard, sans-serif",
        margin: 10,
      },
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 100,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: "#6b7a92",
        fontSize: 11.5,
        fontFamily: "IBM Plex Mono, monospace",
        formatter: "{value}",
      },
      splitLine: { lineStyle: { color: "#e7edf6", type: "dashed" } },
    },
    series: [
      lineSeries("최근 7일 평균", d.avg, "#10b981", false),
      lineSeries("전일", d.prev, "#94a3b8", true),
      {
        ...lineSeries("금일", d.today, "#2563eb", false),
        markArea: redBandRange
          ? {
              silent: true,
              itemStyle: { color: "rgba(239,68,68,0.10)" },
              label: {
                show: true,
                position: "insideTop",
                distance: 8,
                color: "#b91c1c",
                fontSize: 12,
                fontWeight: 800,
                fontFamily: "Inter, Pretendard, sans-serif",
                backgroundColor: "rgba(255,255,255,0.85)",
                padding: [3, 8],
                borderRadius: 4,
                overflow: "none",
              },
              data: [redBandRange],
            }
          : undefined,
        markPoint: {
          symbol: "pin",
          symbolSize: 38,
          data: [{ type: "min", name: "최저", itemStyle: { color: "#dc2626" } }],
          label: {
            color: "#fff",
            fontSize: 11,
            fontWeight: 700,
            formatter: "{c}",
          },
        },
      },
    ],
  };
}

function initCmpCharts() {
  if (cmpChartEl.value && !cmpChart) {
    cmpChart = echarts.init(cmpChartEl.value, null, { renderer: "canvas" });
    cmpChart.setOption(
      buildOption(cmpData, [{ name: "혼잡 구간", xAxis: "마사IC" }, { xAxis: "한남IC" }])
    );
    new ResizeObserver(() => cmpChart && cmpChart.resize()).observe(cmpChartEl.value);
  }
  if (hourChartEl.value && !hourChart) {
    hourChart = echarts.init(hourChartEl.value, null, { renderer: "canvas" });
    hourChart.setOption(
      buildOption(hourData, [{ name: "피크 시간대", xAxis: "08시" }, { xAxis: "12시" }])
    );
    new ResizeObserver(() => hourChart && hourChart.resize()).observe(hourChartEl.value);
  }
}

watch(anaTab, (v) => {
  if (v === "dashboard") nextTick(() => initCmpCharts());
});
window.addEventListener("resize", () => {
  cmpChart && cmpChart.resize();
  hourChart && hourChart.resize();
});

onMounted(async () => {
  nextTick(() => initCmpCharts());
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

    setTimeout(() => jamMap?.invalidateSize(), 200);
  } catch (e) {
    console.warn("[Analytics jam map]", e.message);
  }
});

onBeforeUnmount(() => {
  if (jamMap) { jamMap.remove(); jamMap = null; }
  if (cmpChart) { cmpChart.dispose(); cmpChart = null; }
  if (hourChart) { hourChart.dispose(); hourChart = null; }
});
</script>

<style scoped>
.an-shell { height: 100vh; overflow: hidden; display: flex; flex-direction: column; }
.an-shell .body { flex: 1; min-height: 0; overflow: hidden; }
.an-shell .content {
  flex: 1; min-height: 0; overflow: hidden;
  display: flex !important; flex-direction: column !important; gap: 10px !important;
  padding: 12px 16px !important;
}
.an-shell .row-cmp { flex: 1;    min-height: 0; gap: 12px !important; order: 2; }
.an-shell .row-mid { flex: 1.2;  min-height: 0; gap: 12px !important; order: 1; }
/* row-cmp 단일 컬럼 (인사이트 분리됨) */
.an-shell .row-cmp { grid-template-columns: 1fr !important; }

/* 카드 패딩/여백 조절 */
.an-shell .cmp-area,
.an-shell .jam-map-card,
.an-shell .kpi-tbl-card {
  padding: 10px 14px !important;
  min-height: 0;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden;
}
.an-shell .cmp-h,
.an-shell .jam-map-card h3,
.an-shell .kpi-tbl-card h3 {
  flex-shrink: 0;
  margin-bottom: 6px !important;
}
.an-shell .cmp-grid {
  flex: 1; min-height: 0;
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 20px;
}
.an-shell .cm-chart {
  display: flex; flex-direction: column; min-height: 0;
  background: #ffffff;
  border: 1px solid #c9d4e3;
  padding: 12px 14px;
  border-radius: 2px;
}
.an-shell .cm-chart h4 { flex-shrink: 0; margin: 0; }
.an-shell .cm-head {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; margin-bottom: 8px; flex-shrink: 0; flex-wrap: wrap;
}
.an-shell .cm-legend-ext {
  display: inline-flex; gap: 14px; align-items: center;
  font-size: 12.5px; font-weight: 600; color: #0c1f40;
  font-family: "Inter, Pretendard", sans-serif;
}
.an-shell .cm-legend-ext span { display: inline-flex; align-items: center; gap: 5px; }
.an-shell .cm-legend-ext .lg-dot {
  display: inline-block; width: 10px; height: 10px; border-radius: 50%;
}
.an-shell .cm-legend-ext .lg-dot.bl { background: #2563eb; }
.an-shell .cm-legend-ext .lg-dot.gy { background: #94a3b8; }
.an-shell .cm-legend-ext .lg-dot.gr { background: #10b981; }
.an-shell .cm-echart {
  flex: 1; width: 100%; min-height: 220px; min-width: 0;
}

.an-shell .jam-leaflet { flex: 1; height: auto !important; min-height: 100px; }
.an-shell .jm-legend { flex-shrink: 0; }

.an-shell .tbl-kpi { width: 100%; border-collapse: collapse; table-layout: fixed; }
.an-shell .tbl-kpi th, .an-shell .tbl-kpi td {
  padding: 7px 8px !important;
  font-size: 13.5px !important;
  text-align: center !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.an-shell .tbl-kpi th { font-size: 12.5px !important; }
.an-shell .kpi-head {
  display: flex; align-items: baseline; justify-content: space-between;
  margin-bottom: 6px !important;
  flex-shrink: 0;
}
.an-shell .kpi-head h3 { margin: 0 !important; }
.an-shell .kpi-tbl-card .ch-link {
  color: #2563eb; font-size: 13px; font-weight: 700; cursor: pointer;
  text-decoration: none;
}
.an-shell .kpi-tbl-card .ch-link:hover { text-decoration: underline; }

.an-shell .top { padding: 10px 16px !important; flex-shrink: 0; }
.an-shell .top h1 { font-size: 20px !important; }
.an-shell .top .t-main { font-size: 24px !important; }

/* ★ 탭 패널 (구간/교차로/시간대/사고/보고서/설정) - 빔프로젝트 시연용 */
.an-shell .tab-panel {
  flex: 1; min-height: 0; overflow: hidden;
  display: flex; flex-direction: column;
  background: #ffffff;
  border: 1px solid #c9d4e3;
  border-radius: 4px;
  padding: 20px 24px;
}
.an-shell .tp-h {
  display: flex; align-items: baseline; justify-content: space-between;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 2px solid #0c1f40;
  flex-shrink: 0;
}
.an-shell .tp-h h2 {
  font-size: 24px; font-weight: 800; color: #0c1f40;
  margin: 0; display: flex; align-items: center; gap: 10px;
  letter-spacing: -0.02em;
}
.an-shell .tp-h h2 i { color: #2563eb; font-size: 22px; }
.an-shell .tp-sub { font-size: 15px; color: #4a5b78; font-weight: 600; }

.an-shell .tp-tbl {
  width: 100%; border-collapse: collapse;
  font-size: 17px;
}
.an-shell .tp-tbl th {
  background: #e3e9f2;
  padding: 14px 14px;
  text-align: left;
  font-size: 15px;
  font-weight: 700;
  color: #4a5b78;
  border-bottom: 2px solid #c9d4e3;
  letter-spacing: -0.01em;
}
.an-shell .tp-tbl td {
  padding: 14px 14px;
  border-bottom: 1px solid #d8dfe9;
  color: #0c1f40;
}
.an-shell .tp-tbl tbody tr:hover { background: #f1f5fb; }
.an-shell .tp-tbl strong { font-weight: 700; }
.an-shell .tp-tbl .mono { font-family: "IBM Plex Mono", monospace; }

.an-shell .cg-tag {
  display: inline-block; padding: 4px 10px; border-radius: 100px;
  font-size: 13.5px; font-weight: 800;
}
.an-shell .cg-tag.gr { background: rgba(4,120,87,.14); color: #047857; }
.an-shell .cg-tag.yl { background: rgba(180,83,9,.14); color: #b45309; }
.an-shell .cg-tag.or { background: rgba(180,83,9,.14); color: #b45309; }
.an-shell .cg-tag.rd { background: rgba(220,38,38,.14); color: #b91c1c; }
.an-shell .tp-tbl .up { color: #047857; font-weight: 700; }
.an-shell .tp-tbl .dn { color: #b91c1c; font-weight: 700; }

/* 교차로 분석 그리드 */
.an-shell .tp-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px;
  flex: 1; min-height: 0;
}
.an-shell .tp-card {
  background: #f1f5fb;
  border: 1px solid #c9d4e3;
  border-left: 4px solid #2563eb;
  padding: 18px 20px;
  display: flex; flex-direction: column; gap: 10px;
}
.an-shell .tpc-name {
  font-size: 18px; font-weight: 800; color: #0c1f40;
  letter-spacing: -0.01em; padding-bottom: 10px;
  border-bottom: 1px solid #c9d4e3;
}
.an-shell .tpc-row {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 15.5px; color: #4a5b78;
}
.an-shell .tpc-row strong {
  font-size: 17px; color: #0c1f40; font-weight: 800;
}

/* 보고서 관리 2-column */
.an-shell .tp-2col {
  display: grid; grid-template-columns: 1fr 1fr; gap: 24px;
  flex: 1; min-height: 0; overflow: hidden;
}
.an-shell .tp-2col > div { display: flex; flex-direction: column; min-height: 0; overflow: hidden; }
.an-shell .tp-sec {
  font-size: 17px; font-weight: 800; color: #0c1f40;
  margin: 0 0 12px; padding-bottom: 8px;
  border-bottom: 1px solid #c9d4e3;
}

/* 설정 */
.an-shell .tp-set { display: flex; flex-direction: column; gap: 14px; max-width: 520px; }
.an-shell .tps-row {
  display: grid; grid-template-columns: 200px 1fr; align-items: center; gap: 14px;
  padding: 12px 14px;
  background: #f1f5fb;
  border: 1px solid #c9d4e3;
  border-radius: 4px;
}
.an-shell .tps-row label {
  font-size: 16px; font-weight: 700; color: #0c1f40;
}
.an-shell .tps-row select {
  font-size: 15px; padding: 8px 10px;
  background: #ffffff; border: 1px solid #c9d4e3;
  font-family: inherit; color: #0c1f40;
}
.an-shell .tps-row input[type="checkbox"] {
  width: 22px; height: 22px; accent-color: #2563eb;
}

.an-shell .insight-strip { padding: 12px 16px !important; }
.an-shell .is-card { padding: 10px 14px !important; }
.an-shell .is-h { font-size: 19px !important; }
.an-shell .is-t { font-size: 16.5px !important; }
.an-shell .is-d { font-size: 14.5px !important; -webkit-line-clamp: 1 !important; }
.an-shell .is-more { font-size: 16px !important; padding: 12px 18px !important; }
.an-shell .cm-chart h4 { font-size: 18px !important; }
.an-shell .cm-legend { font-size: 14.5px !important; }
.an-shell .cmp-h h3 { font-size: 20px !important; }
.an-shell .jam-map-card h3,
.an-shell .kpi-tbl-card h3 { font-size: 20px !important; }
.an-shell .tbl-kpi { font-size: 17px; }
.an-shell .tbl-kpi th { font-size: 16px !important; padding: 12px 12px !important; }
.an-shell .tbl-kpi td { padding: 12px 12px !important; }
.an-shell .y-axis span,
.an-shell .cm-x span { font-size: 13px !important; }

/* 인사이트 가로 스트립 */
.an-shell .insight-strip {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 12px;
  align-items: center;
  padding: 8px 12px;
  background: #f1f5fb;
  border: 1px solid #c9d4e3;
  flex-shrink: 0;
}
.an-shell .is-h {
  font-size: 14.5px;
  font-weight: 800;
  color: #0c1f40;
  white-space: nowrap;
  letter-spacing: -0.01em;
}
.an-shell .is-h i { color: #2563eb; margin-right: 4px; }
.an-shell .is-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
.an-shell .is-card {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #ffffff;
  border: 1px solid #c9d4e3;
  border-left: 3px solid #c9d4e3;
  padding: 7px 10px;
  min-width: 0;
}
.an-shell .is-card:nth-child(1) { border-left-color: #dc2626; }
.an-shell .is-card:nth-child(2) { border-left-color: #b45309; }
.an-shell .is-card:nth-child(3) { border-left-color: #047857; }
.an-shell .is-card:nth-child(4) { border-left-color: #2563eb; }
.an-shell .is-card i { font-size: 16.5px; padding-top: 2px; flex-shrink: 0; }
.an-shell .is-card > div { min-width: 0; }
.an-shell .is-t {
  font-size: 15.5px;
  font-weight: 800;
  color: #0c1f40;
  letter-spacing: -0.01em;
}
.an-shell .is-d {
  font-size: 14.5px;
  color: #4a5b78;
  font-weight: 500;
  line-height: 1.35;
  margin-top: 1px;
  letter-spacing: -0.01em;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.an-shell .is-more {
  background: #ffffff;
  border: 1px solid #c9d4e3;
  color: #2563eb;
  padding: 8px 14px;
  font-size: 15.5px;
  font-weight: 700;
  cursor: pointer;
  border-radius: 2px;
  font-family: inherit;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.an-shell .is-more:hover { background: #2563eb; color: #ffffff; border-color: #2563eb; }
.an-shell .row-cmp > .cmp-area,
.an-shell .row-cmp > .insight,
.an-shell .row-mid > .card,
.an-shell .row-bot > .card {
  min-height: 0;
  display: flex; flex-direction: column;
  overflow: hidden;
}
/* 차트 높이 제한 */
.an-shell .cmp-grid { flex: 1; min-height: 0; }
.an-shell .cm-chart { display: flex; flex-direction: column; min-height: 0; }
.an-shell .chart-frame { flex: 1; min-height: 0; }
.an-shell .line-svg { height: 100% !important; }
.an-shell .jam-leaflet { flex: 1; height: auto !important; min-height: 120px; }
/* 표는 카드 안에서 fit */
.an-shell .tbl-kpi,
.an-shell .tbl-resv,
.an-shell .tbl-saved { flex: 0 0 auto; }
/* 인사이트 카드 컴팩트 */
.an-shell .insight { overflow-y: auto; }
.an-shell .ins-card { padding: 6px 0 !important; }
.top { padding: 16px 24px; border-bottom: 1px solid #1a2a45; }
.top h1 { display: flex; align-items: center; gap: 8px; }
.brand-link { display: inline-flex; align-items: center; gap: 8px; color: inherit; text-decoration: none; cursor: pointer; }
.brand-link:hover { opacity: 0.85; }
.top .dot { width: 7px; height: 7px; border-radius: 50%; background: #60a5fa; box-shadow: 0 0 8px #60a5fa; }
.t-sub { font-weight: 500; opacity: .8; }
.t-right { display: flex; align-items: center; gap: 10px; }
.btn-pri { background: #3b82f6; color: #fff; border: 0; border-radius: 6px; padding: 8px 14px; font-size: 14.5px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }

.body { display: flex; min-height: calc(100vh - 60px); }
.filter { width: 220px; background: #06101e; border-right: 1px solid #1a2a45; padding: 20px 16px; flex-shrink: 0; display: flex; flex-direction: column; gap: 20px; }
.filter h3 { font-size: 15.5px; font-weight: 700; margin: 0 0 6px; }
.f-lab { font-size: 16.5px; font-weight: 600; opacity: .85; margin-bottom: 8px; }
.f-search { position: relative; margin-bottom: 8px; }
.f-search i { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); opacity: .55; font-size: 16.5px; }
.f-search input { width: 100%; background: #0a1424; border: 1px solid #1f3055; color: #e4eeff; padding: 6px 26px 6px 10px; border-radius: 5px; font-size: 16.5px; }
.ck-list { display: flex; flex-direction: column; gap: 6px; }
.ck { display: flex; align-items: center; gap: 6px; font-size: 15.5px; cursor: pointer; }
.ck input { accent-color: #60a5fa; }
.sub-list { display: flex; flex-direction: column; gap: 4px; padding: 4px 0 4px 24px; border-left: 1px dashed #1f3055; margin-left: 8px; }
.empty-q { font-size: 15.5px; opacity: .5; padding: 6px 4px; }

.filter { width: 240px; }
.f-block { margin-bottom: 20px; padding-bottom: 18px; border-bottom: 1px solid #1a2a45; }
.f-block:last-of-type { border-bottom: 0; }
.anav { display: flex; flex-direction: column; gap: 2px; }
.anav-i { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 6px; color: rgba(228,238,255,.55); font-size: 15.5px; border: 0; background: none; cursor: pointer; font-family: inherit; text-align: left; }
.anav-i:hover { background: rgba(96,165,250,.06); color: #e4eeff; }
.anav-i.on { background: rgba(96,165,250,.15); color: #60a5fa; font-weight: 600; }
.anav-i i { width: 16px; }
.auth-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.auth-btn { display: flex; align-items: center; justify-content: center; gap: 5px; padding: 9px 6px; border: 0; border-radius: 6px; font-size: 15.5px; font-weight: 700; cursor: pointer; font-family: inherit; color: #fff; }
.auth-btn.bl { background: #3b82f6; }
.auth-btn:nth-child(2).bl { background: rgba(59,130,246,.18); color: #60a5fa; border: 1px solid rgba(59,130,246,.35); }
.auth-btn.gr { background: #10b981; }
.auth-btn.pl { background: #8b5cf6; }
.auth-btn i { font-size: 16.5px; }
.op-msg { margin-top: 8px; font-size: 15.5px; color: #34d399; text-align: center; }
.data-up { margin-top: auto; padding-top: 12px; font-size: 16.5px; opacity: .6; }
.du-l { margin-bottom: 2px; }
.du-r { font-family: "JetBrains Mono", monospace; display: flex; justify-content: space-between; align-items: center; }
.t-avatar { width: 30px; height: 30px; border-radius: 50%; background: #3b82f6; color: #fff; font-size: 15.5px; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; }

.row-mid { display: grid; grid-template-columns: 1.1fr 1fr; gap: 14px; }
.jam-map-card, .kpi-tbl-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.jam-map-card h3, .kpi-tbl-card h3 { font-size: 15.5px; font-weight: 700; margin: 0 0 12px; }
.jam-map-card { position: relative; }
.jam-leaflet { width: 100%; height: 280px; border-radius: 8px; overflow: hidden; background: #06101e; }
.jam-leaflet :deep(.leaflet-container) { background: #06101e; }
.jam-leaflet :deep(.leaflet-control-zoom a) { background: rgba(8,16,32,.85); color: #e4eeff; border-color: #1f3055; }
.jam-leaflet :deep(.ic-tip), .jam-leaflet :deep(.osm-road-tip) { background: rgba(8,16,32,.92); border: 1px solid #1f3055; color: #e4eeff; font-size: 15.5px; padding: 4px 8px; line-height: 1.55; }
.jm-legend { display: flex; align-items: center; gap: 8px; margin-top: 10px; font-size: 16.5px; opacity: .8; }
.jl-label { white-space: nowrap; }
.jl-bar { flex: 1; height: 8px; max-width: 200px; border-radius: 2px;
  background: linear-gradient(90deg, #ef4444 0%, #fb923c 33%, #fbbf24 66%, #34d399 100%); }
.jl-ticks { display: flex; justify-content: space-between; max-width: 200px; flex: 1; font-family: "JetBrains Mono", monospace; }
.tbl-kpi { width: 100%; border-collapse: collapse; font-size: 16.5px; }
.tbl-kpi th, .tbl-kpi td { padding: 8px 6px; text-align: center; border-bottom: 1px solid #1a2a45; }
.tbl-kpi th { font-weight: 600; opacity: .55; font-size: 15.5px; }
.tbl-kpi .mono { font-family: "JetBrains Mono", monospace; }
.tbl-kpi .up { color: #34d399; }
.tbl-kpi .dn { color: #f87171; }
.cg-tag { padding: 2px 8px; border-radius: 100px; font-size: 16.5px; font-weight: 700; }
.cg-tag.yl { background: rgba(245,158,11,.18); color: #fbbf24; }
.cg-tag.or { background: rgba(251,146,60,.2); color: #fb923c; }
.cg-tag.rd { background: rgba(239,68,68,.18); color: #f87171; }

.row-bot { display: grid; grid-template-columns: 1fr 1.5fr; gap: 14px; }
.resv-card, .saved-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.resv-card h3, .saved-card h3 { font-size: 15.5px; font-weight: 700; margin: 0 0 12px; }
.tbl-resv, .tbl-saved { width: 100%; border-collapse: collapse; font-size: 14.5px; }
.tbl-resv th, .tbl-resv td, .tbl-saved th, .tbl-saved td { padding: 8px 6px; text-align: left; border-bottom: 1px solid #1a2a45; }
.tbl-resv th, .tbl-saved th { font-weight: 600; opacity: .55; font-size: 16.5px; }
.tbl-resv .mono, .tbl-saved .mono { font-family: "JetBrains Mono", monospace; opacity: .85; }
.resv-st { padding: 2px 8px; border-radius: 100px; font-size: 14.5px; font-weight: 700; }
.resv-st.ok { background: rgba(96,165,250,.18); color: #60a5fa; }
.resv-st.wait { background: rgba(245,158,11,.18); color: #fbbf24; }
.more-btn { width: 100%; margin-top: 10px; background: rgba(96,165,250,.06); border: 1px solid rgba(96,165,250,.2); color: #60a5fa; padding: 7px; border-radius: 5px; font-size: 14.5px; cursor: pointer; }
.sb { font-size: 14.5px; opacity: .7; padding-left: 10px; position: relative; }
.sb::before { content: ""; position: absolute; left: 0; top: 50%; width: 6px; height: 6px; border-radius: 50%; border: 1px solid #60a5fa; transform: translateY(-50%); }
.seg-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px; margin-bottom: 8px; }
.seg { background: #0a1424; border: 1px solid #1f3055; color: rgba(228,238,255,.7); padding: 5px; font-size: 15.5px; border-radius: 4px; cursor: pointer; }
.seg.on { background: #3b82f6; border-color: #3b82f6; color: #fff; }
.date-r { font-size: 15.5px; opacity: .7; display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: #0a1424; border: 1px solid #1f3055; border-radius: 4px; }
.f-sel { width: 100%; background: #0a1424; border: 1px solid #1f3055; color: #e4eeff; padding: 6px 10px; border-radius: 5px; font-size: 15.5px; }
.reset { margin-top: auto; background: rgba(96,165,250,.08); border: 1px solid rgba(96,165,250,.25); color: #60a5fa; padding: 8px; border-radius: 5px; cursor: pointer; font-size: 16.5px; }

.content { flex: 1; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; min-width: 0; }
.metrics { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
.mt-time .mt-time-v { font-size: 15.5px; font-weight: 700; padding: 4px 0; }
.mt-time .mt-time-v i { opacity: .55; margin-left: 4px; }
.mt-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 14px; display: grid; grid-template-columns: 1fr auto; grid-template-rows: auto auto auto; gap: 4px 12px; }
.mt-lab { grid-column: 1; font-size: 16.5px; opacity: .75; }
.mt-val { grid-column: 1; font-size: 30px; font-weight: 800; }
.mt-val.gr { color: #34d399; }
.mt-val.or { color: #fbbf24; }
.mt-u { font-size: 14.5px; font-weight: 500; opacity: .65; margin-left: 2px; }
.mt-spark { grid-column: 2; grid-row: 1 / 3; align-self: center; width: 80px; }
.sp { width: 100%; height: 24px; }
.mt-d { grid-column: 1 / -1; font-size: 15.5px; opacity: .65; padding-top: 4px; border-top: 1px solid #1a2a45; margin-top: 4px; }
.mt-d .up-r { color: #f87171; }
.mt-d .dn { color: #f87171; }

.row-cmp { display: grid; grid-template-columns: 1fr 260px; gap: 14px; }
.cmp-area { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.cmp-h { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.cmp-h h3 { font-size: 15.5px; font-weight: 700; margin: 0; }
.seg-sub { font-size: 16.5px; opacity: .55; font-weight: 400; margin-left: 4px; }
.cmp-tabs { display: flex; gap: 4px; background: #06101e; border: 1px solid #1f3055; border-radius: 6px; padding: 2px; }
.ct { background: none; border: 0; color: rgba(228,238,255,.6); font-size: 14.5px; padding: 5px 12px; border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; }
.ct.on { background: rgba(96,165,250,.15); color: #60a5fa; }
.cmp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.cm-chart h4 { font-size: 16.5px; font-weight: 600; margin: 0 0 8px; }
.cm-legend { display: flex; flex-wrap: wrap; gap: 10px; font-size: 16.5px; opacity: .8; margin-bottom: 8px; }
.lg-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; }
.lg-dot.bl { background: #60a5fa; }
.lg-dot.gy { background: #9ca3af; }
.lg-dot.gr { background: #10b981; }
.lg-dot.bl-d { background: #3b82f6; opacity: .5; }
.lg-dot.gr-d { background: #10b981; opacity: .5; }
.line-svg { width: 100%; height: 180px; }
.chart-frame { display: flex; gap: 6px; align-items: stretch; }
.y-axis { display: flex; flex-direction: column; justify-content: space-between; font-size: 15.5px; opacity: .5; padding: 2px 0; width: 22px; text-align: right; }
.chart-frame .line-svg { flex: 1; }
.cm-u { font-size: 16.5px; opacity: .55; font-weight: 400; }
.cm-chart h4 { display: flex; align-items: baseline; gap: 4px; }
.cm-x { display: flex; justify-content: space-between; font-size: 15.5px; opacity: .55; padding: 4px 0 0; }

.insight { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 14px; }
.insight h3 { font-size: 14.5px; font-weight: 700; margin: 0 0 8px; display: flex; align-items: center; gap: 6px; }
.ins-card { display: flex; gap: 10px; padding: 10px 0; border-bottom: 1px solid #1a2a45; }
.ins-card:last-of-type { border-bottom: 0; }
.ins-card > i { font-size: 17.5px; padding-top: 1px; flex-shrink: 0; }
.ic-t { font-size: 15.5px; font-weight: 700; margin-bottom: 3px; }
.ic-d { font-size: 15.5px; opacity: .7; line-height: 1.5; }
.ai-detail-btn { width: 100%; margin-top: 12px; background: rgba(96,165,250,.1); border: 1px solid rgba(96,165,250,.3); color: #60a5fa; padding: 9px; border-radius: 6px; font-size: 16.5px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
.insight h3.mt { margin-top: 14px; }
.insight h4 { font-size: 16.5px; opacity: .75; margin: 0 0 8px; font-weight: 500; }
.ins { display: flex; gap: 8px; padding: 8px 0; font-size: 14.5px; line-height: 1.55; border-bottom: 1px solid #1a2a45; }
.ins:last-of-type { border-bottom: 0; }
.ins-ic { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.rec { font-size: 14.5px; padding: 6px 0; display: flex; align-items: flex-start; gap: 6px; line-height: 1.5; }
.rec i { color: #60a5fa; padding-top: 2px; }
.rep-d { display: flex; align-items: center; gap: 8px; padding: 8px; background: rgba(96,165,250,.06); border-radius: 6px; }
.rep-d > i { font-size: 25px; color: #60a5fa; }
.rep-d > div { flex: 1; min-width: 0; }
.rep-t { font-size: 16.5px; font-weight: 700; }
.rep-s { font-size: 16.5px; opacity: .65; }
.rep-dl { background: rgba(96,165,250,.15); border: 0; color: #60a5fa; width: 26px; height: 26px; border-radius: 4px; cursor: pointer; }

.row-bot { display: grid; grid-template-columns: 1fr 1.2fr; gap: 14px; }
.flow-card, .deep-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.flow-card h3, .deep-card h3 { font-size: 15.5px; font-weight: 700; margin: 0 0 12px; }
.flow-grid { display: grid; grid-template-columns: 1fr 100px 1fr; gap: 10px; align-items: center; }
.fc { padding: 6px; }
.fc-h { font-size: 16.5px; margin-bottom: 6px; }
.fc-lg { font-size: 16.5px; opacity: .75; margin-bottom: 6px; display: flex; gap: 8px; }
.flow-svg { width: 100%; height: 120px; }
.fc-x { display: flex; justify-content: space-between; font-size: 15.5px; opacity: .55; padding-top: 4px; }
.fc-mid { display: flex; flex-direction: column; gap: 6px; font-size: 15.5px; padding: 0 8px; }
.m-row { display: flex; align-items: center; gap: 6px; opacity: .8; }
.m-row .d { width: 6px; height: 6px; border-radius: 50%; border: 1px solid #60a5fa; }

.b-red { background: rgba(239,68,68,.18); color: #f87171; font-size: 16.5px; font-weight: 700; padding: 1px 8px; border-radius: 4px; margin-left: 4px; }
.deep-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 14px; }
.dl-h { font-size: 16.5px; font-weight: 700; margin-bottom: 10px; }
.dl-i { display: flex; gap: 10px; padding: 8px 0; align-items: flex-start; }
.dl-i i { font-size: 17.5px; padding-top: 2px; }
.dl-i > div { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.dl-i strong { font-size: 15.5px; }
.dl-i span { font-size: 15.5px; opacity: .7; line-height: 1.45; }
.deep-right { display: flex; flex-direction: column; gap: 10px; }
.dr-c h4 { font-size: 15.5px; font-weight: 600; margin: 0 0 4px; opacity: .85; }
.dr-u { font-size: 14.5px; opacity: .55; font-weight: 400; margin-left: 2px; }
.sp-c { width: 100%; height: 80px; }
.dr-x { display: flex; justify-content: space-between; font-size: 15.5px; opacity: .55; }
</style>
