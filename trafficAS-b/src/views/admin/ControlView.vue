<template>
  <div class="cc-shell">
    <aside class="side">
      <RouterLink to="/" class="brand">Traffic <em>AS</em></RouterLink>
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
          <i class="bi bi-speedometer"></i>
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
                  <span class="thumb-live" v-if="camIdx === i"><span class="dot-live"></span> LIVE</span>
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

      <section v-if="tab === 'map'" class="card pnl">
        <h3>지도 패널</h3>
        <div class="map-stub"><i class="bi bi-map"></i><div>실시간 도로망 상태 — 11개 자치구 색상 표시</div></div>
      </section>

      <section v-if="tab === 'cams'" class="card pnl">
        <h3>카메라 — {{ cams.length }}대 운영</h3>
        <div class="cam-tab-grid">
          <div v-for="(c, i) in cams" :key="c.src" class="cam-tab" :class="{ on: camIdx === i }" @click="focusVideo(i)">
            <video :ref="(el) => setCamVideoRef(el, i)" :src="c.src" muted loop playsinline preload="metadata"></video>
            <div class="ct-info"><strong>{{ c.label }}</strong><span>{{ c.title }}</span></div>
          </div>
        </div>
      </section>

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
function goHome() {
  tab.value = "center";
  window.scrollTo({ top: 0, behavior: "smooth" });
}
const nav = [
  { id: "center",  icon: "bi bi-broadcast",         label: "교통정보센터" },
  { id: "map",     icon: "bi bi-map",               label: "지도" },
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

<style scoped>
/* shell/brand/snav/top/bell/bdg/user는 admin-shared.css */
.cc-shell { height: 100vh; overflow: hidden; }
.side { width: 180px; flex-shrink: 0; }
.main {
  flex: 1; padding: 14px 18px;
  display: flex; flex-direction: column; gap: 10px;
  min-width: 0; height: 100vh; overflow: hidden;
}
.main .top { flex-shrink: 0; }
.t-moon { color: #fbbf24; font-size: 17px; cursor: pointer; }

.stat-row {
  display: grid;
  grid-template-columns: auto repeat(4, 1fr) auto;
  gap: 14px; align-items: stretch;
  background: #ffffff;
  border: 1px solid #c9d4e3;
  border-radius: 4px;
  padding: 10px 16px;
  position: relative; overflow: hidden;
  box-shadow: 0 1px 3px rgba(12, 31, 64, 0.04);
  flex-shrink: 0;
}
.stat-row::before {
  content: ""; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
  background: linear-gradient(180deg, #2563eb, #1d4ed8);
}
.api-h {
  display: flex; flex-direction: column; justify-content: center;
  padding-right: 16px; border-right: 1px solid #e3e9f2;
  min-width: 0;
}
.api-h > i { color: #2563eb; font-size: 18px; margin-bottom: 4px; }
.api-h-t { font-size: 13px; font-weight: 800; color: #0c1f40; letter-spacing: -0.01em; }
.api-h-sub {
  font-size: 10.5px; color: #6b7a92; margin-top: 1px;
  font-family: "JetBrains Mono", monospace;
}

.st {
  display: flex; align-items: center; gap: 12px;
  padding: 4px 14px 4px 0; border-right: 1px solid #e3e9f2;
  min-width: 0;
}
.st:last-of-type { border-right: 0; }
.st > i {
  width: 34px; height: 34px; flex-shrink: 0;
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: 6px;
  font-size: 16px;
}
.st-body { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.st.bad > i { background: rgba(220,38,38,0.1); color: #dc2626; }
.st.warn > i { background: rgba(180,83,9,0.1); color: #b45309; }
.st.alert > i { background: rgba(220,38,38,0.1); color: #dc2626; }
.st.ok > i { background: rgba(5,150,105,0.1); color: #059669; }
.st .lab { font-size: 11.5px; color: #4a5b78; font-weight: 600; letter-spacing: 0.02em; }
.st .val {
  font-size: 20px; font-weight: 800;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  display: inline-flex; align-items: baseline; gap: 5px;
  color: #0c1f40;
}
.st.bad .val, .st.alert .val { color: #b91c1c; }
.st.warn .val { color: #b45309; }
.st.ok .val { color: #047857; }
.st .val small { font-size: 13px; font-weight: 700; color: #6b7a92; }
.st .dlt {
  font-size: 11px; font-weight: 800;
  background: rgba(220,38,38,0.12); color: #b91c1c;
  padding: 1px 6px; border-radius: 3px;
}
.st .sub { font-size: 11px; color: #6b7a92; font-family: "JetBrains Mono", monospace; font-weight: 600; }

.ts {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11.5px; color: #6b7a92;
  font-family: "JetBrains Mono", monospace;
  padding-left: 6px;
}
.ts > i { color: #2563eb; }

.grid-mid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 10px;
  align-items: stretch;
  flex: 1; min-height: 0;
}
.right-stack {
  display: flex; flex-direction: column; gap: 10px;
  min-height: 0; min-width: 0;
}
.right-stack .bot-card.cam { flex: 1; min-height: 0; }
.right-stack .vms-card { flex: 0 0 auto; }
.map-card {
  background: #ffffff; border: 1px solid #c9d4e3; border-radius: 4px;
  padding: 10px 12px; display: flex; flex-direction: column; min-width: 0;
  box-shadow: 0 1px 3px rgba(12, 31, 64, 0.04);
  min-height: 0;
}
.map-card .mc-head { margin-bottom: 6px; }
.map-card .mc-head h2 { color: #0c1f40; font-size: 13.5px; }
.map-card .map-area { flex: 1; min-height: 0; }
.map-card .flow-leaflet { height: 100%; min-height: 0; border-radius: 3px; }

/* 🔔 헤더 종 + 알림 팝오버 */
.hdr-bell-wrap { position: relative; }
.hdr-bell {
  position: relative;
  width: 36px; height: 36px;
  background: rgba(37,99,235,0.08); border: 1px solid rgba(37,99,235,0.25);
  color: #2563eb; border-radius: 100px; cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 15px;
}
.hdr-bell:hover { background: rgba(37,99,235,0.16); }
.hdr-bell.on { background: #2563eb; color: #fff; border-color: #2563eb; }
.hdr-bell.critical {
  background: #dc2626; color: #fff; border-color: #dc2626;
  animation: bellPulse 1.4s ease-in-out infinite;
}
@keyframes bellPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(220,38,38,0.5); }
  50%      { box-shadow: 0 0 0 6px rgba(220,38,38,0); }
}
.hdr-bell-c {
  position: absolute; top: -3px; right: -3px;
  background: #fff; color: #dc2626;
  border: 2px solid #dc2626;
  font-size: 9.5px; font-weight: 800;
  font-family: "JetBrains Mono", monospace;
  min-width: 18px; height: 18px; padding: 0 4px;
  border-radius: 100px;
  display: inline-flex; align-items: center; justify-content: center;
}
.hdr-bell.on .hdr-bell-c { background: #fff; color: #2563eb; border-color: #fff; }
.hdr-bell.critical .hdr-bell-c { background: #fff; color: #dc2626; border-color: #fff; }

.hdr-bell-pop {
  position: absolute; top: calc(100% + 8px); right: 0; z-index: 80;
  width: 360px;
  background: #ffffff; border: 1px solid #c9d4e3;
  border-radius: 6px;
  box-shadow: 0 10px 30px rgba(12,31,64,0.18);
  overflow: hidden;
}
.hbp-h {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 14px; border-bottom: 1px solid #e3e9f2;
}
.hbp-h > i { color: #dc2626; font-size: 15px; }
.hbp-h strong { font-size: 13.5px; color: #0c1f40; flex: 1; }
.hbp-c {
  background: #dc2626; color: #fff;
  padding: 1px 9px; border-radius: 100px;
  font-size: 11px; font-weight: 800;
  font-family: "JetBrains Mono", monospace;
}
.hbp-x {
  background: none; border: 0; color: #4a5b78;
  cursor: pointer; padding: 4px;
  display: inline-flex; align-items: center; justify-content: center;
}
.hbp-x:hover { color: #0c1f40; }
.hbp-list {
  display: flex; flex-direction: column; gap: 6px;
  padding: 10px; max-height: 420px; overflow-y: auto;
}

.ac-row {
  display: flex; gap: 10px;
  background: #f8fafd; border: 1px solid #c9d4e3; border-left: 3px solid #94a3b8;
  border-radius: 3px; padding: 9px 11px; cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.ac-row:hover { background: #eef2f7; }
.ac-row.critical { border-left-color: #dc2626; background: rgba(220,38,38,0.05); animation: alertPulse 1.6s ease-in-out infinite; }
.ac-row.serious  { border-left-color: #c2410c; }
.ac-row.caution  { border-left-color: #b45309; }
.ac-row.info     { border-left-color: #2563eb; }
@keyframes alertPulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(220,38,38,0.35); } 50% { box-shadow: 0 0 0 4px rgba(220,38,38,0); } }
.ac-sev {
  width: 28px; height: 28px; flex-shrink: 0;
  background: rgba(0,0,0,0.04); border-radius: 4px;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 14px;
}
.ac-row.critical .ac-sev { color: #dc2626; background: rgba(220,38,38,0.1); }
.ac-row.serious  .ac-sev { color: #c2410c; background: rgba(194,65,12,0.1); }
.ac-row.caution  .ac-sev { color: #b45309; background: rgba(180,83,9,0.1); }
.ac-row.info     .ac-sev { color: #2563eb; background: rgba(37,99,235,0.1); }
.ac-body { flex: 1; min-width: 0; }
.ac-t { font-size: 12.5px; font-weight: 800; color: #0c1f40; margin-bottom: 1px; }
.ac-d { font-size: 11.5px; color: #4a5b78; line-height: 1.35; margin-bottom: 3px; }
.ac-meta { display: flex; justify-content: space-between; font-size: 10.5px; color: #6b7a92; font-family: "JetBrains Mono", monospace; }
.ac-meta i { color: #2563eb; margin-right: 2px; }
.ac-empty { padding: 20px; text-align: center; color: #6b7a92; font-size: 12px; }

/* 📢 VMS 전광판 제어 (라이트) */
.vms-card {
  background: #ffffff; border: 1px solid #c9d4e3; border-radius: 4px;
  padding: 6px 12px;
  flex: 0 0 auto; min-height: 0;
  display: flex; flex-direction: column;
}
.vms-card .vms-body { flex: 0 0 auto; min-height: 0; }
.vms-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 6px;
}
.vms-head h3 { font-size: 13px !important; }
.vms-head h3 {
  font-size: 14px; font-weight: 700; margin: 0; color: #0c1f40;
  display: inline-flex; align-items: center; gap: 6px;
}
.vms-head h3 i { color: #b45309; }
.vms-sub { font-size: 11.5px; color: #4a5b78; font-family: "JetBrains Mono", monospace; }
.vms-body { display: grid; grid-template-columns: 1fr 1.2fr; gap: 10px; align-items: stretch; }
.vms-left { display: flex; flex-direction: column; gap: 5px; }
.vms-lab { font-size: 11px; color: #4a5b78; font-weight: 700; margin-top: 1px; }
.vms-sel, .vms-input {
  background: #f1f5fb; border: 1px solid #c9d4e3; color: #0c1f40;
  padding: 5px 9px; border-radius: 3px; font-size: 12px;
  font-family: inherit;
}
.vms-input:focus, .vms-sel:focus { outline: none; border-color: #2563eb; background: #fff; }
.vms-tmpl { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-top: 2px; }
.vms-tmpl-b {
  background: #f1f5fb; border: 1px solid #c9d4e3;
  color: #2563eb; padding: 4px 7px; border-radius: 3px;
  font-size: 11px; font-weight: 700; cursor: pointer;
}
.vms-tmpl-b:hover { background: #2563eb; color: #fff; border-color: #2563eb; }
.vms-send {
  margin-top: 4px;
  background: #dc2626; border: 0; color: #fff;
  padding: 6px 12px; border-radius: 4px;
  font-size: 12px; font-weight: 700; cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center; gap: 5px;
}
.vms-send:hover:not(:disabled) { background: #b91c1c; }
.vms-send:disabled { opacity: 0.45; cursor: not-allowed; }

.vms-right { display: flex; flex-direction: column; gap: 5px; height: 100%; }
/* LED 디스플레이 — 검은 배경 유지, 좌측 컨트롤 높이에 맞춰 세로 확장 */
.vms-screen {
  background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
  border: 2px solid #2a2a2a;
  border-radius: 5px; padding: 10px 14px;
  box-shadow: inset 0 0 14px rgba(251,191,36,0.08);
  flex: 1; display: flex; flex-direction: column; justify-content: space-between;
  min-height: 0;
}
.vms-screen-led {
  font-family: "JetBrains Mono", "IBM Plex Mono", monospace;
  color: #fbbf24; font-size: 16px; font-weight: 800;
  letter-spacing: 0.02em; line-height: 1.4;
  text-shadow: 0 0 8px rgba(251,191,36,0.5);
  word-break: keep-all;
  flex: 1; display: flex; align-items: center; justify-content: center;
  text-align: center;
}
.vms-screen-meta {
  display: flex; justify-content: space-between;
  font-size: 10px; color: #fbbf24; opacity: 0.85; margin-top: 5px;
  padding-top: 5px; border-top: 1px dashed rgba(251,191,36,0.25);
}
.vms-screen-meta i { color: #fbbf24; margin-right: 3px; }
.vms-on { display: inline-flex; align-items: center; gap: 4px; color: #34d399; font-weight: 700; }
.vms-on .dot-live { width: 5px; height: 5px; border-radius: 50%; background: #34d399; }

.vms-log-h { font-size: 11.5px; font-weight: 700; color: #4a5b78; margin-top: 2px; }
.vms-log { display: flex; flex-direction: column; gap: 3px; }
.vms-log-i {
  display: grid; grid-template-columns: 40px 60px 1fr; gap: 8px;
  background: #f1f5fb; border: 1px solid #c9d4e3; border-radius: 3px;
  padding: 3px 8px; font-size: 10.5px;
  align-items: center;
}
.vms-log-t { font-family: "JetBrains Mono", monospace; color: #6b7a92; }
.vms-log-id { font-weight: 800; color: #b45309; font-family: "JetBrains Mono", monospace; }
.vms-log-m { color: #0c1f40; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.vms-log-empty { font-size: 11px; color: #6b7a92; padding: 6px; text-align: center; }
.mc-head, .qc-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.mc-head h2, .qc-head h2 { font-size: 14px; font-weight: 700; margin: 0; }
.mc-right { display: inline-flex; align-items: center; gap: 10px; }
.mc-weather-wrap { position: relative; }
.mc-weather-chip {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(96,165,250,0.1); border: 1px solid rgba(96,165,250,0.35);
  color: #e4eeff; padding: 5px 11px; border-radius: 100px;
  font-size: 12.5px; font-weight: 700; cursor: pointer;
}
.mc-weather-chip:hover { background: rgba(96,165,250,0.18); }
.mc-weather-chip.on { background: #2563eb; border-color: #2563eb; color: #fff; }
.mc-weather-chip > i:first-child { font-size: 14px; }
.mc-weather-chip.on > i:first-child { color: #fff !important; }
.mc-weather-chip .mwc-temp { font-family: "JetBrains Mono", monospace; font-weight: 800; }
.mc-weather-chip .mwc-cond { opacity: 0.85; font-size: 12px; }
.mc-weather-chip > i:last-child { font-size: 11px; opacity: 0.7; }
.mc-weather-pop {
  position: absolute; top: calc(100% + 6px); right: 0; z-index: 1000;
  width: 320px;
  background: #ffffff; border: 1px solid #c9d4e3;
  border-radius: 6px; padding: 12px;
  box-shadow: 0 10px 30px rgba(12,31,64,0.18);
}
.mc-toggle { display: flex; gap: 4px; background: #0a1424; border: 1px solid #1f3055; border-radius: 6px; padding: 2px; }
.mt { padding: 5px 14px; font-size: 12px; background: none; border: 0; color: rgba(228,238,255,.55); border-radius: 4px; cursor: pointer; }
.mt.on { background: rgba(96,165,250,.18); color: #60a5fa; }

.map-area { position: relative; background: #06101e; border-radius: 8px; overflow: hidden; height: 400px; }
.flow-leaflet { width: 100%; height: 100%; background: #06101e; }
.flow-leaflet :deep(.leaflet-container) { background: #06101e; }
.flow-leaflet :deep(.leaflet-control-zoom a) { background: none !important; color: #0c1f40; border-color: #c9d4e3; }
.flow-leaflet :deep(.leaflet-control-zoom a:hover) { background: none !important; color: #2563eb; }
.flow-leaflet :deep(.ic-tip), .flow-leaflet :deep(.osm-road-tip) { background: rgba(8,16,32,.92); border: 1px solid #1f3055; color: #e4eeff; font-size: 11px; padding: 4px 8px; line-height: 1.55; }
.map-legend { position: absolute; bottom: 14px; left: 14px; display: flex; gap: 14px; background: rgba(8,16,32,.85); padding: 6px 12px; border-radius: 6px; font-size: 11px; }
.map-legend i.dot { display: inline-block; width: 16px; height: 4px; border-radius: 2px; margin-right: 4px; vertical-align: middle; }
.map-legend i.gr { background: #34d399; }
.map-legend i.yl { background: #f59e0b; }
.map-legend i.or { background: #fb923c; }
.map-legend i.rd { background: #ef4444; }
.map-legend i.bl { background: #2563eb; }

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

.log-tbl { width: 100%; border-collapse: collapse; font-size: 12.5px; color: #0c1f40; }
.log-tbl th, .log-tbl td { padding: 9px 10px; text-align: left; border-bottom: 1px solid #e3e9f2; }
.log-tbl th { font-weight: 700; color: #4a5b78; font-size: 11.5px; background: #f8fafd; }
.log-tbl tbody tr:hover { background: #f1f5fb; }
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

.grid-bot-2 { display: grid; grid-template-columns: 1fr; gap: 12px; }
.bot-card {
  background: #ffffff; border: 1px solid #c9d4e3; border-radius: 4px;
  padding: 10px 12px; min-width: 0;
  box-shadow: 0 1px 3px rgba(12, 31, 64, 0.04);
  min-height: 0;
  display: flex; flex-direction: column;
}
.bot-card .bc-head { flex-shrink: 0; margin-bottom: 6px; }
.bot-card.cam { overflow: hidden; }
.bot-card h3 { color: #0c1f40; }
.bot-card .bc-sub { color: #4a5b78; font-size: 12px; font-weight: 600; }
.bc-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.bc-head h3 { font-size: 13px; font-weight: 700; margin: 0; }
.bc-sub { font-size: 11px; opacity: .55; font-weight: 400; margin-left: 4px; }
.live { font-size: 11px; color: #34d399; display: inline-flex; align-items: center; gap: 4px; font-weight: 700; }

.cam-main {
  position: relative;
  flex: 1; min-height: 0; width: 100%;
  background: #000; border-radius: 4px; overflow: hidden; margin-bottom: 6px;
}
.cam-main video { width: 100%; height: 100%; object-fit: cover; border-bottom: 0; display: block; }
.cam-ts {
  position: absolute; top: 6px; left: 8px;
  font-size: 11px; font-weight: 700; color: #ffffff;
  background: rgba(0,0,0,.72); padding: 2px 7px; border-radius: 3px;
  font-family: "JetBrains Mono", monospace; letter-spacing: 0.02em; z-index: 2;
}
.cam-loc {
  position: absolute; bottom: 6px; left: 8px;
  font-size: 11px; font-weight: 700; color: #ffffff;
  background: rgba(0,0,0,.72); padding: 2px 7px; border-radius: 3px; z-index: 2;
}
.cam-controls {
  position: absolute; bottom: 6px; right: 6px;
  display: inline-flex; gap: 4px; z-index: 3;
  padding: 3px;
  background: rgba(0, 0, 0, 0.78);
  border: 1px solid rgba(255,255,255,0.45);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
.cam-ctl, .cam-zoom {
  width: 22px; height: 22px;
  background: #2563eb;
  border: 1px solid rgba(255,255,255,0.5);
  color: #ffffff;
  border-radius: 3px; cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 11px;
  transition: background 0.15s, transform 0.1s;
  position: static;
}
.cam-ctl i, .cam-zoom i {
  color: #ffffff !important;
  font-size: 11px;
  line-height: 1;
}
.cam-ctl:hover, .cam-zoom:hover {
  background: #1d4ed8;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.5);
}
.cam-ctl:active, .cam-zoom:active { transform: scale(0.92); }
.cam-ctl.cam-send {
  width: auto; padding: 0 8px;
  background: #dc2626; border-color: rgba(255,255,255,0.6);
}
.cam-ctl.cam-send:hover { background: #b91c1c; }
.cam-ctl.cam-send:disabled { background: #047857; cursor: default; }
/* CCTV pin */
:global(.cctv-pin) {
  background: #2563eb; color: #fff;
  border: 2px solid #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; box-shadow: 0 2px 6px rgba(0,0,0,0.4);
  cursor: pointer;
}
:global(.cctv-pin i) { font-size: 11px; }
:global(.cctv-tip) {
  background: rgba(12,31,64,0.95) !important;
  color: #fff !important;
  border: 0 !important;
  font-size: 12px !important;
  padding: 4px 8px !important;
  font-weight: 700;
}

/* CCTV 모달 */
.cctv-modal-bg {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.65);
  z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.cctv-modal {
  background: #0f1d34;
  border: 1px solid #1f3055;
  border-radius: 8px;
  width: min(720px, 100%);
  display: flex; flex-direction: column;
  box-shadow: 0 12px 40px rgba(0,0,0,0.6);
}
.cm-h {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #1f3055;
}
.cm-t { display: inline-flex; align-items: center; gap: 8px; }
.cm-t i { color: #60a5fa; font-size: 16px; }
.cm-t strong { font-size: 14.5px; color: #e4eeff; }
.cm-live {
  display: inline-flex; align-items: center; gap: 4px;
  background: #dc2626; color: #fff;
  font-size: 10.5px; font-weight: 800; letter-spacing: 0.04em;
  padding: 2px 7px; border-radius: 100px; margin-left: 6px;
}
.cm-live .dot-live {
  width: 5px; height: 5px; border-radius: 50%; background: #fff;
  animation: nsPulse 1.2s ease-in-out infinite;
}
.cm-x {
  background: none; border: 0; color: rgba(228,238,255,0.7);
  cursor: pointer; font-size: 16px;
  width: 30px; height: 30px;
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: 4px;
}
.cm-x:hover { background: rgba(255,255,255,0.06); color: #fff; }
.cm-body { position: relative; background: #000; }
.cm-body video { width: 100%; aspect-ratio: 16/9; display: block; background: #000; }
.cm-err {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  color: #f87171; font-weight: 700; font-size: 13px;
  background: rgba(0,0,0,0.55);
}
.cm-foot {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 16px; border-top: 1px solid #1f3055;
  font-size: 12px;
}
.cm-foot span { color: rgba(228,238,255,0.7); display: inline-flex; align-items: center; gap: 5px; }
.cm-foot span i { color: #60a5fa; }
.cm-link {
  color: #60a5fa; text-decoration: none; font-weight: 700;
  display: inline-flex; align-items: center; gap: 4px;
}
.cm-link:hover { color: #93c5fd; text-decoration: underline; }
@keyframes nsPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.send-toast {
  position: absolute; top: 10px; left: 50%; transform: translateX(-50%);
  background: rgba(5,150,105,0.95); color: #fff;
  padding: 8px 16px; border-radius: 5px;
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 700;
  box-shadow: 0 4px 14px rgba(0,0,0,0.4);
  z-index: 4;
  animation: toastSlide 0.25s ease-out;
}
.send-toast i { font-size: 16px; }
@keyframes toastSlide {
  from { opacity: 0; transform: translate(-50%, -8px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}
.cam-thumbs {
  display: flex; align-items: center; gap: 5px;
  flex-shrink: 0; height: 36px;
}
.thumb-nav {
  width: 22px; height: 100%;
  background: #f1f5fb; border: 1px solid #c9d4e3; color: #4a5b78;
  border-radius: 3px; cursor: pointer; flex-shrink: 0;
}
.thumb-nav:hover { background: #2563eb; color: #fff; border-color: #2563eb; }
.thumb {
  flex: 1; height: 100%;
  border-radius: 3px; overflow: hidden; border: 2px solid transparent;
  cursor: pointer; position: relative;
}
.thumb.active { border-color: #2563eb; }
.thumb video { width: 100%; height: 100%; object-fit: cover; display: block; }
.thumb-ph {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #1a2a45 0%, #0f1d34 100%);
  position: relative;
}
.thumb-ph > i { font-size: 14px; color: #60a5fa; opacity: 0.85; }
.thumb.active .thumb-ph { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); }
.thumb.active .thumb-ph > i { color: #fff; opacity: 1; }
.thumb-live {
  position: absolute; top: 3px; right: 3px;
  display: inline-flex; align-items: center; gap: 3px;
  background: rgba(220,38,38,0.95); color: #fff;
  font-size: 0; padding: 0;
  width: 8px; height: 8px;
  border-radius: 50%;
}
.thumb-live span:not(.dot-live) { display: none; }
.thumb-live .dot-live {
  width: 6px; height: 6px; border-radius: 50%; background: #fff;
  animation: nsPulse 1.2s ease-in-out infinite;
}
.thumb-lab {
  position: absolute; bottom: 0; left: 0; right: 0;
  font-size: 9.5px; font-weight: 700;
  color: #fff; text-align: center; padding: 1px 2px;
  background: rgba(0,0,0,0.55);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

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
.rep-date-row { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; font-size: 12.5px; color: #4a5b78; }
.rep-date {
  background: #ffffff; border: 1px solid #c9d4e3;
  color: #0c1f40; padding: 5px 8px; border-radius: 3px;
  font-family: "JetBrains Mono", monospace; font-size: 12.5px;
  margin-left: 6px;
}
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
}
</style>
