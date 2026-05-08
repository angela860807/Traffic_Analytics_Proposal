<template>
  <div class="theme-navy" :class="{ light: !isDark }">
    <AppNav />
    <AppFab />

    <div class="dash-shell">
      <!-- ══ TAB BAR ══ -->
      <nav class="tabbar">
        <div class="tab-inner">
          <button v-for="tab in TABS" :key="tab.id" class="tab-btn" :class="{ active: activeTab === tab.id }" @click="activeTab = tab.id">
            <component :is="tab.icon" class="tab-icon" />
            {{ tab.label }}
            <span v-if="tab.id === 'alerts' && alerts.length" class="tab-badge">{{ alerts.length }}</span>
          </button>
        </div>
        <div class="tab-right">
          <span class="tab-ws mono" :class="wsConnected ? 'ok' : 'err'">● {{ wsConnected ? 'WS 연결됨' : 'WS 대기 중' }}</span>
          <span class="tab-clock mono">{{ timeStr }}</span>
          <span class="tab-live"><span class="live-dot"></span>LIVE</span>
        </div>
      </nav>

      <div class="dash-body">
        <div v-show="activeTab === 'overview'" class="tab-content overview-layout">
          <OverviewTab :segments="segments" :kpis="kpis" @open-fullscreen="openFullscreen" />
        </div>

        <div v-show="activeTab === 'plates'" class="tab-content">
          <PlatesTab :plates="plates" :flow-in="flowIn" :flow-out="flowOut" />
        </div>
        <div v-show="activeTab === 'events'" class="tab-content">
          <EventsTab :incidents="incidents" />
        </div>
        <div v-show="activeTab === 'stats'" class="tab-content">
          <StatsTab :heat-zones="heatZones" :flow-in="flowIn" :flow-out="flowOut" :segments="segments" :acc-cnt="accCnt" :chart-data="chartData" />
        </div>
        <div v-show="activeTab === 'alerts'" class="tab-content">
          <AlertsTab :alerts="alerts" :thresholds="thresholds" @dismiss="dismissAlert" />
        </div>
      </div>

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

    <!-- ══ 풀스크린 모달 ══ -->
    <Teleport to="body">
      <div v-if="fullscreenSeg" class="fs-overlay" @click.self="closeFullscreen">
        <div class="fs-modal">
          <div class="fs-header">
            <div class="fs-title">{{ fullscreenSeg.name }}</div>
            <div class="fs-badge" :class="'lv-'+fullscreenSeg.lv">
              {{ fullscreenSeg.lv === 'H' ? '혼잡' : fullscreenSeg.lv === 'M' ? '지체' : '원활' }}
            </div>
            <div class="mono fs-spd" :style="{ color: levelColor(fullscreenSeg.lv) }">{{ Math.round(fullscreenSeg.spd) }} km/h</div>
            <button class="fs-close" @click="closeFullscreen">✕</button>
          </div>
          <div class="fs-body">
            <video v-if="fullscreenSeg.videoUrl" class="fs-video" :src="fullscreenSeg.videoUrl" autoplay muted loop playsinline></video>
            <canvas v-else class="fs-canvas"></canvas>
            <div class="fs-speed-overlay">
              <span class="mono" :style="{ fontSize:'32px', fontWeight:'700', color: levelColor(fullscreenSeg.lv) }">{{ Math.round(fullscreenSeg.spd) }}</span>
              <span style="font-size:13px;color:var(--t3)">km/h</span>
            </div>
          </div>
          <div class="fs-footer">
            <div class="fs-stat" v-for="s in fsStats" :key="s.label">
              <div class="mono fs-sv" :style="{ color: s.color || 'var(--t)' }">{{ s.value }}</div>
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
          <div v-for="n in notifQueue" :key="n.id" class="notif" :class="'notif-'+n.lv">
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
import { ref, reactive, computed, onMounted, onUnmounted, h, watch } from 'vue'
import AppNav      from '@/components/AppNav.vue'
import AppFab      from '@/components/AppFab.vue'
import OverviewTab from '@/components/dashboard/OverviewTab.vue'

