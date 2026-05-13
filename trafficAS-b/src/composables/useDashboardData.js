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
})

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
/* 외부에서 호출 — 카메라 혼잡도 한 틱 갱신 */
function tickCamCongestion() {
  const next = { ...camCongestion.value }
  for (const k in next) {
    next[k] = Math.max(0.05, Math.min(0.99, next[k] + (Math.random() - 0.5) * 0.15))
  }
  camCongestion.value = next
}

export function useDashboardData() {
  return {
    totalVehicles, inCount, outCount, dupRemoved,
    plates, cameraFeeds, cameraGroups, settings,
    todayStr, dirLabel, levelLabel, plateImg, plateStatus,
    totalCamCount, stats,
    camCongestion, tickCamCongestion,
  }
}
