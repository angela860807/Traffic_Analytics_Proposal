<template>
  <div v-show="active" class="v2-tab-page">
    <div class="v2-page-h">
      <h2><i class="bi bi-camera-video-fill"></i> 실시간 카메라 모니터링</h2>
      <div class="v2-page-actions">
        <div class="v2-mon-summary">
          <span><i class="bi bi-broadcast-pin"></i> 가동 <b>{{ stats.online }}</b>대 / 전체 {{ cameraFeeds.length }}대</span>
          <span class="v2-sep">·</span>
          <span>평균 인식률 <b class="v2-em">{{ avgRecognition }}%</b></span>
          <span class="v2-sep">·</span>
          <span>총 검출 <b class="v2-em">{{ totalDetected.toLocaleString() }}</b>건</span>
        </div>
        <button class="v2-btn-secondary" @click="refreshAll"><i class="bi bi-arrow-clockwise"></i> 새로고침</button>
      </div>
    </div>

    <!-- 카메라 상세 그리드 (3×2) -->
    <div class="v2-mon-grid">
      <div v-for="(cam, i) in cameraFeeds" :key="cam.name"
           class="v2-mon-cell"
           :class="{ 'v2-mon-warn': health(i).status === 'warn', 'v2-mon-offline': health(i).status === 'offline' }">
        <!-- 카메라 헤더 -->
        <div class="v2-mon-top">
          <span class="v2-mon-dot" :class="health(i).status"></span>
          <span class="v2-mon-name">{{ cam.name }}</span>
          <span class="v2-mon-id mono">CAM-{{ String(i + 1).padStart(2, '0') }}</span>
          <span class="v2-mon-hb mono" :class="health(i).status">
            <i class="bi bi-broadcast"></i>
            {{ health(i).sec }}s 전
          </span>
          <button class="v2-mon-mute" :class="{ on: isMuted(i) }"
                  @click="toggleCameraMute(cam.name)"
                  :title="isMuted(i) ? '알람 음소거 해제' : '알람 음소거 (점검 중)'">
            <i :class="isMuted(i) ? 'bi bi-bell-slash-fill' : 'bi bi-bell-fill'"></i>
          </button>
          <span class="v2-mon-badge" :class="health(i).status">
            {{ health(i).status === 'online' ? 'LIVE' : health(i).status === 'warn' ? '지연' : '끊김' }}
          </span>
        </div>

        <!-- 영상 + 오버레이 -->
        <div class="v2-mon-video-wrap">
          <video
            :src="cam.src"
            autoplay muted loop playsinline
            preload="metadata"
            disablepictureinpicture
            class="v2-mon-video"
            @loadedmetadata="onCamLoaded"
          ></video>
          <div class="v2-mon-overlay">
            <div class="v2-mon-conf-row">
              <span>OCR 신뢰도</span>
              <div class="v2-mon-conf-bar">
                <div class="v2-mon-conf-fill" :style="{ width: camStats[i].confidence + '%' }"></div>
              </div>
              <b>{{ camStats[i].confidence }}%</b>
            </div>
          </div>
        </div>

        <!-- 카메라별 통계 -->
        <div class="v2-mon-stats">
          <div class="v2-mon-stat">
            <i class="bi bi-bullseye"></i>
            <div>
              <div class="v2-mon-stat-label">인식률</div>
              <div class="v2-mon-stat-value">{{ camStats[i].recognition }}<small>%</small></div>
            </div>
          </div>
          <div class="v2-mon-stat">
            <i class="bi bi-car-front"></i>
            <div>
              <div class="v2-mon-stat-label">검출 수</div>
              <div class="v2-mon-stat-value">{{ camStats[i].detected }}<small>건</small></div>
            </div>
          </div>
          <div class="v2-mon-stat">
            <i class="bi bi-speedometer"></i>
            <div>
              <div class="v2-mon-stat-label">FPS</div>
              <div class="v2-mon-stat-value">{{ camStats[i].fps }}</div>
            </div>
          </div>
          <div class="v2-mon-stat">
            <i class="bi bi-clock-history"></i>
            <div>
              <div class="v2-mon-stat-label">가동 시간</div>
              <div class="v2-mon-stat-value v2-mon-uptime">{{ camStats[i].uptime }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 집계 통계 카드 -->
    <section class="v2-card">
      <div class="v2-card-h">
        <span><i class="bi bi-graph-up-arrow"></i> 전체 인식 성능</span>
      </div>
      <div class="v2-mon-summary-grid">
        <div class="v2-mon-summary-cell">
          <div class="v2-mon-sm-label">평균 인식률</div>
          <div class="v2-mon-sm-value v2-em-green">{{ avgRecognition }}%</div>
          <div class="v2-mon-sm-bar"><div class="v2-mon-sm-fill green" :style="{ width: avgRecognition + '%' }"></div></div>
        </div>
        <div class="v2-mon-summary-cell">
          <div class="v2-mon-sm-label">평균 신뢰도</div>
          <div class="v2-mon-sm-value v2-em-blue">{{ avgConfidence }}%</div>
          <div class="v2-mon-sm-bar"><div class="v2-mon-sm-fill blue" :style="{ width: avgConfidence + '%' }"></div></div>
        </div>
        <div class="v2-mon-summary-cell">
          <div class="v2-mon-sm-label">평균 FPS</div>
          <div class="v2-mon-sm-value v2-em-orange">{{ avgFps }}</div>
          <div class="v2-mon-sm-bar"><div class="v2-mon-sm-fill orange" :style="{ width: (avgFps / 30) * 100 + '%' }"></div></div>
        </div>
        <div class="v2-mon-summary-cell">
          <div class="v2-mon-sm-label">총 검출 차량</div>
          <div class="v2-mon-sm-value v2-em-purple">{{ totalDetected.toLocaleString() }}<small>건</small></div>
        </div>
        <div class="v2-mon-summary-cell">
          <div class="v2-mon-sm-label">중복 제거</div>
          <div class="v2-mon-sm-value v2-em-green">{{ dupRemoved }}<small>건</small></div>
        </div>
        <div class="v2-mon-summary-cell">
          <div class="v2-mon-sm-label">시스템 가동률</div>
          <div class="v2-mon-sm-value v2-em-green">{{ uptimePct }}%</div>
          <div class="v2-mon-sm-bar"><div class="v2-mon-sm-fill green" :style="{ width: uptimePct + '%' }"></div></div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDashboardData } from '@/composables/useDashboardData'

