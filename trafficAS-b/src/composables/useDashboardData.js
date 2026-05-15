import { ref, reactive, computed } from 'vue'

/* ──────── 오늘 날짜(yyyy-MM-dd, 로컬) ──────── */
const _d = new Date()
const _p = n => String(n).padStart(2, '0')
const todayStr = `${_d.getFullYear()}-${_p(_d.getMonth() + 1)}-${_p(_d.getDate())}`

/* ──────── 차량 통행(진입/이탈) KPI ──────── */
const totalVehicles = ref(2475)
const inCount       = ref(1284)
const outCount      = ref(1191)
const dupRemoved    = ref(178)

/* ──────── OCR 번호판 데이터 ──────── */
const plates = ref([
  { id: 1, num: '128가 4567', cam: '테헤란로 교차로', date: todayStr, time: '14:32:18', conf: 95, dir: 'in',  status: 'FLOW_EVENT_CREATED' },
  { id: 2, num: '52라 3108',  cam: '역삼역 사거리',   date: todayStr, time: '14:32:17', conf: 92, dir: 'out', status: 'FLOW_EVENT_CREATED' },
  { id: 3, num: '미인식',     cam: '강남역 사거리',   date: todayStr, time: '14:32:16', conf: 48, dir: 'in',  status: 'OCR_FAILED' },
  { id: 4, num: '11나 2222',  cam: '선릉역 사거리',   date: todayStr, time: '14:32:15', conf: 91, dir: 'out', status: 'DUPLICATE_SKIPPED' },
  { id: 5, num: '45무 6789',  cam: '교대역 사거리',   date: todayStr, time: '14:32:14', conf: 96, dir: 'in',  status: 'FLOW_EVENT_CREATED' },
])

/* ──────── 카메라 피드(메인 6분할) ──────── */
const cameraFeeds = reactive([
  { name: '테헤란로 교차로', src: '/road7.mp4', online: true },
  { name: '역삼역 사거리',   src: '/road2.mp4', online: true },
  { name: '강남역 사거리',   src: '/road8.mp4', online: true },
  { name: '선릉역 사거리',   src: '/road4.mp4', online: true },
  { name: '교대역 사거리',   src: '/road5.mp4', online: true },
  { name: '잠실역 사거리',   src: '/road6.mp4', online: true },
])

/* ──────── 카메라 그룹(좌측 트리) ──────── */
const cameraGroups = reactive([
  { region: '강남구', expanded: true, cams: [
    { name: '테헤란로 교차로',  status: 'online',  lastSeen: `${todayStr} 14:32:21`, coords: [37.4979, 127.0276] },
    { name: '역삼역 사거리',    status: 'online',  lastSeen: `${todayStr} 14:32:20`, coords: [37.5005, 127.0364] },
    { name: '강남역 사거리',    status: 'online',  lastSeen: `${todayStr} 14:32:22`, coords: [37.4979, 127.0276] },
    { name: '선릉역 사거리',    status: 'offline', lastSeen: '',                     coords: [37.5044, 127.0489] },
    { name: '논현역 사거리',    status: 'online',  lastSeen: `${todayStr} 14:32:18`, coords: [37.5113, 127.0214] },
    { name: '신논현역 사거리',  status: 'online',  lastSeen: `${todayStr} 14:32:17`, coords: [37.5044, 127.0250] },
    { name: '학동역 사거리',    status: 'online',  lastSeen: `${todayStr} 14:32:16`, coords: [37.5145, 127.0340] },
    { name: '청담역 사거리',    status: 'online',  lastSeen: `${todayStr} 14:32:15`, coords: [37.5198, 127.0468] },
  ]},
  { region: '서초구', expanded: true, cams: [
    { name: '교대역 사거리',     status: 'online',  lastSeen: `${todayStr} 14:32:19`, coords: [37.4923, 127.0140] },
    { name: '서초역 사거리',     status: 'online',  lastSeen: `${todayStr} 14:32:18`, coords: [37.4837, 127.0079] },
    { name: '남부터미널 사거리', status: 'online',  lastSeen: `${todayStr} 14:32:17`, coords: [37.4848, 127.0162] },
    { name: '양재역 사거리',     status: 'online',  lastSeen: `${todayStr} 14:32:16`, coords: [37.4842, 127.0344] },
    { name: '방배역 사거리',     status: 'online',  lastSeen: `${todayStr} 14:32:15`, coords: [37.4810, 126.9974] },
    { name: '내방역 사거리',     status: 'error',   lastSeen: `${todayStr} 13:58:02`, coords: [37.4872, 126.9938] },
    { name: '잠원동 사거리',     status: 'online',  lastSeen: `${todayStr} 14:32:14`, coords: [37.5168, 127.0125] },
    { name: '반포역 사거리',     status: 'online',  lastSeen: `${todayStr} 14:32:13`, coords: [37.5093, 127.0123] },
  ]},
  { region: '송파구', expanded: true, cams: [
    { name: '잠실역 사거리',     status: 'online', lastSeen: `${todayStr} 14:32:12`, coords: [37.5135, 127.1000] },
    { name: '잠실나루역 사거리', status: 'online', lastSeen: `${todayStr} 14:32:11`, coords: [37.5202, 127.1023] },
    { name: '올림픽공원 사거리', status: 'online', lastSeen: `${todayStr} 14:32:10`, coords: [37.5159, 127.1296] },
    { name: '석촌역 사거리',     status: 'online', lastSeen: `${todayStr} 14:32:09`, coords: [37.5005, 127.1063] },
    { name: '송파역 사거리',     status: 'online', lastSeen: `${todayStr} 14:32:08`, coords: [37.4988, 127.1118] },
    { name: '가락시장 사거리',   status: 'online', lastSeen: `${todayStr} 14:32:07`, coords: [37.4925, 127.1180] },
    { name: '문정역 사거리',     status: 'online', lastSeen: `${todayStr} 14:32:06`, coords: [37.4854, 127.1235] },
    { name: '장지역 사거리',     status: 'online', lastSeen: `${todayStr} 14:32:05`, coords: [37.4785, 127.1262] },
  ]},
])

