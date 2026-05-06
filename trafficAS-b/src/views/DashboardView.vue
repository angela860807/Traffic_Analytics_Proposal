<template>
  <div class="theme-navy" :class="{ light: !isDark }">
    <AppNav />
    <AppFab />

    <div class="dash-shell">
      <!-- ══ TAB BAR ══ -->
      <nav class="tabbar">
        <div class="tab-inner">
          <button
            v-for="tab in TABS"
            :key="tab.id"
            class="tab-btn"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <component :is="tab.icon" class="tab-icon" />
            {{ tab.label }}
            <span v-if="tab.id === 'alerts' && alerts.length" class="tab-badge">{{
              alerts.length
            }}</span>
            <span v-else-if="tab.badge" class="tab-badge">{{ tab.badge }}</span>
          </button>
        </div>
        <div class="tab-right">
          <span class="tab-ws mono" :class="wsConnected ? 'ok' : 'err'">
            ● {{ wsConnected ? "WS 연결됨" : "WS 대기 중" }}
          </span>
          <span class="tab-clock mono">{{ timeStr }}</span>
          <span class="tab-live"><span class="live-dot"></span>LIVE</span>
        </div>
      </nav>

      <div class="dash-body">
        <!-- ─── 탭 1: 도로 현황 ─── -->
        <div v-show="activeTab === 'overview'" class="tab-content">
          <div class="kpi-bar">
            <div class="kpi" v-for="k in kpis" :key="k.label">
              <div class="kpi-v" :style="{ color: k.color }">
                <span class="mono">{{ k.value }}</span>
                <span class="kpi-unit">{{ k.unit }}</span>
              </div>
              <div class="kpi-l">{{ k.label }}</div>
            </div>
          </div>

          <div class="road-grid">
            <div
              v-for="seg in segments"
              :key="seg.id"
              class="rcard"
              :class="seg.lv"
              @click="openFullscreen(seg)"
            >
              <div class="rc-top">
                <div class="rc-lv-bar" :style="{ background: levelColor(seg.lv) }"></div>
                <div class="rc-info">
                  <div class="rc-name">{{ seg.name }}</div>
                  <div class="rc-cam mono">{{ seg.cam }}</div>
                </div>
                <div class="rc-badge" :class="'lv-' + seg.lv">
                  {{ seg.lv === "H" ? "혼잡" : seg.lv === "M" ? "지체" : "원활" }}
                </div>
              </div>
              <div class="rc-media-wrap">
                <!-- CCTV 로딩 -->
                <div v-if="seg.cctvLoading" class="rc-loading">
                  <div class="loading-ring"></div>
                  <span
                    class="mono"
                    style="font-size: 9px; color: var(--a); letter-spacing: 2px"
                    >CCTV 연결 중...</span
                  >
                </div>
                <!-- 실제 CCTV 스트림 (ITS API) -->
                <video
                  v-else-if="seg.cctvUrl"
                  :ref="
                    (el) => {
                      if (el) {
                        videoRefs[seg.id] = el;
                        el.play().catch(() => {});
                      }
                    }
                  "
                  class="rc-video"
                  autoplay
                  muted
                  loop
                  playsinline
                  @error="seg.cctvUrl = null"
                ></video>
                <!-- MP4 영상 폴백 -->
                <video
                  v-else-if="seg.videoUrl"
                  :ref="
                    (el) => {
                      if (el) {
                        videoRefs[seg.id] = el;
                        el.play().catch(() => {});
                      }
                    }
                  "
                  class="rc-video"
                  :src="seg.videoUrl"
                  autoplay
                  muted
                  loop
                  playsinline
                ></video>
                <canvas
                  v-else
                  :ref="
                    (el) => {
                      if (el) canvasRefs[seg.id] = el;
                    }
                  "
                  class="rc-canvas"
                ></canvas>

                <div class="rc-speed-overlay">
                  <span class="mono rc-spd-num" :style="{ color: levelColor(seg.lv) }">{{
                    Math.round(seg.spd)
                  }}</span>
                  <span class="rc-spd-unit">km/h</span>
                </div>
                <div class="rc-fullscreen-hint mono">클릭하여 확대</div>
              </div>
              <div class="rc-bottom">
                <div class="rc-stat">
                  <div class="mono rc-sv">{{ seg.cnt }}</div>
                  <div class="rc-sl">감지 차량</div>
                </div>
                <div class="rc-divider"></div>
                <div class="rc-stat">
                  <div class="mono rc-sv">{{ seg.conf }}%</div>
                  <div class="rc-sl">인식률</div>
                </div>
                <div class="rc-divider"></div>
                <div class="rc-stat">
                  <div class="rc-sv" style="display: flex; align-items: center; gap: 4px">
                    <span
                      class="rc-status-dot"
                      :style="{ background: levelColor(seg.lv) }"
                    ></span>
                    <span class="mono" style="font-size: 10px">{{
                      seg.lv === "H"
                        ? "정체 주의"
                        : seg.lv === "M"
                        ? "서행 중"
                        : "소통 원활"
                    }}</span>
                  </div>
                  <div class="rc-sl">소통 상태</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ─── 탭 2: 카메라 ─── -->
        <div v-show="activeTab === 'cameras'" class="tab-content">
          <div class="section-head">
            <div class="sh-title">카메라 현황</div>
            <div class="sh-sub">실시간 카메라 상태 및 감지 정보</div>
          </div>
          <div class="cam-grid">
            <div class="cam-card" v-for="cam in cameras" :key="cam.id">
              <div class="cam-card-top">
                <div class="cam-id-badge mono">{{ cam.id }}</div>
                <div class="cam-status" :class="cam.ok ? 'ok' : 'err'">
                  <span class="cam-dot" :class="{ blink: !cam.ok }"></span>
                  {{ cam.ok ? "정상" : "장애" }}
                </div>
              </div>
              <div class="cam-loc-name">{{ cam.loc }}</div>
              <div class="cam-stats">
                <div class="cam-stat">
                  <div class="mono cam-stat-v">{{ cam.cnt }}</div>
                  <div class="cam-stat-l">감지 차량</div>
                </div>
                <div class="cam-stat">
                  <div class="mono cam-stat-v">97%</div>
                  <div class="cam-stat-l">인식률</div>
                </div>
                <div class="cam-stat">
                  <div class="mono cam-stat-v">{{ cam.ok ? "0ms" : "ERR" }}</div>
                  <div class="cam-stat-l">지연시간</div>
                </div>
              </div>
              <div class="cam-bar-wrap">
                <div
                  class="cam-bar-fill"
                  :style="{
                    width: Math.min(cam.cnt / 4, 100) + '%',
                    background:
                      cam.cnt > 250
                        ? 'var(--danger)'
                        : cam.cnt > 150
                        ? 'var(--warn)'
                        : 'var(--ok)',
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- ─── 탭 3: 번호판 인식 ─── -->
        <div v-show="activeTab === 'plates'" class="tab-content">
          <div class="section-head">
            <div class="sh-title">번호판 인식 현황</div>
            <div class="sh-sub">YOLO + EasyOCR 실시간 번호판 인식 로그</div>
          </div>
          <!-- 검색 -->
          <div class="plate-search">
            <input
              v-model="plateSearch"
              class="search-input mono"
              placeholder="번호판 검색 (예: 서울 12가)"
            />
            <div class="search-result-cnt mono">{{ filteredPlates.length }}건</div>
          </div>
          <div class="plate-wrap">
            <div class="plate-stats">
              <div class="pstat">
                <div class="mono pstat-v in-color">{{ flowIn.toLocaleString() }}</div>
                <div class="pstat-l">입차(대/시)</div>
              </div>
              <div class="pstat">
                <div class="mono pstat-v out-color">{{ flowOut.toLocaleString() }}</div>
                <div class="pstat-l">출차(대/시)</div>
              </div>
              <div class="pstat">
                <div class="mono pstat-v">{{ (flowIn + flowOut).toLocaleString() }}</div>
                <div class="pstat-l">총 통행량</div>
              </div>
              <div class="pstat">
                <div class="mono pstat-v" style="color: var(--a)">96.2%</div>
                <div class="pstat-l">평균 인식률</div>
              </div>
            </div>
            <div class="plate-table">
              <div class="pt-head">
                <div>번호판</div>
                <div>방향</div>
                <div>카메라</div>
                <div>시각</div>
                <div>신뢰도</div>
              </div>
              <transition-group name="plate-slide" tag="div">
                <div class="pt-row" v-for="p in filteredPlates" :key="p.id">
                  <div class="mono pt-num">{{ p.num }}</div>
                  <div>
                    <span class="dir-badge" :class="p.dir">{{ p.dir }}</span>
                  </div>
                  <div class="mono" style="font-size: 9px; color: var(--mu)">
                    {{ p.cam }}
                  </div>
                  <div class="mono" style="font-size: 9px; color: var(--mu)">
                    {{ p.time }}
                  </div>
                  <div class="mono" style="font-size: 9px; color: var(--a)">
                    {{ p.conf }}%
                  </div>
                </div>
              </transition-group>
            </div>
          </div>
        </div>

        <!-- ─── 탭 4: 이벤트 ─── -->
        <div v-show="activeTab === 'events'" class="tab-content">
          <div class="section-head">
            <div class="sh-title">실시간 이벤트 로그</div>
            <div class="sh-sub">교통 이상 감지 및 돌발상황 기록</div>
          </div>
          <div class="ev-list-full">
            <div
              class="ev-item"
              v-for="inc in incidents"
              :key="inc.id"
              :class="'ev-' + inc.lv"
            >
              <div class="ev-lv-stripe" :style="{ background: levelColor(inc.lv) }"></div>
              <div class="ev-time mono">{{ inc.time }}</div>
              <div class="ev-badge" :class="'lv-' + inc.lv">{{ inc.type }}</div>
              <div class="ev-loc">{{ inc.loc }}</div>
              <div class="ev-status mono">처리 중</div>
            </div>
          </div>
        </div>

        <!-- ─── 탭 5: 통계 차트 ─── -->
        <div v-show="activeTab === 'stats'" class="tab-content">
          <div class="section-head">
            <div class="sh-title">통계 분석</div>
            <div class="sh-sub">시간대별 통행량 및 구역별 혼잡도 히트맵</div>
          </div>
          <div class="stats-grid">
            <!-- 시간대별 통행량 차트 -->
            <div class="stat-card wide">
              <div class="stat-card-title mono">시간대별 통행량</div>
              <canvas ref="chartRef" class="stat-canvas"></canvas>
            </div>
            <!-- 구역별 히트맵 -->
            <div class="stat-card">
              <div class="stat-card-title mono">구역별 혼잡도 히트맵</div>
              <div class="heatmap">
                <div
                  v-for="zone in heatZones"
                  :key="zone.name"
                  class="hm-cell"
                  :style="{ background: hmColor(zone.pct) }"
                >
                  <div class="hm-name">{{ zone.name }}</div>
                  <div class="mono hm-pct">{{ zone.pct }}%</div>
                </div>
              </div>
            </div>
            <!-- 실시간 통행량 -->
            <div class="stat-card">
              <div class="stat-card-title mono">실시간 집계</div>
              <div class="rt-stats">
                <div class="rt-stat" v-for="s in rtStats" :key="s.label">
                  <div class="mono rt-v" :style="{ color: s.color }">{{ s.value }}</div>
                  <div class="rt-l">{{ s.label }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ─── 탭 6: 알림 ─── -->
        <div v-show="activeTab === 'alerts'" class="tab-content">
          <div class="section-head">
            <div class="sh-title">알림 관리</div>
            <div class="sh-sub">혼잡도 임계값 초과 및 시스템 알림</div>
          </div>
          <div class="alert-setting">
            <div class="alert-setting-title mono">알림 임계값 설정</div>
            <div class="alert-thresholds">
              <div class="threshold-item">
                <span class="th-label">혼잡 임계속도</span>
                <input
                  v-model.number="thresholds.congSpeed"
                  type="range"
                  min="5"
                  max="40"
                  class="th-slider"
                />
                <span class="mono th-val">{{ thresholds.congSpeed }} km/h 이하</span>
              </div>
              <div class="threshold-item">
                <span class="th-label">지체 임계속도</span>
                <input
                  v-model.number="thresholds.slowSpeed"
                  type="range"
                  min="20"
                  max="70"
                  class="th-slider"
                />
                <span class="mono th-val">{{ thresholds.slowSpeed }} km/h 이하</span>
              </div>
            </div>
          </div>
          <div class="alert-list">
            <div v-if="alerts.length === 0" class="no-alerts mono">
              현재 활성 알림 없음
            </div>
            <div
              v-for="a in alerts"
              :key="a.id"
              class="alert-item"
              :class="'alert-' + a.lv"
            >
              <div class="alert-stripe" :style="{ background: levelColor(a.lv) }"></div>
              <div class="alert-icon">{{ a.lv === "H" ? "⚠" : "ℹ" }}</div>
              <div class="alert-body">
                <div class="alert-title">{{ a.title }}</div>
                <div class="alert-desc">{{ a.desc }}</div>
              </div>
              <div class="alert-time mono">{{ a.time }}</div>
              <button class="alert-dismiss" @click="dismissAlert(a.id)">✕</button>
            </div>
          </div>
        </div>
      </div>
      <!-- /dash-body -->

      <!-- ══ TICKER ══ -->
      <div class="ticker-bar">
        <span class="mono ticker-label">LIVE</span>
        <div class="ticker-wrap">
          <div class="ticker-track">
            <span class="ticker-item" v-for="(t, i) in tickerDouble" :key="i">
              <span class="ticker-dot" :style="{ background: levelColor(t.lv) }"></span>
              {{ t.text }}
            </span>
          </div>
        </div>
      </div>
    </div>
    <!-- /dash-shell -->

    <!-- ══ 풀스크린 모달 ══ -->
    <Teleport to="body">
      <div v-if="fullscreenSeg" class="fs-overlay" @click.self="closeFullscreen">
        <div class="fs-modal">
          <div class="fs-header">
            <div class="fs-title">{{ fullscreenSeg.name }}</div>
            <div class="fs-badge" :class="'lv-' + fullscreenSeg.lv">
              {{
                fullscreenSeg.lv === "H"
                  ? "혼잡"
                  : fullscreenSeg.lv === "M"
                  ? "지체"
                  : "원활"
              }}
            </div>
            <div class="mono fs-spd" :style="{ color: levelColor(fullscreenSeg.lv) }">
              {{ Math.round(fullscreenSeg.spd) }} km/h
            </div>
            <button class="fs-close" @click="closeFullscreen">✕</button>
          </div>
          <div class="fs-body">
            <video
              v-if="fullscreenSeg.videoUrl"
              class="fs-video"
              :src="fullscreenSeg.videoUrl"
              autoplay
              muted
              loop
              playsinline
            ></video>
            <canvas v-else class="fs-canvas"></canvas>
            <canvas ref="fsYoloRef" class="fs-yolo"></canvas>
            <div class="fs-speed-overlay">
              <span
                class="mono"
                style="font-size: 32px; font-weight: 700"
                :style="{ color: levelColor(fullscreenSeg.lv) }"
              >
                {{ Math.round(fullscreenSeg.spd) }}
              </span>
              <span style="font-size: 13px; color: var(--mu)">km/h</span>
            </div>
          </div>
          <div class="fs-footer">
            <div class="fs-stat" v-for="s in fsStats" :key="s.label">
              <div class="mono fs-sv" :style="{ color: s.color || 'var(--tx)' }">
                {{ s.value }}
              </div>
              <div class="fs-sl">{{ s.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ══ 알림 팝업 ══ -->
    <Teleport to="body">
      <div class="notif-container">
        <transition-group name="notif">
          <div v-for="n in notifQueue" :key="n.id" class="notif" :class="'notif-' + n.lv">
            <div class="notif-bar" :style="{ background: levelColor(n.lv) }"></div>
            <div class="notif-body">
              <div class="notif-title mono">{{ n.title }}</div>
              <div class="notif-desc">{{ n.desc }}</div>
            </div>
            <button class="notif-close" @click="dismissNotif(n.id)">✕</button>
          </div>
        </transition-group>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, h, watch, nextTick } from "vue";
import AppNav from "@/components/AppNav.vue";
import AppFab from "@/components/AppFab.vue";
import { useTheme } from "@/composables/useTheme";

const { isDark } = useTheme();

/* ── 탭 아이콘 ── */
const mk = (d) => ({
  render: () =>
    h(
      "svg",
      {
        viewBox: "0 0 24 24",
        fill: "none",
        stroke: "currentColor",
        "stroke-width": "1.8",
      },
      d
    ),
});
const GridIcon = mk([
  h("rect", { x: "3", y: "3", width: "7", height: "7" }),
  h("rect", { x: "14", y: "3", width: "7", height: "7" }),
  h("rect", { x: "14", y: "14", width: "7", height: "7" }),
  h("rect", { x: "3", y: "14", width: "7", height: "7" }),
]);
const CamIcon = mk([
  h("path", { d: "M23 7l-7 5 7 5V7z" }),
  h("rect", { x: "1", y: "5", width: "15", height: "14", rx: "2" }),
]);
const PlateIcon = mk([
  h("rect", { x: "2", y: "6", width: "20", height: "12", rx: "2" }),
  h("line", { x1: "6", y1: "10", x2: "6", y2: "14" }),
  h("line", { x1: "10", y1: "10", x2: "10", y2: "14" }),
  h("line", { x1: "14", y1: "10", x2: "14", y2: "14" }),
  h("line", { x1: "18", y1: "10", x2: "18", y2: "14" }),
]);
const AlertIcon = mk([
  h("path", {
    d:
      "M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z",
  }),
  h("line", { x1: "12", y1: "9", x2: "12", y2: "13" }),
  h("line", { x1: "12", y1: "17", x2: "12.01", y2: "17" }),
]);
const ChartIcon = mk([
  h("line", { x1: "18", y1: "20", x2: "18", y2: "10" }),
  h("line", { x1: "12", y1: "20", x2: "12", y2: "4" }),
  h("line", { x1: "6", y1: "20", x2: "6", y2: "14" }),
]);
const BellIcon = mk([
  h("path", { d: "M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" }),
  h("path", { d: "M13.73 21a2 2 0 01-3.46 0" }),
]);

const TABS = [
  { id: "overview", label: "도로 현황", icon: GridIcon },
  { id: "cameras", label: "카메라 현황", icon: CamIcon },
  { id: "plates", label: "번호판 인식", icon: PlateIcon },
  { id: "events", label: "이벤트 로그", icon: AlertIcon },
  { id: "stats", label: "통계 분석", icon: ChartIcon },
  { id: "alerts", label: "알림", icon: BellIcon },
];
const activeTab = ref("overview");

/* ════════════════════════════════════════
   ★★★ ITS CCTV API 키를 여기에 넣으세요 ★★★
   발급: data.go.kr → 마이페이지 → 인증키 발급현황
   ════════════════════════════════════════ */
const ITS_KEY = "76c70eaf15d84a42af8c569681f5ae12";

/* ITS CCTV 목록 조회 — FastAPI 프록시 경유 (CORS 우회) */
const FASTAPI_URL = "http://localhost:8000";
async function fetchCctvList() {
  const url = `${FASTAPI_URL}/cctv?key=${ITS_KEY}&minX=126.7&maxX=127.4&minY=37.3&maxY=37.7`;
  const res = await fetch(url);
  const data = await res.json();
  const list = data?.response?.data || data?.cctvList || [];
  console.log("[CCTV] 목록 수신:", list.length, "개");
  return list;
}

/* 좌표 거리 계산 */
const distLL = (ax, ay, bx, by) => Math.sqrt((ax - bx) ** 2 + (ay - by) ** 2);

/* 각 카드에 가장 가까운 CCTV 매칭 후 재생 */
async function assignCctv() {
  // API 키 없으면 로딩 없이 바로 MP4 폴백
  if (!ITS_KEY || ITS_KEY === "YOUR_ITS_API_KEY") {
    segments.forEach((s) => {
      s.cctvLoading = false;
    });
    return;
  }
  segments.forEach((s) => {
    s.cctvLoading = true;
  });
  try {
    const list = await fetchCctvList();
    if (!list || !list.length) {
      segments.forEach((s) => {
        s.cctvLoading = false;
      });
      return;
    }
    segments.forEach((seg) => {
      let best = null,
        bestD = Infinity;
      list.forEach((c) => {
        const cx = parseFloat(c.coordx || c.lng || 0);
        const cy = parseFloat(c.coordy || c.lat || 0);
        if (isNaN(cx) || isNaN(cy)) return;
        const d = distLL(seg.cx, seg.cy, cx, cy);
        if (d < bestD) {
          bestD = d;
          best = c;
        }
      });
      // ITS API 응답 필드: cctvurl (소문자)
      const url = best?.cctvurl || best?.cctvUrl || best?.streamUrl || null;
      seg.cctvUrl = best && bestD < 0.15 ? url : null; // 범위 0.08→0.15로 확대
      if (seg.cctvUrl) console.log("[CCTV] 매칭:", seg.name, "→", best.cctvname);
      seg.cctvLoading = false;
    });
    await nextTick();
    segments.forEach((seg) => {
      if (seg.cctvUrl) playCctv(seg);
    });
  } catch (e) {
    console.warn("ITS CCTV 오류:", e.message);
    segments.forEach((s) => {
      s.cctvLoading = false;
    }); // 항상 로딩 해제
  }
}

/* HLS 스트림 재생
   ITS CCTV URL 형식: http://cctvsec.ktict.co.kr/... (HLS 스트림)
   → hls.js로 직접 로드 */
function playCctv(seg) {
  const video = videoRefs[seg.id];
  if (!video || !seg.cctvUrl) return;
  const url = seg.cctvUrl;
  console.log("[CCTV] 재생 시도:", seg.name, url.slice(0, 60));

  if (window.Hls && window.Hls.isSupported()) {
    const hls = new window.Hls({
      enableWorker: false,
      lowLatencyMode: true,
      backBufferLength: 30,
    });
    hls.loadSource(url);
    hls.attachMedia(video);
    hls.on(window.Hls.Events.MANIFEST_PARSED, () => {
      video.play().catch(() => {});
      console.log("[CCTV] 재생 성공:", seg.name);
    });
    hls.on(window.Hls.Events.ERROR, (e, data) => {
      if (data.fatal) {
        console.warn("[CCTV] 재생 실패, MP4 폴백:", seg.name);
        seg.cctvUrl = null;
      }
    });
  } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
    video.src = url;
    video.play().catch(() => {});
  } else {
    // hls.js 없음 → MP4 폴백
    console.warn("[CCTV] hls.js 없음, MP4 폴백");
    seg.cctvUrl = null;
  }
}

/* ── WebSocket (라즈베리파이 연동) ── */
const wsConnected = ref(false);
let ws = null,
  wsRetry = null;

function connectWS() {
  // 이전 재시도 타이머 취소
  if (wsRetry) {
    clearTimeout(wsRetry);
    wsRetry = null;
  }

  try {
    ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      wsConnected.value = true;
      console.log("[WS] 라즈베리파이 연결됨");
    };

    ws.onclose = () => {
      wsConnected.value = false;
      // 10초 후 조용히 재시도 (콘솔 스팸 방지)
      wsRetry = setTimeout(connectWS, 10000);
    };

    // onerror는 onclose가 이미 처리하므로 억제
    ws.onerror = () => {
      wsConnected.value = false;
    };

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        /* 라즈베리파이 데이터 형식:
           { road:'테헤란로', speed:12, count:45, lv:'H' }
           { plate:'서울 12가 3456', dir:'IN', cam:'CAM-02', conf:96 } */
        if (data.road) {
          const seg = segments.find((s) => s.name.includes(data.road));
          if (seg) {
            seg.spd = data.speed ?? seg.spd;
            seg.cnt = data.count ?? seg.cnt;
            seg.lv = data.lv ?? seg.lv;
          }
        }
        if (data.plate) {
          plates.value = [
            {
              id: Date.now(),
              num: data.plate,
              dir: data.dir || "IN",
              cam: data.cam || "CAM",
              time: new Date().toTimeString().slice(0, 5),
              conf: data.conf || 95,
            },
            ...plates.value,
          ].slice(0, 20);
        }
      } catch (e) {}
    };
  } catch (e) {
    // WebSocket 생성 실패 → 10초 후 재시도
    wsRetry = setTimeout(connectWS, 10000);
  }
}