defineProps({ active: { type: Boolean, default: false } })
const {
  cameraFeeds, stats, dupRemoved, settings,
  tickCamHeartbeat, camHealth,
  mutedCameras, toggleCameraMute,
  pushNotification,
} = useDashboardData()

/* 카메라별 마지막 알람 시각 — 같은 카메라가 동일 사유로 1분 안에 중복 알림 가지 않게 디바운스 */
const lastAlertAt = new Map()  // key: `${name}|${reason}` → ts
const DEBOUNCE_MS = 60 * 1000
function maybeAlert(name, reason, msg, level = 'warning') {
  if (mutedCameras.value.has(name)) return
  const key = `${name}|${reason}`
  const last = lastAlertAt.get(key) || 0
  if (Date.now() - last < DEBOUNCE_MS) return
  lastAlertAt.set(key, Date.now())
  pushNotification(msg, level)
}

/* 매초 갱신되는 "now" — heartbeat 초 표시 + 카메라 상태가 실시간 변경되도록 */
const nowMs = ref(Date.now())
function camLabel(i) {
  return cameraFeeds[i]?.name || ''
}
function health(i) {
  return camHealth(camLabel(i), nowMs.value)
}
function isMuted(i) {
  return mutedCameras.value.has(camLabel(i))
}

const camStats = ref(cameraFeeds.map(() => ({
  recognition: 88 + Math.round(Math.random() * 10),
  detected:    200 + Math.round(Math.random() * 200),
  fps:         27 + Math.round(Math.random() * 4),
  confidence:  85 + Math.round(Math.random() * 12),
  uptime:      `${12 + Math.floor(Math.random() * 8)}시간 ${Math.floor(Math.random() * 60)}분`,
})))

const avgRecognition = computed(() => Math.round(camStats.value.reduce((s, c) => s + c.recognition, 0) / camStats.value.length))
const avgConfidence  = computed(() => Math.round(camStats.value.reduce((s, c) => s + c.confidence,  0) / camStats.value.length))
const avgFps         = computed(() => Math.round(camStats.value.reduce((s, c) => s + c.fps,         0) / camStats.value.length))
const totalDetected  = computed(() => camStats.value.reduce((s, c) => s + c.detected, 0))
const uptimePct      = computed(() => Math.round((stats.value.online / cameraFeeds.length) * 100))

