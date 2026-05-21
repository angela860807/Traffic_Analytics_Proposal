<template>
  <div v-show="active" class="v2-tab-page">
    <div class="v2-page-h">
      <h2><i class="bi bi-bar-chart-fill"></i> 통계 분석</h2>
      <div class="v2-page-actions">
        <select v-model="statsPeriod" class="v2-select">
          <option value="day">일간</option>
          <option value="week">주간</option>
          <option value="month">월간</option>
        </select>
      </div>
    </div>
    <div class="v2-stats-grid">
      <section class="v2-card">
        <div class="v2-card-h"><span><i class="bi bi-calendar3"></i> 요일별 평균 통행량</span></div>
        <div ref="dowEl" class="v2-stat-chart"></div>
      </section>
      <section class="v2-card">
        <div class="v2-card-h"><span><i class="bi bi-arrow-left-right"></i> 시간대별 진입 / 이탈 추이</span></div>
        <div ref="typeEl" class="v2-stat-chart"></div>
      </section>
      <section class="v2-card">
        <div class="v2-card-h"><span><i class="bi bi-hourglass-split"></i> 도로별 평균 정체 시간</span></div>
        <div ref="jamEl" class="v2-stat-chart"></div>
      </section>
      <section class="v2-card">
        <div class="v2-card-h"><span><i class="bi bi-camera-video"></i> 카메라별 진입 / 이탈 비교</span></div>
        <div ref="camStatEl" class="v2-stat-chart"></div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import echarts from '@/composables/echartsSetup'
import { useDashboardData } from '@/composables/useDashboardData'

const props = defineProps({ active: { type: Boolean, default: false } })
const { cameraFeeds } = useDashboardData()

const statsPeriod = ref('day')
const dowEl     = ref(null)
const typeEl    = ref(null)
const jamEl     = ref(null)
const camStatEl = ref(null)
const charts = {}
let initialized = false

const TT = { trigger: 'axis', backgroundColor: '#0a1727', borderColor: 'rgba(255,255,255,.12)', textStyle: { color: '#e4eeff', fontSize: 12 } }