/* ── 상태 ── */
const timeStr = ref("");
const totalV = ref(1248),
  avgSpd = ref(31),
  cIdx = ref(68);
const flowIn = ref(842),
  flowOut = ref(406),
  accCnt = ref(2);

const kpis = computed(() => [
  {
    label: "감지 차량",
    value: totalV.value.toLocaleString(),
    unit: "대",
    color: "var(--tx)",
  },
  { label: "평균 속도", value: avgSpd.value, unit: "km/h", color: "var(--a)" },
  {
    label: "입차",
    value: flowIn.value.toLocaleString(),
    unit: "대/시",
    color: "var(--ok)",
  },
  {
    label: "출차",
    value: flowOut.value.toLocaleString(),
    unit: "대/시",
    color: "var(--warn)",
  },
  {
    label: "혼잡지수",
    value: cIdx.value,
    unit: "",
    color: cIdx.value > 70 ? "var(--danger)" : "var(--warn)",
  },
  { label: "이상 감지", value: accCnt.value, unit: "건", color: "var(--danger)" },
]);

/* ── 세그먼트 ── */
const segments = reactive([
  {
    id: "s1",
    name: "강남구 테헤란로",
    cam: "CAM-02",
    lv: "H",
    spd: 12,
    cnt: 287,
    conf: 96,
    dir: "H",
    videoUrl: "/videos/road1.mp4",
    cx: 127.0367,
    cy: 37.5007,
    cctvUrl: null,
    cctvLoading: false,
  },
  {
    id: "s2",
    name: "서초구 반포IC",
    cam: "CAM-03",
    lv: "H",
    spd: 9,
    cnt: 195,
    conf: 94,
    dir: "H",
    videoUrl: "/videos/road2.mp4",
    cx: 126.9914,
    cy: 37.5063,
    cctvUrl: null,
    cctvLoading: false,
  },
  {
    id: "s3",
    name: "영동대로",
    cam: "CAM-05",
    lv: "M",
    spd: 28,
    cnt: 134,
    conf: 97,
    dir: "V",
    videoUrl: "/videos/road3.mp4",
    cx: 127.0598,
    cy: 37.5124,
    cctvUrl: null,
    cctvLoading: false,
  },
  {
    id: "s4",
    name: "송파구 올림픽대로",
    cam: "CAM-04",
    lv: "M",
    spd: 35,
    cnt: 168,
    conf: 95,
    dir: "H",
    videoUrl: "/videos/road4.mp4",
    cx: 127.053,
    cy: 37.5172,
    cctvUrl: null,
    cctvLoading: false,
  },
  {
    id: "s5",
    name: "여의도 국회대로",
    cam: "CAM-06",
    lv: "L",
    spd: 54,
    cnt: 89,
    conf: 98,
    dir: "H",
    videoUrl: "/videos/road5.mp4",
    cx: 126.924,
    cy: 37.528,
    cctvUrl: null,
    cctvLoading: false,
  },
  {
    id: "s6",
    name: "종로구 세종대로",
    cam: "CAM-07",
    lv: "L",
    spd: 46,
    cnt: 112,
    conf: 97,
    dir: "H",
    videoUrl: "/videos/road6.mp4",
    cx: 126.9769,
    cy: 37.564,
    cctvUrl: null,
    cctvLoading: false,
  },
]);