import PlatesTab   from '@/components/dashboard/PlatesTab.vue'
import EventsTab   from '@/components/dashboard/EventsTab.vue'
import StatsTab    from '@/components/dashboard/StatsTab.vue'
import AlertsTab   from '@/components/dashboard/AlertsTab.vue'
import { useTheme } from '@/composables/useTheme'
import { levelColor } from '@/utils/levelColor'
import { apiGet } from '@/api/client'

const { isDark } = useTheme()

/* ── 탭 아이콘 ── */
const mk = (d) => ({ render: () => h('svg', { viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':'1.8' }, d) })
const GridIcon  = mk([h('rect',{x:'3',y:'3',width:'7',height:'7'}),h('rect',{x:'14',y:'3',width:'7',height:'7'}),h('rect',{x:'14',y:'14',width:'7',height:'7'}),h('rect',{x:'3',y:'14',width:'7',height:'7'})])

const PlateIcon = mk([h('rect',{x:'2',y:'6',width:'20',height:'12',rx:'2'}),h('line',{x1:'6',y1:'10',x2:'6',y2:'14'}),h('line',{x1:'10',y1:'10',x2:'10',y2:'14'}),h('line',{x1:'14',y1:'10',x2:'14',y2:'14'}),h('line',{x1:'18',y1:'10',x2:'18',y2:'14'})])
const AlertIcon = mk([h('path',{d:'M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z'}),h('line',{x1:'12',y1:'9',x2:'12',y2:'13'}),h('line',{x1:'12',y1:'17',x2:'12.01',y2:'17'})])
const ChartIcon = mk([h('line',{x1:'18',y1:'20',x2:'18',y2:'10'}),h('line',{x1:'12',y1:'20',x2:'12',y2:'4'}),h('line',{x1:'6',y1:'20',x2:'6',y2:'14'})])
const BellIcon  = mk([h('path',{d:'M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9'}),h('path',{d:'M13.73 21a2 2 0 01-3.46 0'})])

const TABS = [
  { id: 'overview', label: '도로 현황',   icon: GridIcon  },

  { id: 'plates',   label: '번호판 인식', icon: PlateIcon },
  { id: 'events',   label: '이벤트 로그', icon: AlertIcon },
  { id: 'stats',    label: '통계 분석',   icon: ChartIcon },
  { id: 'alerts',   label: '알림',        icon: BellIcon  },
]
const activeTab = ref('overview')

/* ── WebSocket ── */
const wsConnected = ref(false)
let ws = null, wsRetry = null

function connectWS() {
  if (wsRetry) { clearTimeout(wsRetry); wsRetry = null }
  try {
    ws = new WebSocket('ws://localhost:8000/ws')
    ws.onopen  = () => { wsConnected.value = true }
    ws.onclose = () => { wsConnected.value = false; wsRetry = setTimeout(connectWS, 10000) }
    ws.onerror = () => { wsConnected.value = false }
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        if (data.road) {
          const seg = segments.find(s => s.name.includes(data.road))
          if (seg) { seg.spd = data.speed??seg.spd; seg.cnt = data.count??seg.cnt; seg.lv = data.lv??seg.lv }
        }
        if (data.plate) {
          plates.value = [{ id: Date.now(), num: data.plate, dir: data.dir||'IN', cam: data.cam||'CAM', time: new Date().toTimeString().slice(0,5), conf: data.conf||95 }, ...plates.value].slice(0,20)
        }
      } catch {}
    }
  } catch { wsRetry = setTimeout(connectWS, 10000) }
}

/* ── 상태 ── */
const timeStr  = ref('')
const totalV   = ref(1248), avgSpd = ref(31), cIdx = ref(68)
const flowIn   = ref(842),  flowOut = ref(406), accCnt = ref(2)
const flowCountsConnected = ref(false)
const cameraListConnected = ref(false)
const hourlyStatsConnected = ref(false)
const FLOW_ZONE_ID = Number(import.meta.env.VITE_DEFAULT_ZONE_ID || 1)

const kpis = computed(() => [
  { label:'감지 차량', value: totalV.value.toLocaleString(), unit:'대',    color:'var(--a)',      type:'bar', pct: Math.min(Math.round((totalV.value/2000)*100),100) },
  { label:'평균 속도', value: avgSpd.value,                  unit:'km/h',  type:'arc',
    color: avgSpd.value<20?'var(--danger)':avgSpd.value<40?'var(--warn)':'var(--ok)',
    pct: Math.min(Math.round((avgSpd.value/100)*100),100) },
  { label:'입차',      value: flowIn.value.toLocaleString(),  unit:'대/시', color:'var(--ok)',     type:'bar', pct: Math.min(Math.round((flowIn.value/1000)*100),100) },
  { label:'출차',      value: flowOut.value.toLocaleString(), unit:'대/시', color:'var(--warn)',   type:'bar', pct: Math.min(Math.round((flowOut.value/1000)*100),100) },
  { label:'혼잡지수',  value: cIdx.value,                     unit:'',      type:'arc',
    color: cIdx.value>70?'var(--danger)':cIdx.value>50?'var(--warn)':'var(--ok)', pct: cIdx.value },
  { label:'이상 감지', value: accCnt.value,                   unit:'건',    color:'var(--danger)', type:'dot', pct: Math.min(Math.round((accCnt.value/5)*100),100) },
])

const segments = reactive([
  { id:'s1', name:'강남구 테헤란로',   cam:'CAM-02', lv:'H', spd:12, cnt:287, conf:96, dir:'H', videoUrl:'/road1.mp4' },
  { id:'s2', name:'서초구 반포IC',     cam:'CAM-03', lv:'H', spd:9,  cnt:195, conf:94, dir:'H', videoUrl:'/road2.mp4' },
  { id:'s3', name:'영동대로',          cam:'CAM-05', lv:'M', spd:28, cnt:134, conf:97, dir:'V', videoUrl:'/road6.mp4' },
  { id:'s4', name:'송파구 올림픽대로', cam:'CAM-04', lv:'M', spd:35, cnt:168, conf:95, dir:'H', videoUrl:'/road5.mp4' },
])


const plates = ref([
  { id:1, num:'서울 12가 3456', dir:'IN',  cam:'CAM-02', time:'14:42', conf:97.2 },
  { id:2, num:'경기 78나 9012', dir:'OUT', cam:'CAM-03', time:'14:38', conf:95.8 },
  { id:3, num:'서울 34다 5678', dir:'IN',  cam:'CAM-02', time:'14:35', conf:98.1 },
  { id:4, num:'인천 56라 7890', dir:'IN',  cam:'CAM-04', time:'14:31', conf:94.3 },
  { id:5, num:'서울 90마 1234', dir:'OUT', cam:'CAM-05', time:'14:28', conf:96.7 },
  { id:6, num:'경기 11바 2345', dir:'IN',  cam:'CAM-06', time:'14:24', conf:97.9 },
])

async function loadDetectionLogs() {
  try {
    const body = await apiGet('/api/v1/detection-logs')
    const rows = body.data || []

    plates.value = rows.map(log => ({
      id: log.logId,
      num: log.plateNumber,
      dir: log.directionType || '-',
      cam: log.cameraName || '-',
      time: log.detectedAt ? log.detectedAt.slice(11, 16) : '-',
      conf: log.confidenceScore != null
        ? Math.round(log.confidenceScore * 1000) / 10
        : 0,
      imagePath: log.imagePath || '',
      imageUrl: log.imageUrl || '',
    }))
  } catch (error) {
    console.warn('Failed to load detection logs', error)
  }
}

function toLocalDateParam(date) {
  const pad = (value) => String(value).padStart(2, '0')
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
  ].join('-')
}

function toLocalDateTimeParam(date) {
  const pad = (value) => String(value).padStart(2, '0')
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
  ].join('-') + 'T' + [
    pad(date.getHours()),
    pad(date.getMinutes()),
    pad(date.getSeconds()),
  ].join(':')
}

