<template>
  <div class="cc-shell" :class="{ 'side-collapsed': !sideOpen }">
    <aside class="side">
      <div class="side-top">
        <RouterLink to="/" class="brand" v-if="sideOpen">Traffic <em>AS</em></RouterLink>
        <button class="side-toggle" @click="sideOpen = !sideOpen"
          :aria-label="sideOpen ? '사이드바 접기' : '사이드바 펼치기'"
          :title="sideOpen ? '사이드바 접기' : '사이드바 펼치기'">
          <i :class="sideOpen ? 'bi bi-arrow-left-short' : 'bi bi-arrow-right-short'"></i>
        </button>
      </div>
      <nav class="snav">
        <button v-for="n in nav" :key="n.id" class="snav-i"
          :class="{ on: tab === n.id }" @click="tab = n.id">
          <i :class="n.icon"></i>{{ n.label }}
        </button>
      </nav>
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
          <div class="hdr-bell-wrap">
            <button class="hdr-bell" :class="{ critical: hasCritical, on: showAlerts }" @click="showAlerts = !showAlerts">
              <i class="bi bi-bell-fill"></i>
              <span v-if="liveAlerts.length" class="hdr-bell-c">{{ liveAlerts.length }}</span>
            </button>
            <div v-if="showAlerts" class="hdr-bell-pop" @click.stop>
              <div class="hbp-h">
                <i class="bi bi-exclamation-octagon-fill"></i>
                <strong>실시간 알림</strong>
                <span class="hbp-c">{{ liveAlerts.length }}건</span>
                <button class="hbp-x" @click="showAlerts = false"><i class="bi bi-x-lg"></i></button>
              </div>
              <div class="hbp-list">
                <div v-for="a in liveAlerts" :key="a.id"
                  class="ac-row" :class="a.sev"
                  @click="focusAlert(a); showAlerts = false">
                  <div class="ac-sev"><i :class="a.icon"></i></div>
                  <div class="ac-body">
                    <div class="ac-t">{{ a.title }}</div>
                    <div class="ac-d">{{ a.detail }}</div>
                    <div class="ac-meta">
                      <span class="ac-loc"><i class="bi bi-geo-alt"></i> {{ a.place }}</span>
                      <span class="ac-time">{{ a.time }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="!liveAlerts.length" class="ac-empty">활성 알림이 없습니다.</div>
              </div>
            </div>
          </div>
          <DeptSwitcher />
          <div class="t-user"><i class="bi bi-person-circle"></i> 교통정보센터 매니저 <i class="bi bi-chevron-down"></i></div>
        </div>
      </header>

      <template v-if="tab === 'center'">
      <section class="stat-row api-row">
        <div class="api-h">
          <i class="bi bi-broadcast-pin"></i>
          <span class="api-h-t">ITS Open API 실시간 지표</span>
          <span class="api-h-sub">서울 · 국도/도시고속도로</span>
        </div>
        <div class="st bad">
          <i class="bi bi-exclamation-triangle-fill"></i>
          <div class="st-body">
            <span class="lab">혼잡 악화 구간</span>
            <span class="val">3<span class="dlt up">↑ +1</span></span>
          </div>
        </div>
        <div class="st warn">
          <i class="bi bi-speedometer2"></i>
          <div class="st-body">
            <span class="lab">속도 급감 구간</span>
            <span class="val">2<span class="dlt up">↑ +1</span></span>
          </div>
        </div>
        <div class="st alert">
          <i class="bi bi-bell-fill"></i>
          <div class="st-body">
            <span class="lab">미처리 이벤트</span>
            <span class="val">{{ queue.length }}</span>
          </div>
        </div>
        <div class="st ok">
          <i class="bi bi-camera-video-fill"></i>
          <div class="st-body">
            <span class="lab">정상 CCTV</span>
            <span class="val">96<small>%</small> <span class="sub">(24/25)</span></span>
          </div>
        </div>
        <div class="ts">
          <i class="bi bi-arrow-clockwise"></i>
          <span>{{ camNowTime }}</span>
        </div>
      </section>

      <section class="grid-mid">
        <div class="map-card">
          <div class="mc-head">
            <h2>실시간 교통 흐름 지도</h2>
            <div class="mc-right">
              <div class="mc-weather-wrap">
                <button class="mc-weather-chip" @click="showWeather = !showWeather" :class="{ on: showWeather }">
                  <i :class="weatherSummary.icon" :style="{ color: weatherSummary.color }"></i>
                  <span class="mwc-temp">{{ weatherSummary.temp }}°</span>
                  <span class="mwc-cond">{{ weatherSummary.condition }}</span>
                  <i class="bi" :class="showWeather ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
                </button>
                <div v-if="showWeather" class="mc-weather-pop" @click.stop>
                  <SideWeather />
                </div>
              </div>
              <div class="mc-toggle">
                <button class="mt" :class="{ on: mapMode === 'flow' }" @click="mapMode = 'flow'">교통흐름</button>
                <button class="mt" :class="{ on: mapMode === 'cctv' }" @click="mapMode = 'cctv'">CCTV</button>
              </div>
            </div>
          </div>
          <div class="map-area">
            <div ref="flowMapEl" class="flow-leaflet"></div>
            <div class="map-legend">
              <span v-if="mapMode === 'flow'"><i class="dot gr"></i>원활</span>
              <span v-if="mapMode === 'flow'"><i class="dot yl"></i>보통</span>
              <span v-if="mapMode === 'flow'"><i class="dot or"></i>혼잡</span>
              <span v-if="mapMode === 'flow'"><i class="dot rd"></i>정체</span>
              <span v-if="mapMode === 'cctv'"><i class="dot bl"></i>CCTV ({{ cctvMarkerCount }}대)</span>
              <span v-if="mapMode === 'cctv' && cctvLoading">로딩 중…</span>
            </div>
          </div>
        </div>

        <!-- 우측 컬럼: 카메라 (위, 크게) + VMS (아래, 작게) -->
        <div class="right-stack">
          <div class="bot-card cam">
            <div class="bc-head">
              <h3>선택 카메라 <span class="bc-sub">{{ activeCam.title }}</span></h3>
              <span class="live"><span class="dot-live"></span> LIVE</span>
            </div>
            <div class="cam-main">
              <video ref="mainCamEl" :src="activeCam.src" autoplay muted loop playsinline preload="auto" :key="activeCam.src"></video>
              <span class="cam-ts">{{ camNowTime }}</span>
              <span class="cam-loc">{{ activeCam.loc }}</span>
              <div class="cam-controls">
                <button class="cam-ctl cam-send" @click="sendToReview" title="단속관리팀 전송" :disabled="sendBusy">
                  <i :class="sendBusy ? 'bi bi-check2-circle' : 'bi bi-send-fill'"></i>
                </button>
                <button class="cam-ctl" @click="toggleMainMute" title="소리"><i :class="mainMuted ? 'bi bi-volume-mute' : 'bi bi-volume-up'"></i></button>
                <button class="cam-zoom" @click="enterFullscreen(mainCamEl)" title="전체화면"><i class="bi bi-arrows-fullscreen"></i></button>
              </div>
            </div>
            <div v-if="sendToast" class="send-toast">
              <i class="bi bi-check-circle-fill"></i>
              <span>{{ sendToast }}</span>
            </div>
            <div class="cam-thumbs">
              <button class="thumb-nav" @click="camIdx > 0 && focusVideo(camIdx - 1)"><i class="bi bi-chevron-left"></i></button>
              <div v-for="(c, i) in cams" :key="c.src" class="thumb" :class="{ active: camIdx === i }" @click="focusVideo(i)">
                <div class="thumb-ph">
                  <i class="bi bi-camera-video-fill"></i>
                </div>
                <div class="thumb-lab">{{ c.label }}</div>
              </div>
              <button class="thumb-nav" @click="camIdx < cams.length - 1 && focusVideo(camIdx + 1)"><i class="bi bi-chevron-right"></i></button>
            </div>
          </div>

          <section class="vms-card">
            <div class="vms-head">
              <h3><i class="bi bi-megaphone-fill"></i> VMS 도로 전광판 제어</h3>
              <span class="vms-sub">{{ vmsDevices.length }}개</span>
            </div>
            <div class="vms-body">
              <div class="vms-left">
                <select class="vms-sel" v-model="vmsTarget">
                  <option v-for="v in vmsDevices" :key="v.id" :value="v.id">{{ v.id }} · {{ v.loc }}</option>
                </select>
                <input v-model="vmsMsg" class="vms-input" maxlength="40" placeholder="메시지 입력" />
                <div class="vms-tmpl">
                  <button class="vms-tmpl-b" @click="vmsMsg = '⚠ 사고 — 우회 권장'">사고</button>
                  <button class="vms-tmpl-b" @click="vmsMsg = '⚡ 정체 — 안전 운행'">정체</button>
                  <button class="vms-tmpl-b" @click="vmsMsg = '🌧 노면 미끄럼 주의'">기상</button>
                  <button class="vms-tmpl-b" @click="vmsMsg = ''">초기화</button>
                </div>
                <button class="vms-send" :disabled="!vmsMsg.trim()" @click="sendVMS"><i class="bi bi-send-fill"></i> 송출</button>
              </div>
              <div class="vms-right">
                <div class="vms-screen">
                  <div class="vms-screen-led">{{ vmsMsg.trim() || '메시지 입력' }}</div>
                  <div class="vms-screen-meta">
                    <span>{{ currentVms.loc }}</span>
                    <span class="vms-on"><span class="dot-live"></span> {{ currentVms.status }}</span>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </section>


      </template>

      <section v-if="tab === 'cams'" class="card pnl">
        <h3>카메라 — {{ cams.length }}대 운영</h3>
        <div class="cam-tab-grid">
          <div v-for="(c, i) in cams" :key="c.src" class="cam-tab" :class="{ on: camIdx === i }" @click="openCamZoom(i)">
            <video :ref="(el) => setCamVideoRef(el, i)" :src="c.src" muted loop playsinline preload="metadata"></video>
            <div class="ct-info"><strong>{{ c.label }}</strong><span>{{ c.title }}</span></div>
            <button class="ct-zoom" @click.stop="openCamZoom(i)" title="확대">
              <i class="bi bi-arrows-fullscreen"></i>
            </button>
          </div>
        </div>
      </section>

      <!-- 카메라 확대 모달 -->
      <div v-if="camZoom !== null" class="cam-zoom-bg" @click.self="camZoom = null">
        <div class="cam-zoom-modal">
          <div class="czm-h">
            <div class="czm-t">
              <i class="bi bi-camera-video-fill"></i>
              <strong>{{ cams[camZoom].label }}</strong>
              <span class="czm-sub">{{ cams[camZoom].title }}</span>
              <span class="czm-live"><span class="dot-live"></span> LIVE</span>
            </div>
            <button class="czm-x" @click="camZoom = null"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="czm-body">
            <video :src="cams[camZoom].src" :key="cams[camZoom].src" autoplay muted loop playsinline></video>
            <span class="czm-loc">{{ cams[camZoom].loc }}</span>
          </div>
        </div>
      </div>

      <section v-if="tab === 'reports'" class="card pnl">
        <h3>보고서 <span class="bc-sub">교통정보센터 전용</span></h3>
        <div class="rep-date-row">
          <label>기준 날짜 <input type="date" v-model="ctrlReportDate" class="rep-date" /></label>
        </div>
        <div class="rep-rows">
          <div v-for="r in reportRows" :key="r.key" class="rep-r">
            <i class="bi bi-file-earmark-text"></i>
            <div><strong>{{ r.t }}</strong><span>{{ r.d }}</span></div>
            <button class="bt-dl" @click="downloadDeptReport('control', r.key, { date: ctrlReportDate })" title="CSV 다운로드"><i class="bi bi-download"></i></button>
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

    <!-- CCTV 라이브 모달 -->
    <div v-if="cctvModal" class="cctv-modal-bg" @click.self="closeCctv">
      <div class="cctv-modal">
        <div class="cm-h">
          <div class="cm-t">
            <i class="bi bi-broadcast"></i>
            <strong>{{ cctvModal.name }}</strong>
            <span class="cm-live"><span class="dot-live"></span> LIVE</span>
          </div>
          <button class="cm-x" @click="closeCctv"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="cm-body">
          <video ref="cctvVideoEl" autoplay muted playsinline controls></video>
          <div v-if="cctvError" class="cm-err">{{ cctvError }}</div>
        </div>
        <div class="cm-foot">
          <span><i class="bi bi-geo-alt"></i> {{ cctvModal.lat.toFixed(5) }}, {{ cctvModal.lng.toFixed(5) }}</span>
          <a :href="cctvModal.url" target="_blank" rel="noopener" class="cm-link">원본 스트림 <i class="bi bi-box-arrow-up-right"></i></a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from "vue";
import { RouterLink } from "vue-router";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { loadOSMRoads, renderOSMRoads } from "@/composables/useOSMRoads";
import DeptSwitcher from "@/components/dashboard/DeptSwitcher.vue";
import { useReportDownload } from "@/composables/useReportDownload";
import { useViolationQueue } from "@/composables/useViolationQueue";
import { fmtDateTime, enterFullscreen, captureFrameDataURL } from "@/composables/useVideoUtils";
const { downloadDeptReport } = useReportDownload();
const { submitViolation } = useViolationQueue();
import SideWeather from "@/components/dashboard/SideWeather.vue";
import { INITIAL_DISTRICTS_WEATHER, DISTRICT_LIST } from "@/data/weather";

const tab = ref("center");
const autoRefresh = ref(true);
const sideOpen = ref(true);
function goHome() {
  tab.value = "center";
  window.scrollTo({ top: 0, behavior: "smooth" });
}
const nav = [
  { id: "center",  icon: "bi bi-broadcast",         label: "교통정보센터" },
  { id: "cams",    icon: "bi bi-camera-video",      label: "카메라" },
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

// 카메라 탭 확대 모달
const camZoom = ref(null);
function openCamZoom(i) {
  camIdx.value = i;
  camZoom.value = i;
}

// 🚨 실시간 알림 패널
const liveAlerts = ref([
  { id: 1, sev: "critical", icon: "bi bi-exclamation-octagon-fill",
    title: "교통사고 발생", detail: "2개 차로 통제 · 우회 안내 필요",
    place: "강변북로 한남TG", time: "14:32", lat: 37.5258, lng: 126.9967 },
  { id: 2, sev: "serious",  icon: "bi bi-traffic-light",
    title: "정체 심화", detail: "평균 18 km/h · 평소 대비 -52%",
    place: "올림픽대로 가양", time: "14:30", lat: 37.5683, lng: 126.8569 },
  { id: 3, sev: "caution",  icon: "bi bi-tools",
    title: "차량 고장 신고", detail: "갓길 정차 · 견인 요청 진행 중",
    place: "경부고속도로 서울TG", time: "14:27", lat: 37.4737, lng: 127.0376 },
  { id: 4, sev: "info",     icon: "bi bi-cloud-rain-heavy-fill",
    title: "노면 결빙 주의", detail: "기상청 도로 경보 — 안전운행",
    place: "내부순환로 정릉터널", time: "14:21", lat: 37.6058, lng: 127.0152 },
]);
const showAlerts = ref(false);
const hasCritical = computed(() => liveAlerts.value.some((a) => a.sev === "critical"));
function focusAlert(a) {
  if (flowMap && a.lat && a.lng) {
    flowMap.flyTo([a.lat, a.lng], 14, { duration: 0.9 });
  }
}

// 📢 VMS 전광판 제어
const vmsDevices = [
  { id: "VMS-01", loc: "강변북로 한남TG 진입",  status: "정상" },
  { id: "VMS-02", loc: "올림픽대로 가양",        status: "정상" },
  { id: "VMS-03", loc: "내부순환로 정릉",        status: "정상" },
  { id: "VMS-04", loc: "동부간선 수락",          status: "점검중" },
];
const vmsTarget = ref(vmsDevices[0].id);
const vmsMsg = ref("");
const vmsBroadcasts = ref([
  { time: "14:18", target: "VMS-02", msg: "올림픽대로 정체 — 우회 권장" },
  { time: "13:55", target: "VMS-01", msg: "안전운행 — 빗길 주의" },
]);
const currentVms = computed(() => vmsDevices.find((v) => v.id === vmsTarget.value) || vmsDevices[0]);
function sendVMS() {
  if (!vmsMsg.value.trim()) return;
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  vmsBroadcasts.value.unshift({
    time: `${p(d.getHours())}:${p(d.getMinutes())}`,
    target: vmsTarget.value,
    msg: vmsMsg.value.trim(),
  });
  if (vmsBroadcasts.value.length > 10) vmsBroadcasts.value.length = 10;
  vmsMsg.value = "";
}

// 지도 헤더 날씨 칩 + 팝오버
const showWeather = ref(false);
const weatherSummary = computed(() => {
  const d = INITIAL_DISTRICTS_WEATHER[DISTRICT_LIST[0]];
  return { temp: d.temp, condition: d.condition, icon: d.icon, color: d.color };
});

// ────── ITS Open API · CCTV (서울 한정) ──────
const CCTV_API_KEY = "76c70eaf15d84a42af8c569681f5ae12";
const CCTV_BASE = import.meta.env.DEV ? "/its/cctvInfo" : "https://openapi.its.go.kr:9443/cctvInfo";
// 서울 행정구역 bbox (대략) — 외곽 지역 컷
const SEOUL_BBOX = { minX: 126.76, maxX: 127.18, minY: 37.41, maxY: 37.70 };
const cctvMarkers = [];
const cctvMarkerCount = ref(0);
const cctvLoading = ref(false);
const cctvModal = ref(null);
const cctvError = ref("");
const cctvVideoEl = ref(null);
let hlsInstance = null;

function clearCctvMarkers() {
  cctvMarkers.forEach((m) => flowMap && flowMap.removeLayer(m));
  cctvMarkers.length = 0;
  cctvMarkerCount.value = 0;
}

async function loadCctv() {
  if (!flowMap) return;
  // zoom-gate: 너무 멀리서 보면 호출 안 함 (API/마커 부담 ↓)
  if (flowMap.getZoom() < 11) {
    clearCctvMarkers();
    return;
  }
  cctvLoading.value = true;
  try {
    const b = flowMap.getBounds();
    // 지도 영역과 서울 bbox 교집합 → 서울 외곽은 컷
    const minX = Math.max(b.getWest(), SEOUL_BBOX.minX).toFixed(6);
    const maxX = Math.min(b.getEast(), SEOUL_BBOX.maxX).toFixed(6);
    const minY = Math.max(b.getSouth(), SEOUL_BBOX.minY).toFixed(6);
    const maxY = Math.min(b.getNorth(), SEOUL_BBOX.maxY).toFixed(6);
    // 교집합 없으면 종료 (지도가 서울 밖일 때)
    if (+maxX <= +minX || +maxY <= +minY) {
      clearCctvMarkers();
      cctvLoading.value = false;
      return;
    }

    // 서울 도심 — its(국도) + ex(도시고속도로) 둘 다
    const types = ["its", "ex"];
    let all = [];
    for (const t of types) {
      const url = `${CCTV_BASE}?apiKey=${CCTV_API_KEY}&type=${t}&cctvType=2` +
        `&minX=${minX}&maxX=${maxX}&minY=${minY}&maxY=${maxY}&getType=json`;
      try {
        const res = await fetch(url);
        const data = await res.json();
        all.push(...(data?.response?.data || []));
      } catch (e) {
        console.warn("[CCTV fetch]", t, e.message);
      }
    }
    // 좌표 기준 중복 제거
    const seen = new Set();
    all = all.filter((c) => {
      const k = `${c.coordy},${c.coordx}`;
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    });
    // 응답 안에서도 서울 bbox 외 항목 제거 (API가 가끔 경계 밖 반환)
    all = all.filter((c) => {
      const lat = +c.coordy, lng = +c.coordx;
      return lng >= SEOUL_BBOX.minX && lng <= SEOUL_BBOX.maxX
          && lat >= SEOUL_BBOX.minY && lat <= SEOUL_BBOX.maxY;
    });
    // 마커 최대 50개로 상한
    if (all.length > 50) all = all.slice(0, 50);
    clearCctvMarkers();
    all.forEach((c) => {
      const lat = +c.coordy;
      const lng = +c.coordx;
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;
      const icon = L.divIcon({
        className: "cctv-pin",
        html: `<i class="bi bi-camera-video-fill"></i>`,
        iconSize: [22, 22],
        iconAnchor: [11, 11],
      });
      const marker = L.marker([lat, lng], { icon }).addTo(flowMap);
      marker.bindTooltip(c.cctvname || "CCTV", {
        direction: "top",
        offset: [0, -8],
        className: "cctv-tip",
      });
      marker.on("click", () => openCctv(c));
      cctvMarkers.push(marker);
    });
    cctvMarkerCount.value = cctvMarkers.length;
  } finally {
    cctvLoading.value = false;
  }
}

async function attachHls(videoEl, url) {
  // Safari/iOS는 native HLS 지원
  if (videoEl.canPlayType("application/vnd.apple.mpegurl")) {
    videoEl.src = url;
    return;
  }
  // 다른 브라우저는 hls.js lazy import
  try {
    const Hls = (await import("hls.js")).default;
    if (Hls.isSupported()) {
      if (hlsInstance) { hlsInstance.destroy(); hlsInstance = null; }
      hlsInstance = new Hls();
      hlsInstance.loadSource(url);
      hlsInstance.attachMedia(videoEl);
      hlsInstance.on(Hls.Events.ERROR, (_, data) => {
        if (data.fatal) cctvError.value = "스트림 재생 오류 — 잠시 후 다시 시도해주세요.";
      });
    } else {
      videoEl.src = url;
    }
  } catch (e) {
    cctvError.value = "HLS 모듈 로드 실패";
  }
}

function openCctv(c) {
  cctvError.value = "";
  cctvModal.value = {
    name: c.cctvname || "CCTV",
    url: c.cctvurl,
    lat: +c.coordy,
    lng: +c.coordx,
  };
  nextTick(() => {
    if (cctvVideoEl.value && c.cctvurl) {
      attachHls(cctvVideoEl.value, c.cctvurl);
    }
  });
}

function closeCctv() {
  cctvModal.value = null;
  if (hlsInstance) { hlsInstance.destroy(); hlsInstance = null; }
}

// mapMode 변경 → CCTV 로드/제거
watch(mapMode, async (m) => {
  if (m === "cctv") {
    await loadCctv();
  } else {
    clearCctvMarkers();
  }
});

const cams = [
  { src: "/0513.mp4", label: "강변북로 구간 A", title: "강변북로 (구리 → 한남)",   loc: "강변북로 구리 → 한남 (실시간)" },
  { src: "/1.mp4",    label: "올림픽대로 구간 B", title: "올림픽대로 (반포 부근)", loc: "올림픽대로 반포 부근 (실시간)" },
];
const camIdx = ref(0);
const activeCam = computed(() => cams[camIdx.value]);

// 메인 카메라 — 라이브 영상이라 소리/전체화면만 제공
const mainCamEl = ref(null);
const mainMuted = ref(true);
function toggleMainMute() {
  if (!mainCamEl.value) return;
  mainCamEl.value.muted = !mainCamEl.value.muted;
  mainMuted.value = mainCamEl.value.muted;
}
// 실시간 시계
const camNowTime = ref("");
let camTimeTimer = null;

// 단속관리팀 전송 (캡처 + 메타데이터 푸시)
const sendBusy = ref(false);
const sendToast = ref("");
let sendToastTimer = null;
function sendToReview() {
  if (sendBusy.value) return;
  const image = captureFrameDataURL(mainCamEl, { outWidth: 640, quality: 0.85 });
  if (!image) {
    sendToast.value = "영상 준비 중입니다";
    if (sendToastTimer) clearTimeout(sendToastTimer);
    sendToastTimer = setTimeout(() => (sendToast.value = ""), 2200);
    return;
  }
  sendBusy.value = true;
  const item = submitViolation({
    image,
    place: activeCam.value?.loc || "관제센터 전송 영상",
    camera: activeCam.value?.label || "CTRL-AUTO",
  });
  sendToast.value = `단속관리팀 전송 완료 · ${item.plate} (${item.detectSpeed}km/h)`;
  if (sendToastTimer) clearTimeout(sendToastTimer);
  sendToastTimer = setTimeout(() => {
    sendToast.value = "";
    sendBusy.value = false;
  }, 2200);
}

// 비디오 1개만 재생 — 클릭 시 다른 비디오 일시정지
const camVideoRefs = ref([]);
function setCamVideoRef(el, i) {
  if (el) camVideoRefs.value[i] = el;
  else camVideoRefs.value[i] = null;
}
function focusVideo(i) {
  camIdx.value = i;
  camVideoRefs.value.forEach((v, idx) => {
    if (!v) return;
    if (idx === i) { v.play().catch(() => {}); }
    else { v.pause(); }
  });
}
watch(camIdx, (i) => {
  camVideoRefs.value.forEach((v, idx) => {
    if (!v) return;
    if (idx === i) v.play().catch(() => {});
    else v.pause();
  });
});

// === Leaflet 실시간 교통 흐름 지도 ===
const flowMapEl = ref(null);
let flowMap = null;

// 카메라 탭 진입 시 활성 비디오 1개만 재생
watch(() => tab.value, (t) => {
  if (t === "cams") {
    setTimeout(() => focusVideo(camIdx.value), 50);
  }
});

// 페이지 비활성화 시 모든 비디오 정지 (탭 전환·창 최소화)
function handleVisibility() {
  if (document.hidden) {
    camVideoRefs.value.forEach((v) => v && v.pause());
    const mains = document.querySelectorAll(".ops-shell video, .cc-shell video");
    mains.forEach((v) => v.pause && v.pause());
  } else {
    camVideoRefs.value.forEach((v, i) => {
      if (v && i === camIdx.value) v.play().catch(() => {});
    });
  }
}
document.addEventListener("visibilitychange", handleVisibility);

onMounted(async () => {
  camNowTime.value = fmtDateTime();
  camTimeTimer = setInterval(() => { camNowTime.value = fmtDateTime(); }, 1000);
  if (!flowMapEl.value) return;
  await new Promise(r => setTimeout(r, 50));
  try {
    flowMap = L.map(flowMapEl.value, {
      center: [37.5520, 127.0050],
      zoom: 11,
      minZoom: 10,
      maxZoom: 18,
      zoomControl: false,
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


    setTimeout(() => flowMap?.invalidateSize(), 200);
    setTimeout(() => flowMap?.invalidateSize(), 800);
  } catch (e) {
    console.warn("[Control flow map]", e.message);
  }
});

onBeforeUnmount(() => {
  if (flowMap) { flowMap.remove(); flowMap = null; }
  document.removeEventListener("visibilitychange", handleVisibility);
  camVideoRefs.value.forEach((v) => v && v.pause());
  if (camTimeTimer) clearInterval(camTimeTimer);
  if (hlsInstance) { hlsInstance.destroy(); hlsInstance = null; }
  clearCctvMarkers();
});

const reportRows = [
  { key: "daily",  t: "일일 운영 보고서",       d: "2026-05-17 14:32 생성" },
  { key: "weekly", t: "주간 정체 분석 보고서", d: "2026-05-11 ~ 05-17" },
  { key: "daily",  t: "이벤트 처리 로그",       d: "최근 30일 누적" },
];

// 보고서 기준 날짜
const ctrlReportDate = ref((() => {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
})());
const setSound = ref(true);
const setRefresh = ref(15);
const setMapMode = ref("flow");
const setMsg = ref("");
function saveSet() {
  setMsg.value = "설정 저장 완료";
  setTimeout(() => { setMsg.value = ""; }, 1800);
}

</script>

<style scoped src="./ControlView.css"></style>