/* ── 카메라 ── */
const cameras = reactive([
  { id: "CAM-01", loc: "강남역 사거리", ok: false, cnt: 142 },
  { id: "CAM-02", loc: "테헤란로 역삼", ok: true, cnt: 287 },
  { id: "CAM-03", loc: "반포IC 진입", ok: true, cnt: 195 },
  { id: "CAM-04", loc: "잠실대교 남단", ok: true, cnt: 168 },
  { id: "CAM-05", loc: "영동대교 북단", ok: true, cnt: 134 },
  { id: "CAM-06", loc: "여의도 국회대로", ok: true, cnt: 89 },
]);

/* ── 번호판 ── */
const plates = ref([
  { id: 1, num: "서울 12가 3456", dir: "IN", cam: "CAM-02", time: "14:42", conf: 97.2 },
  { id: 2, num: "경기 78나 9012", dir: "OUT", cam: "CAM-03", time: "14:38", conf: 95.8 },
  { id: 3, num: "서울 34다 5678", dir: "IN", cam: "CAM-02", time: "14:35", conf: 98.1 },
  { id: 4, num: "인천 56라 7890", dir: "IN", cam: "CAM-04", time: "14:31", conf: 94.3 },
  { id: 5, num: "서울 90마 1234", dir: "OUT", cam: "CAM-05", time: "14:28", conf: 96.7 },
  { id: 6, num: "경기 11바 2345", dir: "IN", cam: "CAM-06", time: "14:24", conf: 97.9 },
]);
const plateSearch = ref("");
const filteredPlates = computed(() => {
  if (!plateSearch.value) return plates.value;
  return plates.value.filter((p) => p.num.includes(plateSearch.value));
});