async function loadFlowCounts() {
  const now = new Date()
  const start = new Date(now)
  start.setHours(0, 0, 0, 0)

  const params = new URLSearchParams({
    zoneId: String(FLOW_ZONE_ID),
    start: toLocalDateTimeParam(start),
    end: toLocalDateTimeParam(now),
  })

  try {
    const [inCount, outCount] = await Promise.all([
      apiGet(`/api/flow-events/stats/count?${params.toString()}&direction=IN`),
      apiGet(`/api/flow-events/stats/count?${params.toString()}&direction=OUT`),
    ])

    flowIn.value = Number(inCount) || 0
    flowOut.value = Number(outCount) || 0
    flowCountsConnected.value = true
  } catch (error) {
    flowCountsConnected.value = false
    console.warn('Failed to load flow counts', error)
  }
}

async function loadZonesAndCameras() {
  try {
    const zones = await apiGet('/api/zones')
    if (!Array.isArray(zones) || zones.length === 0) {
      cameraListConnected.value = false
      return
    }

    heatZones.splice(0, heatZones.length, ...zones.map((zone, index) => ({
      name: zone.zoneName || zone.zoneCode || `ZONE-${zone.zoneId}`,
      pct: heatZones[index]?.pct ?? 50,
    })))

    const selectedZone = zones.find(zone => Number(zone.zoneId) === FLOW_ZONE_ID) || zones[0]
    const cameras = await apiGet(`/api/cameras?zoneId=${selectedZone.zoneId}`)
    if (!Array.isArray(cameras) || cameras.length === 0) {
      cameraListConnected.value = false
      return
    }

    cameras.slice(0, segments.length).forEach((camera, index) => {
      const segment = segments[index]
      if (!segment) return

      segment.name = camera.cameraName || camera.zoneName || camera.cameraCode || segment.name
      segment.cam = camera.cameraCode || camera.cameraName || segment.cam
      segment.dir = camera.directionType || segment.dir
      segment.conf = camera.isActive === false ? 0 : segment.conf
    })

    cameraListConnected.value = true
  } catch (error) {
    cameraListConnected.value = false
    console.warn('Failed to load zones or cameras', error)
  }
}