/* ──────── 설정값 ──────── */
const settings = reactive({
  notifyCritical: true, notifyWarning: true, notifyInfo: false, notifyEmail: false,
  congestionThreshold: 80, ocrConfidence: 85, refreshInterval: 3,
  dedupSeconds: 10, dedupDirSplit: true, wsEnabled: true,
  /* 관제 임계값 — MonitoringTab이 이 값으로 카메라 상태 검사 */
  thresholdRecognition: 70,     // 인식률(%) 이하 시 경고 알림
  thresholdFps: 15,             // FPS 이하 시 경고 알림
  thresholdHeartbeatSec: 10,    // 마지막 프레임 N초 초과 시 끊김 경고
  thresholdHeartbeatOfflineSec: 30, // 30초 초과 시 오프라인
})

/* ──────── 알림(헤더 종) — 모든 컴포넌트가 공유 ──────── */
const notifications = ref([
  { id: 1,  msg: '테헤란로 교차로 혼잡 감지 — 진입 +42%', time: '14:32', color: '#e05260' },
  { id: 2,  msg: 'CAM-03 강남역 OCR 인식률 저하 (78%)', time: '14:28', color: '#d4845a' },
  { id: 3,  msg: '반포IC 이탈 차량 급증', time: '14:15', color: '#d4845a' },
  { id: 4,  msg: '올림픽대로 흐름 원활 전환', time: '13:58', color: '#4caf7d' },
  { id: 5,  msg: 'OCR 파이프라인 정상 가동', time: '13:45', color: '#4caf7d' },
  { id: 6,  msg: '잠실역 사거리 진입 트래픽 급증', time: '13:30', color: '#d4845a' },
  { id: 7,  msg: '양재역 사거리 흐름 정상화', time: '13:02', color: '#4caf7d' },
  { id: 8,  msg: '남부터미널 정체 시작 — 평균 12 km/h', time: '12:36', color: '#e05260' },
  { id: 9,  msg: '석촌역 이탈 차량 통행 증가', time: '12:14', color: '#d4845a' },
  { id: 10, msg: '강남구 전역 평균 정상', time: '11:55', color: '#4caf7d' },
  { id: 11, msg: '중복 감지 178건 자동 제거 완료', time: '11:30', color: '#4caf7d' },
  { id: 12, msg: 'WebSocket 연결 정상', time: '11:00', color: '#4caf7d' },
])
function pushNotification(msg, level = 'warning') {
  const now = new Date()
  const time = `${_p(now.getHours())}:${_p(now.getMinutes())}`
  const color = level === 'critical' ? '#e05260' : level === 'warning' ? '#d4845a' : '#4caf7d'
  notifications.value.unshift({ id: Date.now() + Math.random(), msg, time, color })
  if (notifications.value.length > 50) notifications.value.length = 50
}