/* ── 이벤트 ── */
const incidents = ref([
  { id: 1, time: "14:38", type: "교통사고", loc: "강남구 테헤란로 119", lv: "H" },
  { id: 2, time: "14:22", type: "도로공사", loc: "서초구 반포IC 진입", lv: "M" },
  { id: 3, time: "14:05", type: "차량고장", loc: "잠실대교 남단 2차로", lv: "M" },
  { id: 4, time: "13:48", type: "신호고장", loc: "강남역 사거리", lv: "H" },
  { id: 5, time: "13:31", type: "낙하물", loc: "올림픽대로 동방면", lv: "L" },
]);

/* ── 통계 ── */
const heatZones = reactive([
  { name: "강남·서초", pct: 88 },
  { name: "송파·강동", pct: 62 },
  { name: "마포·영등포", pct: 55 },
  { name: "종로·중구", pct: 43 },
  { name: "노원·도봉", pct: 28 },
  { name: "용산·성동", pct: 71 },
]);
const rtStats = computed(() => [
  {
    label: "총 통행량",
    value: (flowIn.value + flowOut.value).toLocaleString(),
    color: "var(--tx)",
  },
  { label: "입차", value: flowIn.value.toLocaleString(), color: "var(--ok)" },
  { label: "출차", value: flowOut.value.toLocaleString(), color: "var(--warn)" },
  {
    label: "혼잡 구간",
    value: segments.filter((s) => s.lv === "H").length + "개",
    color: "var(--danger)",
  },
  { label: "이상 감지", value: accCnt.value + "건", color: "var(--danger)" },
  { label: "평균 인식률", value: "96.2%", color: "var(--a)" },
]);

/* ── 알림 ── */
const thresholds = reactive({ congSpeed: 20, slowSpeed: 40 });
const alerts = reactive([
  {
    id: 1,
    lv: "H",
    title: "테헤란로 혼잡 감지",
    desc: "평균 속도 12km/h — 임계값 초과",
    time: "14:38",
  },
  {
    id: 2,
    lv: "H",
    title: "CAM-01 장애 감지",
    desc: "강남역 사거리 카메라 응답 없음",
    time: "13:48",
  },
  {
    id: 3,
    lv: "M",
    title: "반포IC 서행 구간",
    desc: "평균 속도 28km/h — 주의 필요",
    time: "14:22",
  },
]);
const notifQueue = reactive([]);
let notifId = 100;

