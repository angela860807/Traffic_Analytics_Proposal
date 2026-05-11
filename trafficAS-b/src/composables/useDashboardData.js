import { ref, reactive, computed } from 'vue'

/* ──────── 차량 통행(진입/이탈) KPI ──────── */
const totalVehicles = ref(2475)
const inCount       = ref(1284)
const outCount      = ref(1191)
const dupRemoved    = ref(178)

/* ──────── OCR 번호판 데이터 ──────── */
const plates = ref([
  { id: 1, num: '128가 4567', cam: '테헤란로 교차로', time: '14:32:18', conf: 95, dir: 'in'  },
  { id: 2, num: '52라 3108',  cam: '역삼역 사거리',   time: '14:32:17', conf: 92, dir: 'out' },
  { id: 3, num: '33다 5678',  cam: '강남역 사거리',   time: '14:32:16', conf: 94, dir: 'in'  },
  { id: 4, num: '11나 2222',  cam: '선릉역 사거리',   time: '14:32:15', conf: 91, dir: 'out' },
  { id: 5, num: '45무 6789',  cam: '교대역 사거리',   time: '14:32:14', conf: 96, dir: 'in'  },
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
    { name: '테헤란로 교차로',  status: 'online',  lastSeen: '2024-05-28 14:32:21' },
    { name: '역삼역 사거리',    status: 'online',  lastSeen: '2024-05-28 14:32:20' },
    { name: '강남역 사거리',    status: 'online',  lastSeen: '2024-05-28 14:32:22' },
    { name: '선릉역 사거리',    status: 'offline', lastSeen: '' },
    { name: '논현역 사거리',    status: 'online',  lastSeen: '2024-05-28 14:32:18' },
    { name: '신논현역 사거리',  status: 'online',  lastSeen: '2024-05-28 14:32:17' },
    { name: '학동역 사거리',    status: 'online',  lastSeen: '2024-05-28 14:32:16' },
    { name: '청담역 사거리',    status: 'online',  lastSeen: '2024-05-28 14:32:15' },
  ]},
  { region: '서초구', expanded: true, cams: [
    { name: '교대역 사거리',     status: 'online',  lastSeen: '2024-05-28 14:32:19' },
    { name: '서초역 사거리',     status: 'online',  lastSeen: '2024-05-28 14:32:18' },
    { name: '남부터미널 사거리', status: 'online',  lastSeen: '2024-05-28 14:32:17' },
    { name: '양재역 사거리',     status: 'online',  lastSeen: '2024-05-28 14:32:16' },
    { name: '방배역 사거리',     status: 'online',  lastSeen: '2024-05-28 14:32:15' },
    { name: '내방역 사거리',     status: 'error',   lastSeen: '2024-05-28 13:58:02' },
    { name: '잠원동 사거리',     status: 'online',  lastSeen: '2024-05-28 14:32:14' },
    { name: '반포역 사거리',     status: 'online',  lastSeen: '2024-05-28 14:32:13' },
  ]},
  { region: '송파구', expanded: true, cams: [
    { name: '잠실역 사거리',     status: 'online', lastSeen: '2024-05-28 14:32:12' },
    { name: '잠실나루역 사거리', status: 'online', lastSeen: '2024-05-28 14:32:11' },
    { name: '올림픽공원 사거리', status: 'online', lastSeen: '2024-05-28 14:32:10' },
    { name: '석촌역 사거리',     status: 'online', lastSeen: '2024-05-28 14:32:09' },
    { name: '송파역 사거리',     status: 'online', lastSeen: '2024-05-28 14:32:08' },
    { name: '가락시장 사거리',   status: 'online', lastSeen: '2024-05-28 14:32:07' },
    { name: '문정역 사거리',     status: 'online', lastSeen: '2024-05-28 14:32:06' },
    { name: '장지역 사거리',     status: 'online', lastSeen: '2024-05-28 14:32:05' },
  ]},
])

/* ──────── 설정값 ──────── */
const settings = reactive({
  notifyCritical: true, notifyWarning: true, notifyInfo: false, notifyEmail: false,
  congestionThreshold: 80, ocrConfidence: 85, refreshInterval: 3,
  dedupSeconds: 10, dedupDirSplit: true, wsEnabled: true,
})

const todayStr = '2024-05-28'

/* ──────── 헬퍼 ──────── */
function dirLabel(d) { return d === 'in' ? '진입' : d === 'out' ? '이탈' : '-' }
function levelLabel(lv) { return lv === 'critical' ? '중요' : lv === 'warning' ? '경고' : '정보' }

/* ──────── 파생값 ──────── */
const totalCamCount = computed(() => cameraGroups.reduce((s, g) => s + g.cams.length, 0))
const allCams       = computed(() => cameraGroups.flatMap(g => g.cams))
const stats         = computed(() => ({
  online:  allCams.value.filter(c => c.status === 'online').length,
  offline: allCams.value.filter(c => c.status === 'offline').length,
  error:   allCams.value.filter(c => c.status === 'error').length,
}))

export function useDashboardData() {
  return {
    totalVehicles, inCount, outCount, dupRemoved,
    plates, cameraFeeds, cameraGroups, settings,
    todayStr, dirLabel, levelLabel,
    totalCamCount, stats,
  }
}