/* 작은 범위로 흔들리는 실시간 업데이트 + 임계값 검사 + heartbeat tick */
const clamp = (v, min, max) => Math.max(min, Math.min(max, v))
function tickRealtime() {
  camStats.value = camStats.value.map((c, i) => {
    const next = {
      recognition: clamp(c.recognition + Math.round((Math.random() - 0.5) * 3), 60, 99),
      detected:    c.detected + Math.round(Math.random() * 5),
      fps:         clamp(c.fps + Math.round((Math.random() - 0.5) * 2), 10, 31),
      confidence:  clamp(c.confidence + Math.round((Math.random() - 0.5) * 4), 60, 99),
      uptime:      c.uptime,
    }
    /* 임계값 검사 — 위반 시 알람 (디바운스 적용) */
    const name = camLabel(i)
    if (next.recognition < settings.thresholdRecognition) {
      maybeAlert(name, 'recognition',
        `${name} 인식률 저하 (${next.recognition}%, 임계 ${settings.thresholdRecognition}% 미만)`,
        next.recognition < 50 ? 'critical' : 'warning')
    }
    if (next.fps < settings.thresholdFps) {
      maybeAlert(name, 'fps',
        `${name} FPS 저하 (${next.fps}, 임계 ${settings.thresholdFps} 미만)`,
        'warning')
    }
    return next
  })

  /* heartbeat 한 틱 + 끊김/오프라인 검사 */
  tickCamHeartbeat()
  cameraFeeds.forEach((cam) => {
    const h = camHealth(cam.name)
    if (h.status === 'offline') {
      maybeAlert(cam.name, 'offline',
        `${cam.name} 연결 끊김 (${h.sec}초간 프레임 미수신)`,
        'critical')
    } else if (h.status === 'warn') {
      maybeAlert(cam.name, 'warn',
        `${cam.name} 프레임 수신 지연 (${h.sec}초)`,
        'warning')
    }
  })
}

/* 새로고침 버튼 — 완전히 새 값으로 리셋 */
function refreshAll() {
  camStats.value = cameraFeeds.map(() => ({
    recognition: 88 + Math.round(Math.random() * 10),
    detected:    200 + Math.round(Math.random() * 200),
    fps:         27 + Math.round(Math.random() * 4),
    confidence:  85 + Math.round(Math.random() * 12),
    uptime:      `${12 + Math.floor(Math.random() * 8)}시간 ${Math.floor(Math.random() * 60)}분`,
  }))
}

function onCamLoaded(e) {
  try { e.target.playbackRate = 0.85 } catch {}
}

let realtimeT = null
let nowT = null
onMounted(() => {
  realtimeT = setInterval(tickRealtime, 2000)
  nowT = setInterval(() => { nowMs.value = Date.now() }, 1000)
})
onUnmounted(() => {
  clearInterval(realtimeT)
  clearInterval(nowT)
})
</script>