function pushNotif(lv, title, desc) {
  const id = ++notifId;
  notifQueue.push({ id, lv, title, desc });
  setTimeout(() => dismissNotif(id), 5000);
}
function dismissNotif(id) {
  const i = notifQueue.findIndex((n) => n.id === id);
  if (i >= 0) notifQueue.splice(i, 1);
}
function dismissAlert(id) {
  const i = alerts.findIndex((a) => a.id === id);
  if (i >= 0) alerts.splice(i, 1);
}

/* 속도 감시 → 알림 자동 생성 */
watch(
  () => segments.map((s) => s.spd),
  (spds) => {
    segments.forEach((seg, i) => {
      if (seg.spd < thresholds.congSpeed && seg.lv !== "H") {
        pushNotif("H", `${seg.name} 혼잡 감지`, `평균 속도 ${Math.round(seg.spd)}km/h`);
      }
    });
  },
  { deep: true }
);

/* ── 티커 ── */
const TICKER_ITEMS = [
  { lv: "H", text: "[강남] 테헤란로 역삼 혼잡 — CAM-02 287대 감지 / 평균 12km/h" },
  { lv: "H", text: "[서초] 반포IC 진입로 사고 감지 — 주의 요망" },
  { lv: "M", text: "[영동] 영동대로 지체 구간 확인 — CAM-05 정상" },
  { lv: "L", text: "[올림픽] 올림픽대로 원활 / 54km/h" },
  { lv: "H", text: "[강남역] CAM-01 장애 — 현장 점검 출동" },
  { lv: "L", text: "[세종대로] 원활 / 인식률 97% 유지" },
];
const tickerDouble = computed(() => [...TICKER_ITEMS, ...TICKER_ITEMS]);

/* ── 풀스크린 ── */
const fullscreenSeg = ref(null);
const fsYoloRef = ref(null);
const fsStats = computed(() =>
  fullscreenSeg.value
    ? [
        { label: "감지 차량", value: fullscreenSeg.value.cnt },
        { label: "평균 속도", value: Math.round(fullscreenSeg.value.spd) + "km/h" },
        { label: "인식률", value: fullscreenSeg.value.conf + "%" },
        { label: "카메라", value: fullscreenSeg.value.cam },
        {
          label: "소통 상태",
          value:
            fullscreenSeg.value.lv === "H"
              ? "정체 주의"
              : fullscreenSeg.value.lv === "M"
              ? "서행 중"
              : "소통 원활",
          color: levelColor(fullscreenSeg.value.lv),
        },
      ]
    : []
);

function openFullscreen(seg) {
  fullscreenSeg.value = seg;
}
function closeFullscreen() {
  fullscreenSeg.value = null;
}

/* ── 통계 차트 ── */
const chartRef = ref(null);
const CHART_H = ["07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18"];
const chartData = reactive([
  4200,
  7800,
  8900,
  7200,
  6100,
  6800,
  7100,
  7600,
  8100,
  8500,
  8900,
  8100,
]);

function drawChart() {
  const canvas = chartRef.value;
  if (!canvas) return;
  const W = canvas.offsetWidth || 600,
    H = 120;
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, W, H);
  const pl = 8,
    pr = 8,
    pt = 10,
    pb = 22,
    cw = W - pl - pr,
    ch = H - pt - pb;
  const mx = Math.max(...chartData) * 1.08;
  const pts = chartData.map((v, i) => ({
    px: pl + i * (cw / (chartData.length - 1)),
    py: pt + ch * (1 - v / mx),
  }));
  const gr = ctx.createLinearGradient(0, pt, 0, pt + ch);
  gr.addColorStop(0, "rgba(62,201,214,0.20)");
  gr.addColorStop(1, "rgba(62,201,214,0)");
  ctx.beginPath();
  ctx.moveTo(pts[0].px, pt + ch);
  pts.forEach((p) => ctx.lineTo(p.px, p.py));
  ctx.lineTo(pts[pts.length - 1].px, pt + ch);
  ctx.closePath();
  ctx.fillStyle = gr;
  ctx.fill();
  ctx.beginPath();
  pts.forEach((p, i) => (i === 0 ? ctx.moveTo(p.px, p.py) : ctx.lineTo(p.px, p.py)));
  ctx.strokeStyle = "#3ec9d6";
  ctx.lineWidth = 2;
  ctx.shadowColor = "#3ec9d6";
  ctx.shadowBlur = 6;
  ctx.stroke();
  ctx.shadowBlur = 0;
  pts.forEach((p, i) => {
    ctx.beginPath();
    ctx.arc(p.px, p.py, 3, 0, Math.PI * 2);
    ctx.fillStyle = "#3ec9d6";
    ctx.fill();
    ctx.fillStyle = "rgba(110,150,175,.55)";
    ctx.font = "8px Share Tech Mono,monospace";
    ctx.textAlign = "center";
    ctx.fillText(CHART_H[i] + "시", p.px, H - 4);
  });
}

/* ── 히트맵 색상 ── */
function hmColor(pct) {
  if (pct > 70) return `rgba(224,82,96,${0.15 + pct / 300})`;
  if (pct > 45) return `rgba(212,132,90,${0.12 + pct / 400})`;
  return `rgba(76,175,125,${0.1 + pct / 500})`;
}

/* ── 헬퍼 ── */
const LEVEL_COLOR = { H: "#e05260", M: "#d4845a", L: "#4caf7d" };
const levelColor = (lv) => LEVEL_COLOR[lv] || "#3ec9d6";

/* ── 캔버스 / 비디오 refs ── */
const canvasRefs = {},
  videoRefs = {},
  segCars = {};
const VCOLORS = { H: "#e05260", M: "#d4845a", L: "#4caf7d" };

/* 배경 캔버스 */
function initCars(seg) {
  const n = seg.lv === "H" ? 6 : seg.lv === "M" ? 4 : 2,
    s = seg.lv === "H" ? 0.35 : seg.lv === "M" ? 1.4 : 2.8;
  const cars = [];
  [1, -1].forEach((dir) => {
    for (let i = 0; i < n; i++)
      cars.push({
        pos: Math.random(),
        dir,
        spd: s * (0.8 + Math.random() * 0.4),
        stop: 0,
        lv: seg.lv,
        col: VCOLORS[seg.lv],
      });
  });
  segCars[seg.id] = cars;
}
function drawCanvas(canvas, seg) {
  const W = canvas.width,
    H = canvas.height;
  if (!W || !H) return;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "#06080f";
  ctx.fillRect(0, 0, W, H);
  const isV = seg.dir === "V",
    RW = isV ? W * 0.42 : H * 0.42,
    LW = RW / 2,
    rc = isV ? W / 2 : H / 2;
  const rdBg = {
    H: "rgba(224,82,96,0.14)",
    M: "rgba(212,132,90,0.12)",
    L: "rgba(76,175,125,0.11)",
  };
  const edCol = {
    H: "rgba(224,82,96,0.75)",
    M: "rgba(212,132,90,0.70)",
    L: "rgba(76,175,125,0.70)",
  };
  ctx.fillStyle = rdBg[seg.lv];
  if (isV) ctx.fillRect(rc - RW / 2, 0, RW, H);
  else ctx.fillRect(0, rc - RW / 2, W, RW);
  ctx.strokeStyle = edCol[seg.lv];
  ctx.lineWidth = 1.5;
  if (isV) {
    [[rc - RW / 2], [rc + RW / 2]].forEach(([x]) => {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, H);
      ctx.stroke();
    });
  } else {
    [[rc - RW / 2], [rc + RW / 2]].forEach(([y]) => {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    });
  }
  ctx.strokeStyle = "rgba(200,170,0,0.55)";
  ctx.lineWidth = 1;
  if (isV) {
    ctx.beginPath();
    ctx.moveTo(rc, 0);
    ctx.lineTo(rc, H);
    ctx.stroke();
  } else {
    ctx.beginPath();
    ctx.moveTo(0, rc);
    ctx.lineTo(W, rc);
    ctx.stroke();
  }
  const cars = segCars[seg.id] || [],
    CL = LW * 0.72,
    CW = LW * 0.46;
  cars.forEach((car) => {
    if (car.lv === "H") {
      if (car.stop > 0) {
        car.stop--;
        return;
      }
      if (Math.random() < 0.004) {
        car.stop = 30 + Math.floor(Math.random() * 80);
      }
    }
    car.pos += (car.spd / 1000) * car.dir;
    if (car.pos > 1.02) car.pos = -0.02;
    if (car.pos < -0.02) car.pos = 1.02;
    const cx = isV ? rc + (car.dir * LW) / 2 : car.pos * W,
      cy = isV ? car.pos * H : rc + (car.dir * LW) / 2;
    ctx.save();
    ctx.shadowColor = car.col;
    ctx.shadowBlur = 7;
    ctx.fillStyle = car.col;
    ctx.globalAlpha = car.stop > 0 ? 0.38 : 0.9;
    ctx.translate(cx, cy);
    if (isV) {
      ctx.fillRect(-CW / 2, -CL / 2, CW, CL);
    } else {
      ctx.fillRect(-CL / 2, -CW / 2, CL, CW);
    }
    ctx.restore();
  });
}