async function loadHourlyStats() {
  const params = new URLSearchParams({
    statDate: toLocalDateParam(new Date()),
    zoneId: String(FLOW_ZONE_ID),
  })

  try {
    const rows = await apiGet(`/api/stats/hourly?${params.toString()}`)
    if (!Array.isArray(rows) || rows.length === 0) {
      hourlyStatsConnected.value = false
      return
    }

    const totalsByHour = new Map(rows.map(row => [
      Number(row.statHour),
      Number(row.totalCount) || 0,
    ]))
    const hours = Array.from({ length: 12 }, (_, index) => index + 7)
    const values = hours.map(hour => totalsByHour.get(hour) ?? 0)

    if (!values.some(value => value > 0)) {
      hourlyStatsConnected.value = false
      return
    }

    chartData.splice(0, chartData.length, ...values)
    hourlyStatsConnected.value = true
  } catch (error) {
    hourlyStatsConnected.value = false
    console.warn('Failed to load hourly stats', error)
  }
}

const incidents = ref([
  { id:1, time:'14:38', type:'교통사고', loc:'강남구 테헤란로 119',   lv:'H' },
  { id:2, time:'14:22', type:'도로공사', loc:'서초구 반포IC 진입',    lv:'M' },
  { id:3, time:'14:05', type:'차량고장', loc:'잠실대교 남단 2차로',   lv:'M' },
  { id:4, time:'13:48', type:'신호고장', loc:'강남역 사거리',          lv:'H' },
  { id:5, time:'13:31', type:'낙하물',   loc:'올림픽대로 동방면',      lv:'L' },
])

const heatZones = reactive([
  { name:'강남·서초',   pct:88 }, { name:'송파·강동',   pct:62 },
  { name:'마포·영등포', pct:55 }, { name:'종로·중구',   pct:43 },
  { name:'노원·도봉',   pct:28 }, { name:'용산·성동',   pct:71 },
])

const chartData = reactive([4200,7800,8900,7200,6100,6800,7100,7600,8100,8500,8900,8100])

/* ── 알림 ── */
const thresholds = reactive({ congSpeed:20, slowSpeed:40 })
const alerts = reactive([
  { id:1, lv:'H', title:'테헤란로 혼잡 감지',  desc:'평균 속도 12km/h — 임계값 초과',       time:'14:38' },
  { id:2, lv:'H', title:'CAM-01 장애 감지',    desc:'강남역 사거리 카메라 응답 없음',        time:'13:48' },
  { id:3, lv:'M', title:'반포IC 서행 구간',    desc:'평균 속도 28km/h — 주의 필요',         time:'14:22' },
])
const notifQueue = reactive([])
let notifId = 100