<style scoped>
.v2-mon-summary {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 12px; color: rgba(228,238,255,.75);
  padding: 6px 12px; background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.06); border-radius: 20px;
}
.v2-mon-summary i { color: #4caf7d; }
.v2-mon-summary b   { color: #e4eeff; font-weight: 700; }
.v2-mon-summary .v2-em { color: #60a5fa; }
.v2-sep { color: rgba(228,238,255,.2); margin: 0 2px; }

.v2-mon-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.v2-mon-cell {
  background: #0f1d30;
  border: 1px solid rgba(255,255,255,.05);
  border-radius: 8px;
  overflow: hidden;
  display: flex; flex-direction: column;
}

.v2-mon-top {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,.05);
  font-size: 12px;
}
.v2-mon-dot {
  width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
}
.v2-mon-dot.online  { background: #4caf7d; box-shadow: 0 0 6px #4caf7d; animation: pulse 1.6s ease-in-out infinite; }
.v2-mon-dot.warn    { background: #d4845a; box-shadow: 0 0 6px #d4845a; animation: pulse 1s ease-in-out infinite; }
.v2-mon-dot.offline { background: #e05260; box-shadow: 0 0 6px #e05260; }
@keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: .35 } }
.v2-mon-name { color: #e4eeff; font-weight: 600; flex: 1; }
.v2-mon-id   { font-size: 10px; color: rgba(228,238,255,.45); }

.v2-mon-hb {
  font-size: 9.5px; font-weight: 600;
  padding: 2px 6px; border-radius: 3px;
  display: inline-flex; align-items: center; gap: 3px;
  background: rgba(76,175,125,.12);
  color: #4caf7d; border: 1px solid rgba(76,175,125,.3);
}
.v2-mon-hb.warn    { background: rgba(212,132,90,.15); color: #d4845a; border-color: rgba(212,132,90,.35); }
.v2-mon-hb.offline { background: rgba(224,82,96,.18); color: #e05260; border-color: rgba(224,82,96,.4); animation: pulse 1s ease-in-out infinite; }

.v2-mon-mute {
  background: transparent; border: 1px solid rgba(255,255,255,.08);
  color: rgba(228,238,255,.5); width: 22px; height: 22px;
  border-radius: 4px; cursor: pointer; padding: 0;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 10px; transition: all .15s;
}
.v2-mon-mute:hover { color: #e4eeff; border-color: rgba(255,255,255,.2); }
.v2-mon-mute.on { background: rgba(212,132,90,.18); color: #d4845a; border-color: rgba(212,132,90,.4); }

.v2-mon-badge {
  font-size: 9px; font-weight: 800; color: #fff;
  padding: 2px 6px; border-radius: 3px; letter-spacing: .5px;
}
.v2-mon-badge.online  { background: #e05260; }
.v2-mon-badge.warn    { background: #d4845a; }
.v2-mon-badge.offline { background: #6b7280; }

.v2-mon-cell.v2-mon-warn    { box-shadow: 0 0 0 1px rgba(212,132,90,.4); }
.v2-mon-cell.v2-mon-offline { box-shadow: 0 0 0 1px rgba(224,82,96,.5); opacity: .85; }

.v2-mon-video-wrap {
  position: relative;
  aspect-ratio: 16 / 9;
  background: #000;
}
.v2-mon-video {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  object-fit: cover; display: block;
}
.v2-mon-overlay {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 8px 10px;
  background: linear-gradient(transparent, rgba(0,0,0,.75));
}
.v2-mon-conf-row {
  display: flex; align-items: center; gap: 8px;
  font-size: 10px; color: rgba(255,255,255,.85);
}
.v2-mon-conf-row b { color: #4caf7d; font-size: 11px; }
.v2-mon-conf-bar {
  flex: 1; height: 4px; background: rgba(255,255,255,.15); border-radius: 2px; overflow: hidden;
}
.v2-mon-conf-fill {
  height: 100%; background: linear-gradient(90deg, #f0934e, #4caf7d); border-radius: 2px;
  transition: width .4s;
}

.v2-mon-stats {
  display: grid; grid-template-columns: repeat(2, 1fr);
  gap: 1px;
  background: rgba(255,255,255,.04);
}
.v2-mon-stat {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px;
  background: #0f1d30;
}
.v2-mon-stat > i {
  font-size: 16px; color: #60a5fa;
  width: 22px; text-align: center;
}
.v2-mon-stat-label { font-size: 10px; color: rgba(228,238,255,.5); }
.v2-mon-stat-value {
  font-size: 16px; font-weight: 700; color: #e4eeff;
  line-height: 1.1; margin-top: 1px;
}
.v2-mon-stat-value small {
  font-size: 11px; font-weight: 500; color: rgba(228,238,255,.55); margin-left: 2px;
}
.v2-mon-uptime { font-size: 12px !important; font-weight: 600 !important; }

.v2-mon-summary-grid {
  display: grid; grid-template-columns: repeat(6, 1fr);
  gap: 14px;
}
.v2-mon-summary-cell {
  background: #0b1726;
  border: 1px solid rgba(255,255,255,.04);
  border-radius: 6px;
  padding: 14px 16px;
}
.v2-mon-sm-label { font-size: 11px; color: rgba(228,238,255,.55); margin-bottom: 6px; }
.v2-mon-sm-value {
  font-size: 22px; font-weight: 800; line-height: 1.1;
}
.v2-mon-sm-value small { font-size: 12px; font-weight: 500; color: rgba(228,238,255,.55); margin-left: 2px; }
.v2-mon-sm-bar {
  height: 4px; background: rgba(255,255,255,.06); border-radius: 2px; overflow: hidden;
  margin-top: 10px;
}
.v2-mon-sm-fill { height: 100%; border-radius: 2px; transition: width .4s; }
.v2-mon-sm-fill.green  { background: linear-gradient(90deg, #4caf7d, #6fde9f); }
.v2-mon-sm-fill.blue   { background: linear-gradient(90deg, #60a5fa, #93c5fd); }
.v2-mon-sm-fill.orange { background: linear-gradient(90deg, #d4845a, #f0934e); }
.v2-em-green  { color: #4caf7d; }
.v2-em-blue   { color: #60a5fa; }
.v2-em-orange { color: #d4845a; }
.v2-em-purple { color: #a78bfa; }

@media (max-width: 1400px) {
  .v2-mon-grid { grid-template-columns: repeat(2, 1fr); }
  .v2-mon-summary-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 900px) {
  .v2-mon-grid { grid-template-columns: 1fr; }
  .v2-mon-summary-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