/* ── 라이프사이클 ── */
let clockTimer = null,
  dataTimer = null,
  animId = null;

onMounted(async () => {
  clockTimer = setInterval(() => {
    const n = new Date();
    timeStr.value = [n.getHours(), n.getMinutes(), n.getSeconds()]
      .map((v) => String(v).padStart(2, "0"))
      .join(":");
  }, 1000);

  segments.forEach((s) => initCars(s));
  connectWS();
  assignCctv(); /* ITS CCTV 연결 */

  const animate = () => {
    segments.forEach((seg) => {
      if (!seg.videoUrl) {
        const canvas = canvasRefs[seg.id];
        if (canvas) {
          const wrap = canvas.parentElement;
          if (wrap) {
            const nw = wrap.clientWidth || 200,
              nh = wrap.clientHeight || 100;
            if (canvas.width !== nw || canvas.height !== nh) {
              canvas.width = nw;
              canvas.height = nh;
            }
          }
          drawCanvas(canvas, seg);
        }
      }
    });
    animId = requestAnimationFrame(animate);
  };
  setTimeout(() => {
    animId = requestAnimationFrame(animate);
  }, 200);

  await nextTick();
  setTimeout(drawChart, 500);

  dataTimer = setInterval(() => {
    totalV.value = 1100 + Math.round(Math.random() * 300);
    avgSpd.value = 27 + Math.round(Math.random() * 9);
    cIdx.value = 60 + Math.round(Math.random() * 15);
    flowIn.value = 750 + Math.round(Math.random() * 200);
    flowOut.value = 350 + Math.round(Math.random() * 150);
    cameras.forEach((c) => {
      c.cnt = Math.max(50, c.cnt + Math.round((Math.random() - 0.35) * 8));
    });
    segments.forEach((s) => {
      s.spd = Math.max(5, s.spd + (Math.random() > 0.5 ? 1 : -1) * Math.random() * 2);
      s.cnt = Math.max(10, s.cnt + Math.round((Math.random() - 0.5) * 6));
    });
    heatZones.forEach((z) => {
      z.pct = Math.max(10, Math.min(95, z.pct + Math.round((Math.random() - 0.5) * 5)));
    });
    chartData.push(6000 + Math.round(Math.random() * 3000));
    chartData.shift();
    drawChart();
  }, 4000);

  // 초기 알림
  setTimeout(
    () => pushNotif("H", "테헤란로 혼잡 감지", "평균 속도 12km/h — 임계값 초과"),
    2000
  );
  setTimeout(() => pushNotif("M", "반포IC 서행 감지", "평균 속도 28km/h"), 5000);
});

onUnmounted(() => {
  clearInterval(clockTimer);
  clearInterval(dataTimer);
  if (animId) cancelAnimationFrame(animId);
  if (wsRetry) clearTimeout(wsRetry);
  if (ws) ws.close();
});
</script>

<style scoped>
.theme-navy {
  --danger: #e05260;
  --warn: #d4845a;
  --ok: #4caf7d;
}
.dash-shell {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 62px);
  margin-top: 62px;
  overflow: hidden;
  background: var(--bg);
}

/* ── 탭바 ── */
.tabbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 48px;
  flex-shrink: 0;
  background: var(--bg2);
  border-bottom: 1px solid var(--b);
}
.tab-inner {
  display: flex;
  gap: 2px;
}
.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  font-size: 11.5px;
  font-weight: 500;
  color: var(--t2);
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 4px 4px 0 0;
  transition: all 0.2s;
}
.tab-btn:hover {
  color: var(--t);
  background: rgba(255, 255, 255, 0.04);
}
.tab-btn.active {
  color: var(--a);
  background: rgba(62, 201, 214, 0.08);
  border-bottom: 2px solid var(--a);
}
.tab-icon {
  width: 13px;
  height: 13px;
  flex-shrink: 0;
}
.tab-badge {
  background: var(--danger);
  color: #fff;
  font-size: 9px;
  font-family: "IBM Plex Mono", monospace;
  padding: 1px 5px;
  border-radius: 8px;
  min-width: 16px;
  text-align: center;
}
.tab-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.tab-ws {
  font-size: 8px;
  letter-spacing: 1px;
  font-family: "IBM Plex Mono", monospace;
  padding: 2px 8px;
  border: 1px solid;
  border-radius: 2px;
}
.tab-ws.ok {
  color: var(--ok);
  border-color: rgba(76, 175, 125, 0.35);
}
.tab-ws.err {
  color: var(--mu);
  border-color: rgba(255, 255, 255, 0.1);
}
.tab-clock {
  font-family: "IBM Plex Mono", monospace;
  font-size: 13px;
  color: var(--a);
  letter-spacing: 2px;
}
.tab-live {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 8px;
  letter-spacing: 2px;
  color: var(--ok);
  border: 1px solid rgba(76, 175, 125, 0.4);
  padding: 3px 10px;
}
.live-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--ok);
  animation: lp 1.4s ease-in-out infinite;
}
@keyframes lp {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.15;
  }
}