function pushNotif(lv, title, desc) {
  const id = ++notifId
  notifQueue.push({ id, lv, title, desc })
  setTimeout(() => dismissNotif(id), 5000)
}
function dismissNotif(id) { const i = notifQueue.findIndex(n=>n.id===id); if (i>=0) notifQueue.splice(i,1) }
function dismissAlert(id)  { const i = alerts.findIndex(a=>a.id===id);    if (i>=0) alerts.splice(i,1)    }

watch(() => segments.map(s => s.spd), () => {
  segments.forEach(seg => {
    if (seg.spd < thresholds.congSpeed) {
      const exists = alerts.find(a => a.title === `${seg.name} 혼잡 감지`)
      if (!exists) {
        const n = new Date()
        const t = `${String(n.getHours()).padStart(2,'0')}:${String(n.getMinutes()).padStart(2,'0')}`
        alerts.unshift({ id: Date.now() + Math.random(), lv:'H', title:`${seg.name} 혼잡 감지`, desc:`평균 속도 ${Math.round(seg.spd)}km/h — 임계값(${thresholds.congSpeed}km/h) 초과`, time:t })
        pushNotif('H', `${seg.name} 혼잡 감지`, `평균 속도 ${Math.round(seg.spd)}km/h`)
      }
    }
    if (seg.spd >= thresholds.slowSpeed) {
      const i = alerts.findIndex(a => a.title === `${seg.name} 혼잡 감지`)
      if (i >= 0) alerts.splice(i, 1)
    }
  })
}, { deep: true })

/* ── 티커 ── */
const TICKER_ITEMS = [
  { lv:'H', text:'[강남] 테헤란로 역삼 혼잡 — CAM-02 287대 감지 / 평균 12km/h' },
  { lv:'H', text:'[서초] 반포IC 진입로 사고 감지 — 주의 요망' },
  { lv:'M', text:'[영동] 영동대로 지체 구간 확인 — CAM-05 정상' },
  { lv:'L', text:'[올림픽] 올림픽대로 원활 / 54km/h' },
  { lv:'H', text:'[강남역] CAM-01 장애 — 현장 점검 출동' },
  { lv:'L', text:'[세종대로] 원활 / 인식률 97% 유지' },
]
const tickerDouble = computed(() => [...TICKER_ITEMS, ...TICKER_ITEMS])

/* ── 풀스크린 ── */
const fullscreenSeg = ref(null)
const fsStats = computed(() => fullscreenSeg.value ? [
  { label:'감지 차량', value: fullscreenSeg.value.cnt },
  { label:'평균 속도', value: Math.round(fullscreenSeg.value.spd)+'km/h' },
  { label:'인식률',    value: fullscreenSeg.value.conf+'%' },
  { label:'카메라',    value: fullscreenSeg.value.cam },
  { label:'소통 상태', value: fullscreenSeg.value.lv==='H'?'정체 주의':fullscreenSeg.value.lv==='M'?'서행 중':'소통 원활', color: levelColor(fullscreenSeg.value.lv) },
] : [])

function openFullscreen(seg) { fullscreenSeg.value = seg }
function closeFullscreen()   { fullscreenSeg.value = null }

/* ── 라이프사이클 ── */
let clockTimer = null, dataTimer = null, logTimer = null, flowTimer = null, cameraTimer = null, statsTimer = null

onMounted(() => {
  clockTimer = setInterval(() => {
    const n = new Date()
    timeStr.value = [n.getHours(),n.getMinutes(),n.getSeconds()].map(v=>String(v).padStart(2,'0')).join(':')
  }, 1000)

  connectWS()
  loadDetectionLogs()
  loadFlowCounts()
  loadZonesAndCameras()
  loadHourlyStats()
  logTimer = setInterval(loadDetectionLogs, 5000)
  flowTimer = setInterval(loadFlowCounts, 5000)
  cameraTimer = setInterval(loadZonesAndCameras, 30000)
  statsTimer = setInterval(loadHourlyStats, 30000)

  dataTimer = setInterval(() => {
    totalV.value  = 1100 + Math.round(Math.random()*300)
    avgSpd.value  = 27   + Math.round(Math.random()*9)
    cIdx.value    = 60   + Math.round(Math.random()*15)
    if (!flowCountsConnected.value) {
      flowIn.value  = 750  + Math.round(Math.random()*200)
      flowOut.value = 350  + Math.round(Math.random()*150)
    }
segments.forEach(s => {
      s.spd = Math.max(5, s.spd + (Math.random()>.5?1:-1)*Math.random()*2)
      s.cnt = Math.max(10, s.cnt + Math.round((Math.random()-.5)*6))
    })
    heatZones.forEach(z => { z.pct = Math.max(10,Math.min(95,z.pct+Math.round((Math.random()-.5)*5))) })
    if (!hourlyStatsConnected.value) {
      chartData.push(6000+Math.round(Math.random()*3000)); chartData.shift()
    }
  }, 4000)

  setTimeout(() => pushNotif('H','테헤란로 혼잡 감지','평균 속도 12km/h — 임계값 초과'), 2000)
  setTimeout(() => pushNotif('M','반포IC 서행 감지','평균 속도 28km/h'), 5000)
})