function dowOpt() {
  const vals = [72, 68, 75, 71, 90, 55, 42]
  return {
    backgroundColor: 'transparent',
    grid: { top: 20, right: 16, bottom: 30, left: 40 },
    tooltip: { ...TT, formatter: p => `${p[0].name}<br/>평균 통행량: <b>${p[0].value}%</b>` },
    xAxis: { type: 'category', data: ['월','화','수','목','금','토','일'],
      axisLine: { lineStyle: { color: 'rgba(255,255,255,.1)' } },
      axisTick: { show: false },
      axisLabel: { color: 'rgba(228,238,255,.5)', fontSize: 11 } },
    yAxis: { type: 'value', max: 100,
      axisLabel: { color: 'rgba(228,238,255,.4)', fontSize: 10, formatter: '{value}%' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,.05)' } }, axisLine: { show: false } },
    series: [{ type: 'bar',
      data: vals.map(v => ({ value: v, itemStyle: { color: v > 80 ? '#d4845a' : v > 60 ? '#60a5fa' : '#4caf7d', borderRadius: [4, 4, 0, 0] } })),
      barMaxWidth: 26,
      label: { show: true, position: 'top', color: 'rgba(228,238,255,.55)', fontSize: 10, formatter: '{c}%' } }],
  }
}

function typeOpt() {
  const hours = Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2,'0')}:00`)
  const inData  = [5,3,2,2,4,8,28,55,78,68,62,58,55,60,65,72,82,88,75,55,38,25,15,8]
  const outData = [4,3,2,2,3,6,22,48,72,75,68,62,58,62,68,75,85,82,68,48,32,22,12,6]
  return {
    backgroundColor: 'transparent',
    grid: { top: 32, right: 16, bottom: 24, left: 40 },
    tooltip: TT,
    legend: { top: 4, left: 'center', textStyle: { color: 'rgba(228,238,255,.7)', fontSize: 11 }, itemWidth: 12, itemHeight: 8 },
    xAxis: { type: 'category', data: hours, boundaryGap: false,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,.1)' } }, axisTick: { show: false },
      axisLabel: { color: 'rgba(228,238,255,.4)', fontSize: 10, interval: 3 } },
    yAxis: { type: 'value',
      axisLabel: { color: 'rgba(228,238,255,.4)', fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,.05)' } }, axisLine: { show: false } },
    series: [
      { name: '진입 (IN)',  type: 'line', data: inData,  smooth: true, symbol: 'none',
        lineStyle: { color: '#4caf7d', width: 2 },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(76,175,125,.4)' }, { offset: 1, color: 'rgba(76,175,125,0)' }] } } },
      { name: '이탈 (OUT)', type: 'line', data: outData, smooth: true, symbol: 'none',
        lineStyle: { color: '#d4845a', width: 2 },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(212,132,90,.35)' }, { offset: 1, color: 'rgba(212,132,90,0)' }] } } },
    ],
  }
}

function jamOpt() {
  const roads = ['테헤란로', '반포IC', '영동대로', '올림픽대로', '잠실대교']
  const vals  = [28, 21, 15, 18, 12]
  return {
    backgroundColor: 'transparent',
    grid: { top: 20, right: 16, bottom: 30, left: 70 },
    tooltip: { ...TT, formatter: p => `${p[0].name}<br/>평균 정체: <b>${p[0].value}분</b>` },
    xAxis: { type: 'value',
      axisLabel: { color: 'rgba(228,238,255,.4)', fontSize: 10, formatter: '{value}분' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,.05)' } }, axisLine: { show: false } },
    yAxis: { type: 'category', data: roads,
      axisLabel: { color: 'rgba(228,238,255,.6)', fontSize: 11 },
      axisLine: { show: false }, axisTick: { show: false } },
    series: [{ type: 'bar',
      data: vals.map(v => ({ value: v, itemStyle: { color: v > 20 ? '#e05260' : v > 15 ? '#d4845a' : '#4caf7d', borderRadius: [0, 4, 4, 0] } })),
      barMaxWidth: 22,
      label: { show: true, position: 'right', color: 'rgba(228,238,255,.7)', fontSize: 11, formatter: '{c}분' } }],
  }
}

function camStatOpt() {
  const cams = cameraFeeds.map(c => c.name.replace(' 사거리', '').replace(' 교차로', ''))
  const inVals  = [187, 145, 220, 98,  158, 120]
  const outVals = [165, 132, 195, 105, 142, 110]
  return {
    backgroundColor: 'transparent',
    grid: { top: 32, right: 16, bottom: 42, left: 40 },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' },
      backgroundColor: '#0a1727', borderColor: 'rgba(255,255,255,.12)', textStyle: { color: '#e4eeff' } },
    legend: { top: 4, left: 'center', textStyle: { color: 'rgba(228,238,255,.7)', fontSize: 11 }, itemWidth: 12, itemHeight: 8 },
    xAxis: { type: 'category', data: cams,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,.1)' } }, axisTick: { show: false },
      axisLabel: { color: 'rgba(228,238,255,.5)', fontSize: 10, rotate: 20 } },
    yAxis: { type: 'value',
      axisLabel: { color: 'rgba(228,238,255,.4)', fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,.05)' } }, axisLine: { show: false } },
    series: [
      { name: '진입 (IN)',  type: 'bar', data: inVals,  barMaxWidth: 18,
        itemStyle: { color: '#4caf7d', borderRadius: [3, 3, 0, 0] } },
      { name: '이탈 (OUT)', type: 'bar', data: outVals, barMaxWidth: 18,
        itemStyle: { color: '#d4845a', borderRadius: [3, 3, 0, 0] } },
    ],
  }
}

function init(key, el, opt) {
  if (!el) return
  if (charts[key]) { try { charts[key].dispose() } catch {} }
  const c = echarts.init(el, null, { renderer: 'canvas' })
  c.setOption(opt)
  charts[key] = c
}

function initAll() {
  init('dow',     dowEl.value,     dowOpt())
  init('type',    typeEl.value,    typeOpt())
  init('jam',     jamEl.value,     jamOpt())
  init('camStat', camStatEl.value, camStatOpt())
}
function resizeAll() {
  Object.values(charts).forEach(c => { try { c.resize() } catch {} })
}

watch(() => props.active, async (v) => {
  if (!v) return
  await nextTick()
  if (!initialized) { initAll(); initialized = true }
  else setTimeout(resizeAll, 60)
})

onMounted(() => {
  window.addEventListener('resize', resizeAll)
  if (props.active) {
    nextTick().then(() => { initAll(); initialized = true })
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeAll)
  Object.values(charts).forEach(c => { try { c.dispose() } catch {} })
})
</script>
