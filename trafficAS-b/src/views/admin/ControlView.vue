<template>
  <div class="cc-shell">
    <aside class="side">
      <RouterLink to="/" class="brand"><span class="dot"></span> Traffic <em>AS</em></RouterLink>
      <nav class="snav">
        <button v-for="n in nav" :key="n.id" class="snav-i"
          :class="{ on: tab === n.id }" @click="tab = n.id">
          <i :class="n.icon"></i>{{ n.label }}
        </button>
      </nav>
      <SideWeather />
    </aside>

    <div class="main">
      <header class="top">
        <h1><a class="t-main" @click="goHome">교통정보센터</a></h1>
        <div class="t-right">
          <span class="hdr-time"><i class="bi bi-clock"></i> 마지막 업데이트 <strong>14:32:18</strong></span>
          <button class="km-toggle" :class="{ on: autoRefresh }" @click="autoRefresh = !autoRefresh" :aria-pressed="autoRefresh">
            <span class="km-dot"></span>
            <span class="km-lab">자동 새로고침</span>
            <span class="km-state">{{ autoRefresh ? 'ON' : 'OFF' }}</span>
          </button>
          <DeptSwitcher />
          <div class="t-user"><i class="bi bi-person-circle"></i> 교통정보센터 매니저 <i class="bi bi-chevron-down"></i></div>
        </div>
      </header>

      <template v-if="tab === 'center'">
      <section class="stat-row">
        <div class="st bad">
          <i class="bi bi-exclamation-triangle-fill"></i>
          <span class="lab">혼잡 악화 구간</span>
          <span class="val">3</span>
          <span class="dlt up">↑ +1</span>
        </div>
        <div class="st warn">
          <i class="bi bi-speedometer"></i>
          <span class="lab">속도 급감 구간</span>
          <span class="val">2</span>
          <span class="dlt up">↑ +1</span>
        </div>
        <div class="st alert">
          <i class="bi bi-bell-fill"></i>
          <span class="lab">미처리 이벤트</span>
          <span class="val">{{ queue.length }}</span>
        </div>
        <div class="st ok">
          <i class="bi bi-camera-video-fill"></i>
          <span class="lab">정상 카메라 비율</span>
          <span class="val">96<small>%</small></span>
          <span class="sub">(24/25)</span>
        </div>
        <div class="ts">
          <span>최종 갱신 14:32:18</span>
          <button class="ts-btn">전체 보기 <i class="bi bi-chevron-right"></i></button>
        </div>
      </section>

      <section class="grid-mid">
        <div class="map-card">
          <div class="mc-head">
            <h2>실시간 교통 흐름 지도</h2>
            <div class="mc-toggle">
              <button class="mt" :class="{ on: mapMode === 'flow' }" @click="mapMode = 'flow'">교통흐름</button>
              <button class="mt" :class="{ on: mapMode === 'cctv' }" @click="mapMode = 'cctv'">CCTV</button>
            </div>
          </div>
          <div class="map-area">
            <div ref="flowMapEl" class="flow-leaflet"></div>
            <div class="map-legend">
              <span><i class="dot gr"></i>원활</span>
              <span><i class="dot yl"></i>보통</span>
              <span><i class="dot or"></i>혼잡</span>
              <span><i class="dot rd"></i>정체</span>
            </div>
          </div>
        </div>

        <div class="queue-card">
          <div class="qc-head">
            <h2>긴급 처리 큐 <span class="qc-badge">{{ queue.length }}</span></h2>
            <button class="qc-more">전체 보기 <i class="bi bi-chevron-right"></i></button>
          </div>
          <div class="qc-th">
            <span>우선순위</span><span>구간 / 내용</span><span>경과</span><span>확인</span>
          </div>
          <div v-for="(q, i) in queue" :key="i" class="qc-row">
            <span class="qc-num" :class="q.sev">{{ i + 1 }}</span>
            <div class="qc-body">
              <div class="qc-t">{{ q.line }} <span class="sev-pill" :class="q.sev">{{ q.sevLabel }}</span></div>
              <div class="qc-d">{{ q.detail }}</div>
            </div>
            <span class="qc-time">{{ q.time }}</span>
            <div class="qc-acts">
              <button class="btn-ok" @click="resolveQueue(i, '확인')">확인</button>
            </div>
          </div>
          <div v-if="!queue.length" class="qc-empty">처리 대기 항목이 없습니다.</div>
          <div class="qc-foot">
            <i class="bi bi-info-circle"></i>
            실제 사고·정체 처리는 관할 구청·시청·경찰에서 수행하며, 본 큐는 모니터링·확인 용도입니다.
          </div>
        </div>
      </section>

      <section class="grid-bot">
        <div class="bot-card cam">
          <div class="bc-head">
            <h3>선택 카메라 <span class="bc-sub">{{ activeCam.title }}</span></h3>
            <span class="live"><span class="dot-live"></span> LIVE</span>
          </div>
          <div class="cam-main">
            <video :src="activeCam.src" autoplay muted loop playsinline :key="activeCam.src"></video>
            <span class="cam-ts">2026-05-16 14:32:18</span>
            <span class="cam-loc">{{ activeCam.loc }}</span>
            <button class="cam-zoom"><i class="bi bi-arrows-fullscreen"></i></button>
          </div>
          <div class="cam-thumbs">
            <button class="thumb-nav" @click="camIdx > 0 && camIdx--"><i class="bi bi-chevron-left"></i></button>
            <div v-for="(c, i) in cams" :key="c.src" class="thumb" :class="{ active: camIdx === i }" @click="camIdx = i">
              <video :src="c.src" autoplay muted loop playsinline></video>
              <div class="thumb-lab">{{ c.label }}</div>
            </div>
            <button class="thumb-nav" @click="camIdx < cams.length - 1 && camIdx++"><i class="bi bi-chevron-right"></i></button>
          </div>
          <button class="cam-more-btn">다른 카메라 보기</button>
        </div>

        <div class="bot-card chart">
          <div class="bc-head">
            <h3>선택 구간 속도 추이</h3>
            <div class="bc-tabs">
              <button v-for="t in chartTabs" :key="t.id" class="bt" :class="{ on: chartTab === t.id }" @click="chartTab = t.id">{{ t.label }}</button>
            </div>
          </div>
          <div class="chart-sub">강변북로 (구리 → 한남)</div>
          <div class="chart-y"><span>속도 (km/h)</span></div>
          <svg class="line-chart" viewBox="0 0 400 160" preserveAspectRatio="none">
            <defs>
              <linearGradient id="cg1" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#3b82f6" stop-opacity=".25"/>
                <stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/>
              </linearGradient>
              <linearGradient id="cg2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#ef4444" stop-opacity=".35"/>
                <stop offset="100%" stop-color="#ef4444" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <line x1="0" y1="32" x2="400" y2="32" stroke="rgba(255,255,255,.04)"/>
            <line x1="0" y1="64" x2="400" y2="64" stroke="rgba(255,255,255,.04)"/>
            <line x1="0" y1="96" x2="400" y2="96" stroke="rgba(255,255,255,.04)"/>
            <line x1="0" y1="128" x2="400" y2="128" stroke="rgba(255,255,255,.04)"/>
            <rect x="320" y="0" width="80" height="160" fill="url(#cg2)"/>
            <path :d="chartLine" fill="none" stroke="#3b82f6" stroke-width="2"/>
            <path :d="chartArea" fill="url(#cg1)"/>
            <path :d="chartTail" fill="none" stroke="#ef4444" stroke-width="2"/>
            <circle cx="400" cy="128" r="4" fill="#ef4444"/>
          </svg>
          <div class="chart-x"><span v-for="x in chartX" :key="x">{{ x }}</span></div>
          <div class="chart-legend">
            <span><i class="dot bl"></i> 평균 속도</span>
            <span><i class="dot rd"></i> 현재 속도</span>
          </div>
        </div>

        <div class="bot-card evt-detail-card">
          <div class="bc-head">
            <h3>선택 이벤트 상세 <span class="b-mi">미처리</span></h3>
          </div>
          <div class="ed-rows">
            <div class="ed-row"><span>이벤트 유형</span><strong>혼잡 악화</strong></div>
            <div class="ed-row"><span>구간</span><strong>강변북로 (구리 → 한남)</strong></div>
            <div class="ed-row"><span>발생 시간</span><strong>2025-05-16 14:30:12</strong></div>
            <div class="ed-row"><span>우선순위</span><strong class="rd">1 (긴급)</strong></div>
            <div class="ed-row"><span>현재 상태</span><strong>혼잡</strong></div>
            <div class="ed-row"><span>설명</span><strong>교통량 증가로 속도 저하</strong></div>
            <div class="ed-row"><span>조치 이력</span><strong>-</strong></div>
          </div>
          <div class="ed-acts">
            <button class="ea ok" @click="actionFlash('확인 처리됨')">확인</button>
            <button class="ea fwd" @click="actionFlash('타 부서 전달됨')">부서 전달</button>
            <button class="ea end" @click="actionFlash('처리 완료')">처리 완료</button>
          </div>
          <div v-if="flashMsg" class="ea-msg">{{ flashMsg }}</div>
        </div>

        <div class="bot-card guide-card">
          <div class="bc-head"><h3>관제 가이드</h3><button class="bc-more">전체 가이드 <i class="bi bi-chevron-right"></i></button></div>
          <ol class="gd-list">
            <li>
              <span class="gd-n">1</span>
              <div>
                <strong>이벤트 식별</strong>
                <span>지도·카메라·긴급 처리 큐에서 사고·정체·고장을 확인합니다.</span>
              </div>
            </li>
            <li>
              <span class="gd-n">2</span>
              <div>
                <strong>심각도 분류</strong>
                <span>교통사고(매우 심각) · 정체(심각) · 차량고장(주의) 기준으로 우선순위를 부여합니다.</span>
              </div>
            </li>
            <li>
              <span class="gd-n">3</span>
              <div>
                <strong>외부 기관 통보</strong>
                <span>실제 처리는 관할 구청·시청·경찰 담당. 본 시스템은 모니터링·기록 용도입니다.</span>
              </div>
            </li>
            <li>
              <span class="gd-n">4</span>
              <div>
                <strong>확인 / 상황 종료</strong>
                <span>현장 해소를 확인하면 큐에서 [확인]으로 처리하고 로그에 보존됩니다.</span>
              </div>
            </li>
          </ol>
        </div>
      </section>

      <section class="grid-bot-2">
        <div class="bot-card log-row-card">
          <div class="bc-head"><h3>최근 이벤트 로그</h3></div>
          <table class="log-tbl">
            <thead><tr><th>시간</th><th>우선순위</th><th>이벤트</th><th>구간</th><th>상태</th><th>조치</th><th>담당자</th></tr></thead>
            <tbody>
              <tr v-for="l in eventLog" :key="l.id">
                <td class="mono">{{ l.time }}</td>
                <td><span class="lp-num" :class="l.sev">{{ l.priority }}</span></td>
                <td>{{ l.title }}</td>
                <td>{{ l.section }}</td>
                <td><span class="lp-st" :class="l.stTone">{{ l.st }}</span></td>
                <td><span class="lp-act" :class="l.actTone">{{ l.act }}</span></td>
                <td>{{ l.who }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="bot-card quick-card">
          <div class="bc-head"><h3>빠른 작업</h3></div>
          <div class="quick-grid">
            <button class="qa" @click="actionFlash('구간 확대')"><i class="bi bi-zoom-in"></i><span>구간 확대</span><em>선택 구간 상세 지도</em></button>
            <button class="qa" @click="actionFlash('카메라 보기')"><i class="bi bi-camera-video"></i><span>카메라 보기</span><em>해당 구간 카메라 목록</em></button>
            <button class="qa" @click="actionFlash('이벤트 접수')"><i class="bi bi-bell"></i><span>이벤트 접수</span><em>선택 이벤트 접수</em></button>
            <button class="qa" @click="actionFlash('부서 전달')"><i class="bi bi-share"></i><span>부서 전달</span><em>유관 부서로 전달</em></button>
            <button class="qa" @click="actionFlash('상황 종료')"><i class="bi bi-x-circle"></i><span>상황 종료</span><em>이벤트 처리 완료</em></button>
            <button class="qa" @click="actionFlash('보고서 생성')"><i class="bi bi-file-earmark-text"></i><span>보고서 생성</span><em>이벤트 리포트 생성</em></button>
          </div>
        </div>
      </section>

      </template>

      <section v-if="tab === 'map'" class="card pnl">
        <h3>지도 패널</h3>
        <div class="map-stub"><i class="bi bi-map"></i><div>실시간 도로망 상태 — 11개 자치구 색상 표시</div></div>
      </section>

      <section v-if="tab === 'events'" class="card pnl">
        <h3>이벤트 — 전체 목록 ({{ queue.length }}건)</h3>
        <table class="pnl-tbl">
          <thead><tr><th>우선순위</th><th>구간</th><th>내용</th><th>경과</th></tr></thead>
          <tbody>
            <tr v-for="(q, i) in queue" :key="i"><td>{{ q.sevLabel }}</td><td>{{ q.line }}</td><td>{{ q.detail }}</td><td>{{ q.time }}</td></tr>
            <tr v-if="!queue.length"><td colspan="4" class="pnl-empty">처리 대기 항목이 없습니다.</td></tr>
          </tbody>
        </table>
      </section>

      <section v-if="tab === 'cams'" class="card pnl">
        <h3>카메라 — {{ cams.length }}대 운영</h3>
        <div class="cam-tab-grid">
          <div v-for="(c, i) in cams" :key="c.src" class="cam-tab" :class="{ on: camIdx === i }" @click="camIdx = i">
            <video :src="c.src" autoplay muted loop playsinline></video>
            <div class="ct-info"><strong>{{ c.label }}</strong><span>{{ c.title }}</span></div>
          </div>
        </div>
      </section>

      <section v-if="tab === 'stats'" class="card pnl">
        <h3>교통통계 <span class="bc-sub">시간대별 평균 속도</span></h3>
        <div class="bc-tabs">
          <button v-for="t in chartTabs" :key="t.id" class="bt" :class="{ on: chartTab === t.id }" @click="chartTab = t.id">{{ t.label }}</button>
        </div>
        <svg class="line-chart" viewBox="0 0 400 160" preserveAspectRatio="none">
          <path :d="chartLine" fill="none" stroke="#3b82f6" stroke-width="2"/>
        </svg>
        <div class="chart-x"><span v-for="x in chartX" :key="x">{{ x }}</span></div>
      </section>

      <section v-if="tab === 'reports'" class="card pnl">
        <h3>보고서</h3>
        <div class="rep-rows">
          <div v-for="r in reportRows" :key="r.t" class="rep-r">
            <i class="bi bi-file-earmark-text"></i>
            <div><strong>{{ r.t }}</strong><span>{{ r.d }}</span></div>
            <button class="bt-dl"><i class="bi bi-download"></i></button>
          </div>
        </div>
      </section>

      <section v-if="tab === 'settings'" class="card pnl">
        <h3>설정</h3>
        <div class="set-row"><label>알림 사운드</label><input type="checkbox" v-model="setSound" /></div>
        <div class="set-row"><label>큐 자동 갱신 (초)</label><input type="number" v-model.number="setRefresh" min="5" max="300" /></div>
        <div class="set-row"><label>지도 모드 기본값</label>
          <select v-model="setMapMode"><option value="flow">교통흐름</option><option value="cctv">CCTV</option></select>
        </div>
        <button class="btn-save" @click="saveSet"><i class="bi bi-check2"></i> 저장</button>
        <div v-if="setMsg" class="set-msg">{{ setMsg }}</div>
      </section>

      <footer class="foot">Traffic AS · v2.1.0</footer>
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

const tab = ref("center");
const autoRefresh = ref(true);
function goHome() {
  tab.value = "center";
  window.scrollTo({ top: 0, behavior: "smooth" });
}
const nav = [
  { id: "center",  icon: "bi bi-broadcast",         label: "교통정보센터" },
  { id: "map",     icon: "bi bi-map",               label: "지도" },
  { id: "events",  icon: "bi bi-bell",              label: "이벤트" },
  { id: "cams",    icon: "bi bi-camera-video",      label: "카메라" },
  { id: "stats",   icon: "bi bi-bar-chart",         label: "교통통계" },
  { id: "reports", icon: "bi bi-file-earmark-text", label: "보고서" },
  { id: "settings",icon: "bi bi-gear",              label: "설정" },
];

const queue = ref([
  { line: "강변북로 (구리 → 한남)",     detail: "교통사고 발생 — 2개 차로 통제", time: "2분", sev: "critical", sevLabel: "교통사고" },
  { line: "올림픽대로 (가양 → 여의도)", detail: "차량 정체 (평균 18km/h)",       time: "9분", sev: "serious",  sevLabel: "정체" },
  { line: "내부순환로 (정릉 → 성수)",   detail: "차량 정체 — 사고 여파",           time: "8분", sev: "serious",  sevLabel: "정체" },
  { line: "경부고속도로 (서울TG 부근)", detail: "차량 고장 — 갓길 정차",           time: "5분", sev: "caution",  sevLabel: "차량고장" },
  { line: "동부간선도로 (수락 → 성수)", detail: "차량 정체 — 출근시간 누적",       time: "4분", sev: "caution",  sevLabel: "정체" },
]);

const mapMode = ref("flow");

const cams = [
  { src: "/road1.mp4", label: "한남대교 진입",   title: "강변북로 (구리 → 한남)",   loc: "강변북로 구리 → 한남 (한남대교 진입)" },
  { src: "/road2.mp4", label: "반포대교 부근",   title: "올림픽대로 (반포 부근)",   loc: "올림픽대로 반포대교 부근" },
  { src: "/road4.mp4", label: "동작대교 부근",   title: "올림픽대로 (동작 부근)",   loc: "올림픽대로 동작대교 부근" },
  { src: "/road3.mp4", label: "성수대교 부근",   title: "강변북로 (성수 부근)",     loc: "강변북로 성수대교 부근" },
];
const camIdx = ref(0);
const activeCam = computed(() => cams[camIdx.value]);

const chartTabs = [
  { id: "1h", label: "1시간" },
  { id: "3h", label: "3시간" },
  { id: "6h", label: "6시간" },
];
const chartTab = ref("1h");

const chartData = {
  "1h": { line: "M0,46 L40,42 L80,50 L120,52 L160,58 L200,68 L240,78 L280,88 L320,108 L360,118 L400,128", tail: "M320,108 L360,118 L400,128", x: ["13:30", "13:45", "14:00", "14:15", "14:30"] },
  "3h": { line: "M0,30 L50,38 L100,35 L150,48 L200,55 L250,72 L300,90 L350,108 L400,128", tail: "M300,90 L350,108 L400,128", x: ["11:30", "12:15", "13:00", "13:45", "14:30"] },
  "6h": { line: "M0,28 L60,40 L120,52 L180,58 L240,70 L300,86 L360,110 L400,128", tail: "M300,86 L360,110 L400,128", x: ["08:30", "10:00", "11:30", "13:00", "14:30"] },
};
const chartLine = computed(() => chartData[chartTab.value].line);
const chartTail = computed(() => chartData[chartTab.value].tail);
const chartArea = computed(() => `${chartData[chartTab.value].line} L400,160 L0,160 Z`);
const chartX = computed(() => chartData[chartTab.value].x);

function resolveQueue(idx, action) {
  const item = queue.value[idx];
  if (!item) return;
  queue.value.splice(idx, 1);
  flashMsg.value = `${item.line} ${action} 처리`;
  clearFlashLater();
}

const flashMsg = ref("");
let flashTimer = null;
function clearFlashLater() {
  if (flashTimer) clearTimeout(flashTimer);
  flashTimer = setTimeout(() => { flashMsg.value = ""; }, 2200);
}
function actionFlash(msg) {
  flashMsg.value = msg;
  clearFlashLater();
}

// === Leaflet 실시간 교통 흐름 지도 ===
const flowMapEl = ref(null);
let flowMap = null;

const incidents = [
  { lat: 37.5500, lng: 127.0900, num: 1, color: "#ef4444", label: "교통사고" },
  { lat: 37.5300, lng: 126.8800, num: 2, color: "#ef4444", label: "차량 정체" },
  { lat: 37.5500, lng: 127.0680, num: 3, color: "#f59e0b", label: "속도 급감" },
];

onMounted(async () => {
  if (!flowMapEl.value) return;
  await new Promise(r => setTimeout(r, 50));
  try {
    flowMap = L.map(flowMapEl.value, {
      center: [37.5520, 127.0050],
      zoom: 11,
      minZoom: 10,
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
      flowMap.removeLayer(vworld);
      cartoDark.addTo(flowMap);
    });
    vworld.addTo(flowMap);

    // OSM Overpass에서 서울 주요 간선 도로만 (motorway/trunk) → 데이터 80% 감소
    const ways = await loadOSMRoads(
      "osm-roads-control-seoul-v2",
      "37.46,126.86,37.66,127.15",
      ["motorway", "trunk"]
    );
    if (ways && ways.length > 0) {
      renderOSMRoads(flowMap, ways);
    }

    incidents.forEach(inc => {
      const html = `<div style="
        width:24px;height:24px;border-radius:50%;
        background:${inc.color};border:2px solid #fff;
        color:#fff;font-weight:800;font-size:12px;
        display:flex;align-items:center;justify-content:center;
      ">${inc.num}</div>`;
      L.marker([inc.lat, inc.lng], {
        icon: L.divIcon({ className: "inc-pin", html, iconSize: [24, 24] }),
      }).addTo(flowMap).bindTooltip(`${inc.num}. ${inc.label}`, { direction: "top", className: "ic-tip" });
    });

    setTimeout(() => flowMap?.invalidateSize(), 200);
    setTimeout(() => flowMap?.invalidateSize(), 800);
  } catch (e) {
    console.warn("[Control flow map]", e.message);
  }
});

onBeforeUnmount(() => {
  if (flowMap) { flowMap.remove(); flowMap = null; }
});

const eventLog = [
  { id: 1, time: "14:30:12", priority: 1, sev: "critical", title: "강변북로 혼잡 악화", section: "구리 → 한남", st: "미처리", stTone: "wait",  act: "확인",      actTone: "ok",  who: "-" },
  { id: 2, time: "14:28:05", priority: 2, sev: "serious",  title: "올림픽대로 속도 급감", section: "가양 → 여의도", st: "접수", stTone: "rec",   act: "부서 전달", actTone: "fwd", who: "김관제" },
  { id: 3, time: "14:22:41", priority: 3, sev: "serious",  title: "내부순환로 정체",     section: "성동 → 성수",   st: "처리 중", stTone: "prog", act: "상황 종료", actTone: "end", who: "이관제" },
  { id: 4, time: "14:18:33", priority: 4, sev: "caution",  title: "경부고속도로 사고",   section: "서초 IC 부근",  st: "처리 완료", stTone: "done", act: "상세 보기", actTone: "view", who: "박관제" },
];

const reportRows = [
  { t: "일일 운영 보고서", d: "2026-05-17 14:32 생성" },
  { t: "주간 정체 분석 보고서", d: "2026-05-11 ~ 05-17" },
  { t: "이벤트 처리 로그", d: "최근 30일 누적" },
];
const setSound = ref(true);
const setRefresh = ref(15);
const setMapMode = ref("flow");
const setMsg = ref("");
function saveSet() {
  setMsg.value = "설정 저장 완료";
  setTimeout(() => { setMsg.value = ""; }, 1800);
}

</script>

<style scoped>
/* shell/brand/snav/top/bell/bdg/user는 admin-shared.css */
.side { width: 180px; }
.main { flex: 1; padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; min-width: 0; }
.t-moon { color: #fbbf24; font-size: 17px; cursor: pointer; }

.stat-row { display: grid; grid-template-columns: repeat(4, 1fr) auto; gap: 12px; align-items: center; background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 12px 16px; }
.st { display: flex; align-items: center; gap: 10px; padding-right: 16px; border-right: 1px solid #1a2a45; }
.st:last-of-type { border-right: 0; }
.st i { font-size: 18px; }
.st.bad i, .st.bad .val { color: #ef4444; }
.st.warn i, .st.warn .val { color: #fbbf24; }
.st.alert i, .st.alert .val { color: #ef4444; }
.st.ok i, .st.ok .val { color: #34d399; }
.st .lab { font-size: 12px; opacity: .75; }
.st .val { font-size: 20px; font-weight: 800; margin-left: auto; }
.st .val small { font-size: 12px; font-weight: 700; opacity: .85; }
.st .dlt { font-size: 11px; font-weight: 700; margin-left: 4px; color: #ef4444; }
.st .sub { font-size: 11px; opacity: .55; margin-left: 4px; }
.ts { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; font-size: 11.5px; opacity: .65; }
.ts-btn { background: rgba(96,165,250,.08); border: 1px solid rgba(96,165,250,.25); color: #60a5fa; padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; }

.grid-mid { display: grid; grid-template-columns: 1.55fr 1fr; gap: 12px; }
.map-card, .queue-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 14px; display: flex; flex-direction: column; }
.mc-head, .qc-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.mc-head h2, .qc-head h2 { font-size: 14px; font-weight: 700; margin: 0; }
.mc-toggle { display: flex; gap: 4px; background: #0a1424; border: 1px solid #1f3055; border-radius: 6px; padding: 2px; }
.mt { padding: 5px 14px; font-size: 12px; background: none; border: 0; color: rgba(228,238,255,.55); border-radius: 4px; cursor: pointer; }
.mt.on { background: rgba(96,165,250,.18); color: #60a5fa; }

.map-area { position: relative; background: #06101e; border-radius: 8px; overflow: hidden; height: 400px; }
.flow-leaflet { width: 100%; height: 100%; background: #06101e; }
.flow-leaflet :deep(.leaflet-container) { background: #06101e; }
.flow-leaflet :deep(.leaflet-control-zoom a) { background: rgba(8,16,32,.85); color: #e4eeff; border-color: #1f3055; }
.flow-leaflet :deep(.ic-tip), .flow-leaflet :deep(.osm-road-tip) { background: rgba(8,16,32,.92); border: 1px solid #1f3055; color: #e4eeff; font-size: 11px; padding: 4px 8px; line-height: 1.55; }
.map-legend { position: absolute; bottom: 14px; left: 14px; display: flex; gap: 14px; background: rgba(8,16,32,.85); padding: 6px 12px; border-radius: 6px; font-size: 11px; }
.map-legend i.dot { display: inline-block; width: 16px; height: 4px; border-radius: 2px; margin-right: 4px; vertical-align: middle; }
.map-legend i.gr { background: #34d399; }
.map-legend i.yl { background: #f59e0b; }
.map-legend i.or { background: #fb923c; }
.map-legend i.rd { background: #ef4444; }

.qc-badge { display: inline-block; min-width: 18px; height: 18px; line-height: 18px; padding: 0 6px; border-radius: 999px; background: #ef4444; color: #fff; font-size: 11px; font-weight: 700; text-align: center; margin-left: 4px; }
.qc-more { background: none; border: 0; color: #60a5fa; font-size: 12px; cursor: pointer; }
.qc-th { display: grid; grid-template-columns: 60px 1fr 50px 90px; gap: 8px; padding: 7px 0; border-bottom: 1px solid #1a2a45; font-size: 11px; opacity: .55; font-weight: 600; }
.qc-row { display: grid; grid-template-columns: 60px 1fr 50px 90px; gap: 8px; padding: 10px 0; border-bottom: 1px solid #1a2a45; align-items: center; }
.qc-num { display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; font-weight: 800; font-size: 12px; color: #fff; }
.qc-num.critical { background: #ef4444; }
.qc-num.serious  { background: #f97316; }
.qc-num.caution  { background: #f59e0b; }
.qc-body { min-width: 0; }
.qc-t { font-size: 12.5px; font-weight: 600; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.qc-d { font-size: 11.5px; opacity: .6; margin-top: 1px; }
.sev-pill { padding: 2px 7px; border-radius: 3px; font-size: 10.5px; font-weight: 700; }
.sev-pill.critical { background: #ef4444; color: #fff; }
.sev-pill.serious  { background: rgba(249,115,22,.2); color: #fb923c; }
.sev-pill.caution  { background: rgba(245,158,11,.18); color: #fbbf24; }
.qc-time { font-size: 11.5px; opacity: .7; }
.qc-acts { display: flex; gap: 4px; }
.btn-ok, .btn-fwd { padding: 5px 10px; border-radius: 4px; font-size: 11.5px; font-weight: 600; cursor: pointer; border: 0; }
.btn-ok { background: #3b82f6; color: #fff; }
.btn-fwd { background: rgba(255,255,255,.06); color: rgba(228,238,255,.7); border: 1px solid #1f3055; }
.qc-empty { padding: 18px 0; text-align: center; font-size: 12px; opacity: .55; }
.ea-msg { margin-top: 6px; font-size: 11px; color: #34d399; text-align: center; }
.cam-more-btn { width: 100%; margin-top: 8px; padding: 7px; background: rgba(96,165,250,.06); border: 1px solid rgba(96,165,250,.2); color: #60a5fa; border-radius: 5px; font-size: 11.5px; font-weight: 600; cursor: pointer; }

.b-mi { background: rgba(245,158,11,.2); color: #fbbf24; font-size: 10.5px; font-weight: 700; padding: 1px 8px; border-radius: 4px; margin-left: 4px; }
.evt-detail-card .ed-rows { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.ed-row { display: flex; justify-content: space-between; font-size: 11.5px; padding: 4px 0; border-bottom: 1px dashed rgba(255,255,255,.05); }
.ed-row > span { opacity: .65; }
.ed-row > strong { font-weight: 700; }
.ed-row .rd { color: #f87171; }
.ed-acts { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.ed-acts .ea.end { grid-column: 1 / -1; background: #10b981; color: #fff; }

.role-card .role-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: rgba(96,165,250,.06); border: 1px solid rgba(96,165,250,.2); border-radius: 6px; margin-bottom: 12px; }
.role-lab { font-size: 11px; opacity: .65; }
.role-val { font-size: 13px; font-weight: 700; display: inline-flex; align-items: center; gap: 6px; }
.role-val i { color: #34d399; }
.role-h { font-size: 11.5px; opacity: .75; font-weight: 600; margin-bottom: 8px; }
.role-perms { display: flex; flex-direction: column; gap: 6px; }
.rp { display: flex; align-items: center; gap: 8px; font-size: 11px; }
.rp-tag { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px; flex-shrink: 0; }
.rp-tag.bl { background: rgba(96,165,250,.18); color: #60a5fa; }
.rp-tag.gr { background: rgba(16,185,129,.18); color: #34d399; }
.rp span:last-child { opacity: .7; }

.log-tbl { width: 100%; border-collapse: collapse; font-size: 11.5px; }
.log-tbl th, .log-tbl td { padding: 8px; text-align: left; border-bottom: 1px solid #1a2a45; }
.log-tbl th { font-weight: 600; opacity: .55; font-size: 10.5px; }
.log-tbl .mono { font-family: "JetBrains Mono", monospace; }
.lp-num { display: inline-flex; width: 20px; height: 20px; border-radius: 50%; color: #fff; font-size: 10.5px; font-weight: 800; align-items: center; justify-content: center; }
.lp-num.critical { background: #ef4444; }
.lp-num.serious  { background: #f97316; }
.lp-num.caution  { background: #f59e0b; }
.lp-st, .lp-act { padding: 1px 7px; border-radius: 4px; font-size: 10.5px; font-weight: 700; }
.lp-st.wait { background: rgba(245,158,11,.2); color: #fbbf24; }
.lp-st.rec  { background: rgba(96,165,250,.18); color: #60a5fa; }
.lp-st.prog { background: rgba(96,165,250,.15); color: #60a5fa; }
.lp-st.done { background: rgba(16,185,129,.15); color: #34d399; }
.lp-act.ok   { background: #3b82f6; color: #fff; }
.lp-act.fwd  { background: rgba(96,165,250,.15); color: #60a5fa; border: 1px solid rgba(96,165,250,.3); }
.lp-act.end  { background: rgba(16,185,129,.15); color: #34d399; }
.lp-act.view { background: rgba(255,255,255,.06); color: rgba(228,238,255,.7); }

.quick-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.qa { background: rgba(255,255,255,.03); border: 1px solid #1f3055; color: #e4eeff; padding: 12px 8px; border-radius: 6px; cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 4px; font-family: inherit; }
.qa:hover { background: rgba(96,165,250,.08); }
.qa i { font-size: 18px; color: #60a5fa; }
.qa span { font-size: 11.5px; font-weight: 700; }
.qa em { font-size: 10px; opacity: .6; font-style: normal; }
.qc-foot { margin-top: auto; padding-top: 10px; font-size: 11px; opacity: .6; display: flex; align-items: center; gap: 6px; }
.dot-live { width: 6px; height: 6px; border-radius: 50%; background: #34d399; box-shadow: 0 0 4px #34d399; display: inline-block; }

.grid-bot { display: grid; grid-template-columns: 1.25fr 0.95fr 1.3fr 1fr; gap: 12px; }
.grid-bot-2 { display: grid; grid-template-columns: 1.6fr 1fr; gap: 12px; }
.bot-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 14px; min-width: 0; }
.bc-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.bc-head h3 { font-size: 13px; font-weight: 700; margin: 0; }
.bc-sub { font-size: 11px; opacity: .55; font-weight: 400; margin-left: 4px; }
.live { font-size: 11px; color: #34d399; display: inline-flex; align-items: center; gap: 4px; font-weight: 700; }

.cam-main { position: relative; aspect-ratio: 16/10; background: #000; border-radius: 6px; overflow: hidden; margin-bottom: 8px; }
.cam-main video { width: 100%; height: 100%; object-fit: cover; }
.cam-ts { position: absolute; top: 8px; left: 10px; font-size: 10.5px; background: rgba(0,0,0,.55); padding: 2px 6px; border-radius: 3px; font-family: "JetBrains Mono", monospace; }
.cam-loc { position: absolute; bottom: 8px; left: 10px; font-size: 11px; background: rgba(0,0,0,.55); padding: 3px 8px; border-radius: 3px; }
.cam-zoom { position: absolute; bottom: 8px; right: 10px; width: 24px; height: 24px; border-radius: 4px; background: rgba(0,0,0,.6); color: #fff; border: 0; cursor: pointer; }
.cam-thumbs { display: flex; align-items: stretch; gap: 6px; }
.thumb-nav { width: 22px; background: rgba(255,255,255,.04); border: 1px solid #1f3055; color: rgba(228,238,255,.65); border-radius: 4px; cursor: pointer; flex-shrink: 0; }
.thumb { flex: 1; border-radius: 5px; overflow: hidden; border: 2px solid transparent; cursor: pointer; position: relative; }
.thumb.active { border-color: #3b82f6; }
.thumb video { width: 100%; aspect-ratio: 16/9; object-fit: cover; display: block; }
.thumb-lab { font-size: 10.5px; opacity: .65; text-align: center; padding: 2px 0; }

.chart-sub { font-size: 11px; opacity: .65; margin-bottom: 8px; }
.bc-tabs { display: flex; gap: 2px; background: #0a1424; border: 1px solid #1f3055; border-radius: 4px; padding: 2px; }
.bt { background: none; border: 0; padding: 4px 10px; font-size: 11px; color: rgba(228,238,255,.55); border-radius: 3px; cursor: pointer; }
.bt.on { background: rgba(96,165,250,.18); color: #60a5fa; }
.chart-y { font-size: 10px; opacity: .55; margin-bottom: 4px; }
.line-chart { width: 100%; height: 160px; display: block; }
.chart-x { display: flex; justify-content: space-between; font-family: "JetBrains Mono", monospace; font-size: 10px; opacity: .55; padding: 4px 0; }
.chart-legend { display: flex; gap: 14px; font-size: 11px; opacity: .65; margin-top: 6px; }
.chart-legend i.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; }
.chart-legend i.bl { background: #3b82f6; }
.chart-legend i.rd { background: #ef4444; }

.evt-summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }
.es { background: rgba(255,255,255,.02); border: 1px solid #1a2a45; border-radius: 6px; padding: 8px; display: flex; gap: 8px; }
.es i { font-size: 16px; padding-top: 2px; }
.text-bl { color: #60a5fa; }
.text-or { color: #fbbf24; }
.text-gr { color: #34d399; }
.es-t { font-size: 11.5px; font-weight: 700; }
.es-d { font-size: 11px; opacity: .75; margin-top: 1px; }
.es-ts { font-size: 10px; opacity: .5; margin-top: 2px; font-family: "JetBrains Mono", monospace; }

.evt-row { display: grid; grid-template-columns: 1fr 1fr 100px; gap: 12px; }
.vid-thumbs { display: flex; gap: 6px; margin-top: 6px; }
.vthumb { flex: 1; border-radius: 5px; overflow: hidden; position: relative; }
.vthumb video { width: 100%; aspect-ratio: 16/10; object-fit: cover; display: block; }
.vthumb span { position: absolute; bottom: 4px; left: 4px; font-size: 9.5px; background: rgba(0,0,0,.6); padding: 1px 5px; border-radius: 2px; font-family: "JetBrains Mono", monospace; }

.es-row { display: flex; justify-content: space-between; padding: 5px 0; font-size: 11.5px; border-bottom: 1px solid #1a2a45; }
.es-row:last-of-type { border-bottom: 0; }
.es-row span { opacity: .7; }
.es-row strong { font-weight: 700; }

.evt-actions { display: flex; flex-direction: column; gap: 6px; }
.ea { padding: 9px; border-radius: 5px; font-size: 12.5px; font-weight: 600; cursor: pointer; border: 0; }
.ea.ok  { background: #3b82f6; color: #fff; }
.ea.fwd, .ea.end { background: rgba(255,255,255,.04); color: rgba(228,238,255,.75); border: 1px solid #1f3055; }


.pnl { padding: 18px; }
.pnl h3 { font-size: 14px; font-weight: 700; margin: 0 0 14px; }
.map-stub { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; height: 320px; background: #06101e; border: 1px dashed #1f3055; border-radius: 8px; opacity: .85; }
.map-stub > i { font-size: 36px; color: #60a5fa; }
.pnl-tbl { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.pnl-tbl th, .pnl-tbl td { padding: 9px 10px; text-align: left; border-bottom: 1px solid #1a2a45; }
.pnl-tbl th { font-weight: 600; opacity: .6; font-size: 11.5px; }
.pnl-empty { text-align: center; opacity: .55; padding: 24px 0; }
.cam-tab-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.cam-tab { border: 2px solid transparent; border-radius: 8px; overflow: hidden; cursor: pointer; background: #06101e; }
.cam-tab.on { border-color: #3b82f6; }
.cam-tab video { width: 100%; aspect-ratio: 16/9; object-fit: cover; display: block; }
.ct-info { padding: 8px 10px; display: flex; flex-direction: column; }
.ct-info strong { font-size: 12.5px; }
.ct-info span { font-size: 11px; opacity: .65; }
.rep-rows { display: flex; flex-direction: column; gap: 8px; }
.rep-r { display: flex; align-items: center; gap: 12px; padding: 12px; background: #06101e; border: 1px solid #1f3055; border-radius: 6px; }
.rep-r > i { font-size: 20px; color: #60a5fa; }
.rep-r > div { flex: 1; display: flex; flex-direction: column; }
.rep-r strong { font-size: 13px; }
.rep-r span { font-size: 11px; opacity: .6; }
.bt-dl { width: 32px; height: 32px; background: rgba(96,165,250,.12); border: 0; color: #60a5fa; border-radius: 5px; cursor: pointer; }
.set-row { display: grid; grid-template-columns: 200px 1fr; gap: 12px; align-items: center; padding: 10px 0; border-bottom: 1px solid #1a2a45; font-size: 13px; }
.set-row input[type="number"], .set-row select { background: #06101e; border: 1px solid #1f3055; color: #e4eeff; padding: 6px 10px; border-radius: 5px; font-size: 12.5px; max-width: 200px; }
.set-row input[type="checkbox"] { accent-color: #60a5fa; }
.btn-save { margin-top: 14px; background: #3b82f6; color: #fff; border: 0; padding: 9px 16px; border-radius: 6px; font-size: 12.5px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
.set-msg { margin-top: 10px; font-size: 12px; color: #34d399; }

@media (max-width: 1400px) {
  .grid-mid { grid-template-columns: 1fr; }
  .grid-bot { grid-template-columns: 1fr; }
}
</style>