onUnmounted(() => {
  clearInterval(clockTimer); clearInterval(dataTimer); clearInterval(logTimer); clearInterval(flowTimer); clearInterval(cameraTimer); clearInterval(statsTimer)
  if (wsRetry) clearTimeout(wsRetry)
  if (ws) ws.close()
})
</script>

<style scoped>
.theme-navy { --danger:#e05260; --warn:#d4845a; --ok:#4caf7d; }

.dash-shell { display:flex; flex-direction:column; height:calc(100vh - 62px); margin-top:62px; overflow:hidden; background:var(--bg); }

/* ── 탭바 ── */
.tabbar { display:flex; align-items:center; justify-content:space-between; padding:0 16px; height:48px; flex-shrink:0; background:var(--bg2); border-bottom:1px solid var(--b); }
.tab-inner { display:flex; gap:2px; }
.tab-btn { display:flex; align-items:center; gap:6px; padding:6px 14px; font-size:11.5px; font-weight:500; color:var(--t2); border:none; background:transparent; cursor:pointer; border-radius:4px 4px 0 0; transition:all .2s; }
.tab-btn:hover { color:var(--t); background:rgba(255,255,255,.04); }
.tab-btn.active { color:var(--a); background:rgba(62,201,214,.08); border-bottom:2px solid var(--a); }
.tab-icon { width:13px; height:13px; flex-shrink:0; }
.tab-badge { background:var(--danger); color:#fff; font-size:9px; font-family:'IBM Plex Mono',monospace; padding:1px 5px; border-radius:8px; min-width:16px; text-align:center; }
.tab-right { display:flex; align-items:center; gap:12px; }
.tab-ws { font-size:8px; letter-spacing:1px; padding:2px 8px; border:1px solid; border-radius:2px; }
.tab-ws.ok { color:var(--ok); border-color:rgba(76,175,125,.35); }
.tab-ws.err { color:var(--t3); border-color:rgba(255,255,255,.1); }
.tab-clock { font-family:'IBM Plex Mono',monospace; font-size:13px; color:var(--a); letter-spacing:2px; }
.tab-live { display:flex; align-items:center; gap:5px; font-size:8px; letter-spacing:2px; color:var(--ok); border:1px solid rgba(76,175,125,.4); padding:3px 10px; }
.live-dot { width:5px; height:5px; border-radius:50%; background:var(--ok); animation:lp 1.4s ease-in-out infinite; }
@keyframes lp { 0%,100%{opacity:1} 50%{opacity:.15} }

/* ── 바디 ── */
.dash-body { flex:1; overflow:hidden; min-height:0; }
.tab-content { height:100%; overflow-y:auto; padding:12px 14px 0; display:flex; flex-direction:column; gap:10px; }
.overview-layout { overflow:hidden !important; flex-direction:row; gap:10px; padding-bottom:12px; }

/* ── 풀스크린 ── */
.fs-overlay { position:fixed; inset:0; background:rgba(0,0,0,.88); z-index:1000; display:flex; align-items:center; justify-content:center; backdrop-filter:blur(8px); }
.fs-modal { background:var(--bg2); border:1px solid var(--b); border-radius:12px; width:80vw; max-width:900px; max-height:88vh; display:flex; flex-direction:column; overflow:hidden; }
.fs-header { display:flex; align-items:center; gap:12px; padding:14px 18px; border-bottom:1px solid var(--b); flex-shrink:0; }
.fs-title { font-size:16px; font-weight:600; color:var(--t); flex:1; }
.fs-badge { font-family:'IBM Plex Mono',monospace; font-size:9px; padding:3px 10px; border:1px solid; border-radius:3px; letter-spacing:1px; }
.lv-H { color:#e05260; border-color:rgba(224,82,96,.45); background:rgba(224,82,96,.1); }
.lv-M { color:#d4845a; border-color:rgba(212,132,90,.4);  background:rgba(212,132,90,.08); }
.lv-L { color:#4caf7d; border-color:rgba(76,175,125,.4);  background:rgba(76,175,125,.08); }
.fs-spd { font-size:18px; font-weight:700; }
.fs-close { background:none; border:none; color:var(--t3); cursor:pointer; font-size:20px; padding:4px 8px; margin-left:8px; transition:color .2s; }
.fs-close:hover { color:var(--danger); }
.fs-body { flex:1; position:relative; min-height:0; overflow:hidden; }
.fs-video { width:100%; height:100%; object-fit:contain; display:block; }
.fs-canvas { width:100%; height:100%; display:block; }
.fs-speed-overlay { position:absolute; top:14px; right:16px; display:flex; align-items:baseline; gap:5px; background:rgba(0,0,0,.8); padding:6px 14px; border-radius:6px; z-index:10; }
.fs-footer { display:flex; gap:0; border-top:1px solid var(--b); flex-shrink:0; }
.fs-stat { flex:1; text-align:center; padding:12px 8px; border-right:1px solid var(--b); }
.fs-stat:last-child { border-right:none; }
.fs-sv { font-family:'IBM Plex Mono',monospace; font-size:15px; font-weight:700; }
.fs-sl { font-size:8px; color:var(--t3); margin-top:3px; }

/* ── 알림 팝업 ── */
.notif-container { position:fixed; bottom:44px; right:18px; z-index:900; display:flex; flex-direction:column; gap:8px; pointer-events:none; width:310px; }
.notif { display:flex; align-items:stretch; background:#fff; border:none; border-radius:8px; overflow:hidden; pointer-events:all; box-shadow:0 8px 32px rgba(0,0,0,.22), 0 2px 8px rgba(0,0,0,.12); }
.notif-bar { width:5px; flex-shrink:0; }
.notif-body { flex:1; padding:11px 14px; }
.notif-title { font-family:'IBM Plex Mono',monospace; font-size:10.5px; font-weight:700; color:#0c1a30; letter-spacing:.3px; }
.notif-desc { font-size:10px; color:#4a5568; margin-top:3px; line-height:1.5; }
.notif-close { background:none; border:none; color:#94a3b8; cursor:pointer; font-size:15px; padding:0 12px; transition:color .15s; }
.notif-close:hover { color:#e05260; }
.notif-enter-active { transition:all .3s ease; }
.notif-leave-active { transition:all .25s ease; }
.notif-enter-from,.notif-leave-to { transform:translateX(100%); opacity:0; }

/* ── 티커 ── */
.ticker-bar { height:34px; flex-shrink:0; display:flex; align-items:center; overflow:hidden; background:var(--bg2); border-top:1px solid var(--b); }
.ticker-label { font-family:'IBM Plex Mono',monospace; font-size:8px; letter-spacing:2px; color:var(--a); opacity:.7; padding:0 14px; border-right:1px solid var(--b); white-space:nowrap; flex-shrink:0; }
.ticker-wrap { flex:1; overflow:hidden; }
.ticker-track { display:flex; gap:28px; white-space:nowrap; animation:tickerMove 32s linear infinite; }
@keyframes tickerMove { from{transform:translateX(0)} to{transform:translateX(-50%)} }
.ticker-item { display:inline-flex; align-items:center; gap:6px; font-family:'IBM Plex Mono',monospace; font-size:8.5px; color:var(--t2); }
.ticker-dot { display:inline-block; width:4px; height:4px; border-radius:50%; flex-shrink:0; }

.mono { font-family:'IBM Plex Mono',monospace; }

@media (max-width:1300px) {
  .overview-layout { flex-direction:column; }
}
@media (max-width:768px) {
  .fs-modal { width:95vw; }
}
</style>