/* ──────── 헬퍼 ──────── */
function dirLabel(d) { return d === 'in' ? '진입' : d === 'out' ? '이탈' : '-' }
function levelLabel(lv) { return lv === 'critical' ? '중요' : lv === 'warning' ? '경고' : '정보' }
function plateImg(p) {
  if (!p) return ''
  /* 우선순위: crop(plateCropImageUrl) → 원본(imageUrl) → 데모 폴백
     PROD에선 데이터 없을 때 빈 문자열 반환 (가짜 이미지 노출 방지) */
  return p.plateCropImageUrl
      || p.cropUrl
      || p.imageUrl
      || (import.meta.env.DEV ? '/car1.jpg' : '')
}
function plateStatus(s) {
  if (s === 'OCR_FAILED')        return { label: '실패', cls: 'fail', icon: 'bi bi-x-circle-fill' }
  if (s === 'DUPLICATE_SKIPPED') return { label: '중복', cls: 'dup',  icon: 'bi bi-arrow-repeat' }
  return                                { label: '정상', cls: 'ok',   icon: 'bi bi-check-circle-fill' }
}

/* ──────── 파생값 ──────── */
const totalCamCount = computed(() => cameraGroups.reduce((s, g) => s + g.cams.length, 0))
const allCams       = computed(() => cameraGroups.flatMap(g => g.cams))
const stats         = computed(() => ({
  online:  allCams.value.filter(c => c.status === 'online').length,
  offline: allCams.value.filter(c => c.status === 'offline').length,
  error:   allCams.value.filter(c => c.status === 'error').length,
}))

/* 카메라별 혼잡도(0~1) — 초기값 랜덤 + dataT 인터벌이 ±15%로 흔듦 */
const camCongestion = ref(
  Object.fromEntries(
    cameraGroups.flatMap(g => g.cams).map(c => [c.name, 0.3 + Math.random() * 0.6])
  )
)
function tickCamCongestion() {
  const next = { ...camCongestion.value }
  for (const k in next) {
    next[k] = Math.max(0.05, Math.min(0.99, next[k] + (Math.random() - 0.5) * 0.15))
  }
  camCongestion.value = next
}

/* ──────── 카메라 heartbeat — 마지막 프레임 수신 시각(ms) ──────── */
const _allCamNames = [...new Set([...cameraFeeds.map(c => c.name), ...cameraGroups.flatMap(g => g.cams.map(c => c.name))])]
const camHeartbeat = ref(Object.fromEntries(_allCamNames.map(n => [n, Date.now()])))
/* 알람 음소거된 카메라 이름들 — 점검 중일 때 알람 안 옴 */
const mutedCameras = ref(new Set())

/* 외부에서 호출 — heartbeat 한 틱
 * 대부분(95%)은 alive로 갱신, 5% 확률로 미갱신(끊김 시뮬레이션) */
function tickCamHeartbeat() {
  const next = { ...camHeartbeat.value }
  const now = Date.now()
  _allCamNames.forEach(name => {
    if (Math.random() < 0.95) next[name] = now
  })
  camHeartbeat.value = next
}

/* 카메라 현재 상태 계산 — settings.threshold* 임계값 기준 */
function camHealth(name, nowMs = Date.now()) {
  const last = camHeartbeat.value[name]
  if (!last) return { status: 'unknown', sec: 999 }
  const sec = Math.floor((nowMs - last) / 1000)
  if (sec >= settings.thresholdHeartbeatOfflineSec) return { status: 'offline', sec }
  if (sec >= settings.thresholdHeartbeatSec)        return { status: 'warn',    sec }
  return { status: 'online', sec }
}

function toggleCameraMute(name) {
  const next = new Set(mutedCameras.value)
  if (next.has(name)) next.delete(name); else next.add(name)
  mutedCameras.value = next
}

export function useDashboardData() {
  return {
    totalVehicles, inCount, outCount, dupRemoved,
    plates, cameraFeeds, cameraGroups, settings,
    todayStr, dirLabel, levelLabel, plateImg, plateStatus,
    totalCamCount, stats,
    camCongestion, tickCamCongestion,
    /* 알림 */
    notifications, pushNotification,
    /* heartbeat / 임계값 / 음소거 */
    camHeartbeat, tickCamHeartbeat, camHealth, mutedCameras, toggleCameraMute,
  }
}