/* ── 바디 ── */
.dash-body {
  flex: 1;
  overflow: hidden;
  min-height: 0;
}
.tab-content {
  height: 100%;
  overflow-y: auto;
  padding: 12px 14px 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* ── KPI ── */
.kpi-bar {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 7px;
  flex-shrink: 0;
}
.kpi {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 6px;
  padding: 10px 12px;
  transition: border-color 0.2s;
}
.kpi:hover {
  border-color: var(--ba);
}
.kpi-v {
  font-size: 21px;
  font-weight: 700;
  line-height: 1;
  display: flex;
  align-items: baseline;
  gap: 3px;
}
.kpi-unit {
  font-size: 9px;
  color: var(--t3);
  font-family: "IBM Plex Mono", monospace;
}
.kpi-l {
  font-size: 8.5px;
  color: var(--t3);
  margin-top: 4px;
  letter-spacing: 0.5px;
}

/* ── 도로 그리드 ── */
.road-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 7px;
  min-height: 0;
  padding-bottom: 12px;
}
.rcard {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.25s, transform 0.2s;
}
.rcard:hover {
  transform: translateY(-1px);
}
.rcard:hover .rc-fullscreen-hint {
  opacity: 1;
}
.rcard.H {
  border-color: rgba(224, 82, 96, 0.3);
}
.rcard.M {
  border-color: rgba(212, 132, 90, 0.26);
}
.rcard.L {
  border-color: rgba(76, 175, 125, 0.26);
}
.rc-top {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}
.rc-lv-bar {
  width: 3px;
  height: 44px;
  flex-shrink: 0;
}
.rc-info {
  flex: 1;
  padding: 7px 10px;
  min-width: 0;
}
.rc-name {
  font-size: 11px;
  font-weight: 500;
  color: var(--t);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.rc-cam {
  font-size: 8.5px;
  color: var(--t3);
  margin-top: 2px;
}
.rc-badge {
  font-family: "IBM Plex Mono", monospace;
  font-size: 7px;
  padding: 2px 7px;
  border: 1px solid;
  border-radius: 2px;
  white-space: nowrap;
  flex-shrink: 0;
  margin-right: 10px;
  letter-spacing: 1px;
}
.lv-H {
  color: var(--danger);
  border-color: rgba(224, 82, 96, 0.45);
  background: rgba(224, 82, 96, 0.1);
}
.lv-M {
  color: var(--warn);
  border-color: rgba(212, 132, 90, 0.4);
  background: rgba(212, 132, 90, 0.08);
}
.lv-L {
  color: var(--ok);
  border-color: rgba(76, 175, 125, 0.4);
  background: rgba(76, 175, 125, 0.08);
}
.rc-media-wrap {
  flex: 1;
  min-height: 0;
  position: relative;
  overflow: hidden;
}
.rc-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
}
.rc-canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.rc-speed-overlay {
  position: absolute;
  top: 7px;
  right: 9px;
  display: flex;
  align-items: baseline;
  gap: 3px;
  background: rgba(6, 8, 15, 0.8);
  padding: 3px 7px;
  border-radius: 4px;
  z-index: 15;
}
.rc-spd-num {
  font-family: "IBM Plex Mono", monospace;
  font-size: 17px;
  font-weight: 700;
  line-height: 1;
}
.rc-spd-unit {
  font-size: 8px;
  color: var(--mu);
}
.rc-fullscreen-hint {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  font-family: "IBM Plex Mono", monospace;
  font-size: 8px;
  letter-spacing: 1.5px;
  color: rgba(62, 201, 214, 0.7);
  background: rgba(0, 0, 0, 0.7);
  padding: 3px 10px;
  border-radius: 2px;
  z-index: 15;
  opacity: 0;
  transition: opacity 0.2s;
  white-space: nowrap;
}
.rc-bottom {
  display: flex;
  align-items: center;
  padding: 5px 10px;
  flex-shrink: 0;
  border-top: 1px solid var(--b);
}
.rc-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.rc-divider {
  width: 1px;
  height: 22px;
  background: var(--b);
}
.rc-sv {
  font-family: "IBM Plex Mono", monospace;
  font-size: 12px;
  font-weight: 600;
  color: var(--t);
  line-height: 1;
}
.rc-sl {
  font-size: 7.5px;
  color: var(--t3);
}
.rc-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ── 섹션 ── */
.section-head {
  flex-shrink: 0;
  padding-bottom: 4px;
}
.sh-title {
  font-family: "Syne", sans-serif;
  font-size: 19px;
  font-weight: 700;
  color: var(--t);
  letter-spacing: -0.5px;
}
.sh-sub {
  font-size: 12px;
  color: var(--t2);
  margin-top: 4px;
  font-weight: 300;
}

/* ── 카메라 ── */
.cam-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding-bottom: 12px;
}
.cam-card {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 8px;
  padding: 16px;
  transition: border-color 0.2s;
}
.cam-card:hover {
  border-color: var(--ba);
}
.cam-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.cam-id-badge {
  font-family: "IBM Plex Mono", monospace;
  font-size: 10px;
  color: var(--a);
  background: rgba(62, 201, 214, 0.08);
  border: 1px solid rgba(62, 201, 214, 0.2);
  padding: 2px 8px;
  border-radius: 3px;
}
.cam-status {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 9px;
  letter-spacing: 1px;
  font-family: "IBM Plex Mono", monospace;
}
.cam-status.ok {
  color: var(--ok);
}
.cam-status.err {
  color: var(--danger);
}
.cam-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
.cam-status.ok .cam-dot {
  box-shadow: 0 0 5px var(--ok);
}
.cam-status.err .cam-dot {
  box-shadow: 0 0 5px var(--danger);
}
.cam-loc-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--t);
  margin-bottom: 12px;
}
.cam-stats {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}
.cam-stat {
  text-align: center;
}
.cam-stat-v {
  font-family: "IBM Plex Mono", monospace;
  font-size: 15px;
  font-weight: 700;
  color: var(--t);
}
.cam-stat-l {
  font-size: 8px;
  color: var(--t3);
  margin-top: 2px;
}
.cam-bar-wrap {
  height: 4px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
  overflow: hidden;
}
.cam-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 1.4s ease;
}

/* ── 번호판 ── */
.plate-search {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.search-input {
  flex: 1;
  background: var(--card);
  border: 1px solid var(--b);
  color: var(--t);
  padding: 8px 12px;
  font-size: 12px;
  font-family: "IBM Plex Mono", monospace;
  border-radius: 4px;
  outline: none;
  transition: border-color 0.2s;
}
.search-input:focus {
  border-color: var(--a);
}
.search-input::placeholder {
  color: var(--t3);
}
.search-result-cnt {
  font-size: 11px;
  color: var(--mu);
  white-space: nowrap;
}
.plate-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-bottom: 12px;
}
.plate-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 7px;
}
.pstat {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 8px;
  padding: 12px 14px;
}
.pstat-v {
  font-family: "IBM Plex Mono", monospace;
  font-size: 22px;
  font-weight: 700;
  color: var(--t);
}
.pstat-l {
  font-size: 8.5px;
  color: var(--t3);
  margin-top: 3px;
}
.plate-table {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 8px;
  overflow: hidden;
}
.pt-head {
  display: grid;
  grid-template-columns: 2fr 1fr 1.2fr 1fr 1fr;
  padding: 9px 16px;
  font-size: 9px;
  color: var(--t3);
  letter-spacing: 1px;
  border-bottom: 1px solid var(--b);
  background: rgba(0, 0, 0, 0.1);
}
.pt-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1.2fr 1fr 1fr;
  padding: 9px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  align-items: center;
  transition: background 0.15s;
}
.pt-row:hover {
  background: rgba(255, 255, 255, 0.03);
}
.pt-row:last-child {
  border-bottom: none;
}
.pt-num {
  font-family: "IBM Plex Mono", monospace;
  font-size: 12px;
  font-weight: 500;
  color: var(--t);
}
.dir-badge {
  font-family: "IBM Plex Mono", monospace;
  font-size: 8px;
  padding: 2px 6px;
  border: 1px solid;
  border-radius: 2px;
  letter-spacing: 1px;
}
.dir-badge.IN {
  color: var(--ok);
  border-color: rgba(76, 175, 125, 0.4);
  background: rgba(76, 175, 125, 0.08);
}
.dir-badge.OUT {
  color: var(--warn);
  border-color: rgba(212, 132, 90, 0.4);
  background: rgba(212, 132, 90, 0.08);
}
/* 번호판 슬라이드 애니메이션 */
.plate-slide-enter-active {
  transition: all 0.3s ease;
}
.plate-slide-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

/* ── 이벤트 ── */
.ev-list-full {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-bottom: 12px;
}
.ev-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 6px;
  overflow: hidden;
  padding-right: 14px;
  transition: border-color 0.2s;
}
.ev-item:hover {
  border-color: var(--ba);
}
.ev-lv-stripe {
  width: 4px;
  height: 50px;
  flex-shrink: 0;
}
.ev-time {
  font-family: "IBM Plex Mono", monospace;
  font-size: 11px;
  color: var(--t3);
  width: 44px;
  flex-shrink: 0;
}
.ev-badge {
  font-family: "IBM Plex Mono", monospace;
  font-size: 8px;
  padding: 3px 9px;
  border: 1px solid;
  border-radius: 3px;
  flex-shrink: 0;
  letter-spacing: 1px;
}
.ev-loc {
  flex: 1;
  font-size: 12px;
  color: var(--t);
}
.ev-status {
  font-size: 9px;
  color: var(--t3);
  font-family: "IBM Plex Mono", monospace;
  white-space: nowrap;
}

/* ── 통계 ── */
.stats-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 10px;
  padding-bottom: 12px;
  min-height: 0;
}
.stat-card {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.stat-card.wide {
  grid-column: span 1;
}
.stat-card-title {
  font-size: 9px;
  color: var(--a);
  letter-spacing: 2px;
  opacity: 0.75;
}
.stat-canvas {
  display: block;
  width: 100%;
  flex: 1;
}
/* 히트맵 */
.heatmap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  flex: 1;
}
.hm-cell {
  border-radius: 6px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 1px solid rgba(255, 255, 255, 0.06);
}
.hm-name {
  font-size: 9.5px;
  color: rgba(255, 255, 255, 0.8);
}
.hm-pct {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}
/* 실시간 집계 */
.rt-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.rt-stat {
  background: var(--bg2);
  border-radius: 4px;
  padding: 10px;
}
.rt-v {
  font-family: "IBM Plex Mono", monospace;
  font-size: 18px;
  font-weight: 700;
}
.rt-l {
  font-size: 8px;
  color: var(--t3);
  margin-top: 3px;
}

/* ── 알림 ── */
.alert-setting {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 8px;
  padding: 14px;
  flex-shrink: 0;
}
.alert-setting-title {
  font-size: 9px;
  color: var(--a);
  letter-spacing: 2px;
  opacity: 0.75;
  margin-bottom: 12px;
}
.alert-thresholds {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.threshold-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 11px;
  color: var(--t2);
}
.th-label {
  width: 100px;
  flex-shrink: 0;
}
.th-slider {
  flex: 1;
  accent-color: var(--a);
}
.th-val {
  font-family: "IBM Plex Mono", monospace;
  font-size: 11px;
  color: var(--a);
  width: 90px;
  text-align: right;
  flex-shrink: 0;
}
.alert-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-bottom: 12px;
}
.no-alerts {
  text-align: center;
  color: var(--mu);
  font-size: 11px;
  padding: 30px;
  opacity: 0.5;
}
.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 6px;
  overflow: hidden;
  padding-right: 14px;
}
.alert-stripe {
  width: 4px;
  height: 56px;
  flex-shrink: 0;
}
.alert-icon {
  font-size: 18px;
  flex-shrink: 0;
}
.alert-body {
  flex: 1;
  min-width: 0;
}
.alert-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--t);
}
.alert-desc {
  font-size: 10px;
  color: var(--t2);
  margin-top: 3px;
}
.alert-time {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  color: var(--t3);
  flex-shrink: 0;
}
.alert-dismiss {
  background: none;
  border: none;
  color: var(--t3);
  cursor: pointer;
  font-size: 14px;
  padding: 4px 8px;
  transition: color 0.2s;
}
.alert-dismiss:hover {
  color: var(--danger);
}

/* ── 풀스크린 모달 ── */
.fs-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.88);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
}
.fs-modal {
  background: var(--bg2);
  border: 1px solid var(--br2);
  border-radius: 12px;
  width: 80vw;
  max-width: 900px;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.fs-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--b);
  flex-shrink: 0;
}
.fs-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--t);
  flex: 1;
}
.fs-badge {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  padding: 3px 10px;
  border: 1px solid;
  border-radius: 3px;
  letter-spacing: 1px;
}
.fs-spd {
  font-size: 18px;
  font-weight: 700;
}
.fs-close {
  background: none;
  border: none;
  color: var(--t3);
  cursor: pointer;
  font-size: 20px;
  padding: 4px 8px;
  margin-left: 8px;
  transition: color 0.2s;
}
.fs-close:hover {
  color: var(--danger);
}
.fs-body {
  flex: 1;
  position: relative;
  min-height: 0;
  overflow: hidden;
}
.fs-video {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}
.fs-canvas {
  width: 100%;
  height: 100%;
  display: block;
}
.fs-yolo {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 5;
}
.fs-speed-overlay {
  position: absolute;
  top: 14px;
  right: 16px;
  display: flex;
  align-items: baseline;
  gap: 5px;
  background: rgba(0, 0, 0, 0.8);
  padding: 6px 14px;
  border-radius: 6px;
  z-index: 10;
}
.fs-footer {
  display: flex;
  gap: 0;
  border-top: 1px solid var(--b);
  flex-shrink: 0;
}
.fs-stat {
  flex: 1;
  text-align: center;
  padding: 12px 8px;
  border-right: 1px solid var(--b);
}
.fs-stat:last-child {
  border-right: none;
}
.fs-sv {
  font-family: "IBM Plex Mono", monospace;
  font-size: 15px;
  font-weight: 700;
}
.fs-sl {
  font-size: 8px;
  color: var(--t3);
  margin-top: 3px;
}

/* ── 알림 팝업 ── */
.notif-container {
  position: fixed;
  bottom: 44px;
  right: 18px;
  z-index: 900;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
  width: 300px;
}
.notif {
  display: flex;
  align-items: stretch;
  background: var(--bg2);
  border: 1px solid var(--b);
  border-radius: 6px;
  overflow: hidden;
  pointer-events: all;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}
.notif-bar {
  width: 4px;
  flex-shrink: 0;
}
.notif-body {
  flex: 1;
  padding: 10px 12px;
}
.notif-title {
  font-family: "IBM Plex Mono", monospace;
  font-size: 10px;
  font-weight: 600;
  color: var(--t);
  letter-spacing: 0.5px;
}
.notif-desc {
  font-size: 9.5px;
  color: var(--t2);
  margin-top: 3px;
}
.notif-close {
  background: none;
  border: none;
  color: var(--t3);
  cursor: pointer;
  font-size: 14px;
  padding: 0 10px;
}
.notif-close:hover {
  color: var(--danger);
}
.notif-enter-active {
  transition: all 0.3s ease;
}
.notif-leave-active {
  transition: all 0.25s ease;
}
.notif-enter-from {
  transform: translateX(100%);
  opacity: 0;
}
.notif-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* ── 티커 ── */
.ticker-bar {
  height: 34px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  overflow: hidden;
  background: var(--bg2);
  border-top: 1px solid var(--b);
}
.ticker-label {
  font-family: "IBM Plex Mono", monospace;
  font-size: 8px;
  letter-spacing: 2px;
  color: var(--a);
  opacity: 0.7;
  padding: 0 14px;
  border-right: 1px solid var(--b);
  white-space: nowrap;
  flex-shrink: 0;
}
.ticker-wrap {
  flex: 1;
  overflow: hidden;
}
.ticker-track {
  display: flex;
  gap: 28px;
  white-space: nowrap;
  animation: tickerMove 32s linear infinite;
}
@keyframes tickerMove {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-50%);
  }
}
.ticker-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: "IBM Plex Mono", monospace;
  font-size: 8.5px;
  color: var(--t2);
}
.ticker-dot {
  display: inline-block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ── 유틸 ── */
.mono {
  font-family: "IBM Plex Mono", monospace;
}
.in-color {
  color: var(--ok);
}
.out-color {
  color: var(--warn);
}
.blink {
  animation: lp 1.4s ease-in-out infinite;
}

.rc-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: rgba(6, 8, 15, 0.92);
  z-index: 2;
}
.loading-ring {
  width: 28px;
  height: 28px;
  border: 2px solid rgba(62, 201, 214, 0.15);
  border-top-color: var(--a);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ── 반응형 ── */
@media (max-width: 1300px) {
  .kpi-bar {
    grid-template-columns: repeat(3, 1fr);
  }
  .road-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(3, 1fr);
  }
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
}
@media (max-width: 768px) {
  .road-grid {
    grid-template-columns: 1fr;
  }
  .cam-grid {
    grid-template-columns: 1fr 1fr;
  }
  .plate-stats {
    grid-template-columns: 1fr 1fr;
  }
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .fs-modal {
    width: 95vw;
  }
}
</style>
