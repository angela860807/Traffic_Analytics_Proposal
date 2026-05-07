<template>
  <div class="stats-layout">

    <!-- ── 상단 KPI ── -->
    <div class="stats-kpi-row">
      <div class="sk" v-for="s in topKpis" :key="s.label">
        <div class="sk-icon" :style="{ background: s.color + '18', color: s.color }">{{ s.icon }}</div>
        <div class="sk-right">
          <div class="sk-v mono" :style="{ color: s.color }">{{ s.value }}</div>
          <div class="sk-l">{{ s.label }}</div>
        </div>
        <div class="sk-bar-wrap"><div class="sk-bar-fill" :style="{ width: s.pct+'%', background: s.color }"></div></div>
      </div>
    </div>

    <!-- ── 메인 3패널 ── -->
    <div class="stats-main">

      <!-- 좌: 차트 -->
      <div class="stat-panel chart-panel">
        <div class="panel-head"><span class="ph-bar"></span>시간대별 통행량</div>
        <canvas ref="chartRef" class="stat-canvas"></canvas>
        <div class="chart-legend">
          <span class="cl-dot" style="background:#3ec9d6"></span>
          <span class="cl-txt">통행량 추이 (대/시)</span>
          <span class="cl-peak mono">최고 {{ Math.max(...chartData).toLocaleString() }}대</span>
        </div>
      </div>

      <!-- 중: 히트맵 -->
      <div class="stat-panel">
        <div class="panel-head"><span class="ph-bar"></span>구역별 혼잡도</div>
        <div class="heatmap">
          <div v-for="zone in heatZones" :key="zone.name" class="hm-cell">
            <div class="hm-top">
              <span class="hm-name">{{ zone.name }}</span>
              <span class="hm-pct mono" :style="{ color: hmBarColor(zone.pct) }">{{ zone.pct }}%</span>
            </div>
            <div class="hm-bar-wrap">
              <div class="hm-bar-fill" :style="{ width: zone.pct+'%', background: hmBarColor(zone.pct) }"></div>
            </div>
            <div class="hm-status-dot" :style="{ background: hmBarColor(zone.pct) }"></div>
          </div>
        </div>
      </div>

      <!-- 우: 실시간 집계 -->
      <div class="stat-panel">
        <div class="panel-head"><span class="ph-bar"></span>실시간 집계</div>
        <div class="rt-grid">
          <div class="rt-card" v-for="s in rtStats" :key="s.label">
            <div class="rt-top">
              <div class="rt-v mono" :style="{ color: s.color }">{{ s.value }}</div>
              <div class="rt-trend" :style="{ color: s.color }">▲</div>
            </div>
            <div class="rt-l">{{ s.label }}</div>
            <div class="rt-bar-wrap"><div class="rt-bar-fill" :style="{ width: s.pct+'%', background: s.color }"></div></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'

const props = defineProps({
  heatZones: Array, flowIn: Number, flowOut: Number,
  segments: Array,  accCnt: Number,  chartData: Array,
})

const chartRef = ref(null)
const CHART_H = ['07','08','09','10','11','12','13','14','15','16','17','18']

const topKpis = computed(() => [
  { label:'총 통행량',   value:(props.flowIn+props.flowOut).toLocaleString(), color:'var(--a)',  icon:'≡',  pct:80 },
  { label:'입차',        value:props.flowIn.toLocaleString(),                  color:'#4caf7d',  icon:'↑',  pct:Math.min(Math.round(props.flowIn/1000*100),100) },
  { label:'출차',        value:props.flowOut.toLocaleString(),                 color:'#d4845a',  icon:'↓',  pct:Math.min(Math.round(props.flowOut/1000*100),100) },
  { label:'혼잡 구간',   value:props.segments.filter(s=>s.lv==='H').length+'개', color:'#e05260', icon:'⚠', pct:props.segments.filter(s=>s.lv==='H').length/props.segments.length*100 },
  { label:'이상 감지',   value:props.accCnt+'건',                               color:'#e05260', icon:'!',  pct:Math.min(props.accCnt/5*100,100) },
  { label:'평균 인식률', value:'96.2%',                                          color:'var(--a)', icon:'✓', pct:96 },
])

const rtStats = computed(() => [
  { label:'총 통행량',   value:(props.flowIn+props.flowOut).toLocaleString(), color:'var(--a)',  pct:80 },
  { label:'입차',        value:props.flowIn.toLocaleString(),  color:'#4caf7d', pct:Math.min(Math.round(props.flowIn/1000*100),100) },
  { label:'출차',        value:props.flowOut.toLocaleString(), color:'#d4845a', pct:Math.min(Math.round(props.flowOut/1000*100),100) },
  { label:'혼잡 구간',   value:props.segments.filter(s=>s.lv==='H').length+'개', color:'#e05260', pct:props.segments.filter(s=>s.lv==='H').length/props.segments.length*100 },
  { label:'이상 감지',   value:props.accCnt+'건', color:'#e05260', pct:Math.min(props.accCnt/5*100,100) },
  { label:'인식률',      value:'96.2%', color:'var(--a)', pct:96 },
])

function hmBarColor(pct) {
  return pct > 70 ? '#e05260' : pct > 45 ? '#d4845a' : '#4caf7d'
}

function drawChart() {
  const canvas = chartRef.value
  if (!canvas) return
  const W = canvas.offsetWidth || 600, H = canvas.offsetHeight || 160
  canvas.width = W; canvas.height = H
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, W, H)
  const pl=14, pr=14, pt=18, pb=32, cw=W-pl-pr, ch=H-pt-pb
  const data = props.chartData
  const mx = Math.max(...data)*1.08, mn = Math.min(...data)*0.94
  const pts = data.map((v,i) => ({ px: pl+i*(cw/(data.length-1)), py: pt+ch*(1-(v-mn)/(mx-mn)) }))

  // Y axis grid lines
  for (let i = 0; i <= 4; i++) {
    const y = pt + ch*(i/4)
    ctx.strokeStyle = 'rgba(255,255,255,0.04)'; ctx.lineWidth = 1
    ctx.beginPath(); ctx.moveTo(pl,y); ctx.lineTo(W-pr,y); ctx.stroke()
    const val = Math.round(mx - (mx-mn)*(i/4))
    ctx.fillStyle='rgba(150,170,200,.35)'; ctx.font='8px IBM Plex Mono,monospace'; ctx.textAlign='right'
    ctx.fillText(val >= 1000 ? (val/1000).toFixed(1)+'k' : val, pl-3, y+3)
  }

  // Gradient fill
  const gr = ctx.createLinearGradient(0,pt,0,pt+ch)
  gr.addColorStop(0,'rgba(62,201,214,0.28)'); gr.addColorStop(0.7,'rgba(62,201,214,0.06)'); gr.addColorStop(1,'rgba(62,201,214,0)')
  ctx.beginPath(); ctx.moveTo(pts[0].px, pt+ch)
  pts.forEach(p => ctx.lineTo(p.px, p.py))
  ctx.lineTo(pts[pts.length-1].px, pt+ch); ctx.closePath()
  ctx.fillStyle = gr; ctx.fill()

  // Smooth line (bezier)
  ctx.beginPath()
  pts.forEach((p,i) => {
    if (i === 0) { ctx.moveTo(p.px, p.py); return }
    const px0 = pts[i-1]
    const cpx1 = px0.px + (p.px-px0.px)/3
    const cpx2 = p.px  - (p.px-px0.px)/3
    ctx.bezierCurveTo(cpx1, px0.py, cpx2, p.py, p.px, p.py)
  })
  ctx.strokeStyle='#3ec9d6'; ctx.lineWidth=2.5; ctx.shadowColor='#3ec9d6'; ctx.shadowBlur=10; ctx.stroke(); ctx.shadowBlur=0

  // Dots + labels
  pts.forEach((p,i) => {
    ctx.beginPath(); ctx.arc(p.px,p.py,3.5,0,Math.PI*2)
    ctx.fillStyle='#3ec9d6'; ctx.shadowColor='#3ec9d6'; ctx.shadowBlur=8; ctx.fill(); ctx.shadowBlur=0
    ctx.fillStyle='rgba(150,170,200,.55)'; ctx.font='8.5px IBM Plex Mono,monospace'; ctx.textAlign='center'
    ctx.fillText(CHART_H[i]+'시', p.px, H-8)
  })
}

watch(() => props.chartData, () => drawChart(), { deep: true })
onMounted(async () => { await nextTick(); setTimeout(drawChart, 300) })
</script>

<style scoped>
.stats-layout { display: flex; flex-direction: column; gap: 8px; flex: 1; min-height: 0; padding-bottom: 12px; }

.panel-head { display: flex; align-items: center; gap: 8px; font-size: 11px; font-weight: 700; color: var(--t); letter-spacing: .04em; margin-bottom: 10px; }
.ph-bar { width: 3px; height: 13px; background: var(--a); border-radius: 2px; flex-shrink: 0; }

/* ── 상단 KPI ── */
.stats-kpi-row { display: grid; grid-template-columns: repeat(6,1fr); gap: 7px; flex-shrink: 0; }
.sk { background: var(--bg2); border: 1px solid var(--b); border-radius: 8px; padding: 10px 12px; display: flex; align-items: center; gap: 10px; position: relative; overflow: hidden; }
.sk-icon { width: 30px; height: 30px; border-radius: 7px; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; font-family: 'IBM Plex Mono',monospace; }
.sk-right { flex: 1; min-width: 0; }
.sk-v { font-size: 16px; font-weight: 700; line-height: 1; }
.sk-l { font-size: 8px; color: var(--t3); letter-spacing: .5px; text-transform: uppercase; margin-top: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sk-bar-wrap { position: absolute; bottom: 0; left: 0; right: 0; height: 2px; background: rgba(255,255,255,.04); }
.sk-bar-fill { height: 100%; transition: width 1s ease; }

/* ── 메인 3패널 ── */
.stats-main { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 8px; flex: 1; min-height: 0; }
.stat-panel { background: var(--bg2); border: 1px solid var(--b); border-radius: 10px; padding: 14px; display: flex; flex-direction: column; overflow: hidden; }

/* 차트 */
.stat-canvas { display: block; width: 100%; flex: 1; min-height: 0; }
.chart-legend { display: flex; align-items: center; gap: 6px; margin-top: 6px; flex-shrink: 0; }
.cl-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.cl-txt { font-size: 9px; color: var(--t3); }
.cl-peak { font-size: 9px; color: var(--a); margin-left: auto; }

/* 히트맵 */
.heatmap { display: flex; flex-direction: column; gap: 7px; flex: 1; overflow-y: auto; }
.hm-cell { background: var(--card); border: 1px solid var(--b); border-radius: 6px; padding: 8px 10px; position: relative; }
.hm-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
.hm-name { font-size: 10px; color: var(--t); font-weight: 500; }
.hm-pct { font-size: 12px; font-weight: 700; }
.hm-bar-wrap { height: 5px; background: rgba(255,255,255,.06); border-radius: 2px; overflow: hidden; }
.hm-bar-fill { height: 100%; border-radius: 2px; transition: width 1s ease; }
.hm-status-dot { position: absolute; top: 8px; right: 8px; width: 5px; height: 5px; border-radius: 50%; opacity: .7; }

/* 실시간 집계 */
.rt-grid { display: flex; flex-direction: column; gap: 7px; flex: 1; overflow-y: auto; }
.rt-card { background: var(--card); border: 1px solid var(--b); border-radius: 7px; padding: 9px 11px; }
.rt-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 2px; }
.rt-v { font-size: 15px; font-weight: 700; line-height: 1; }
.rt-trend { font-size: 9px; opacity: .7; }
.rt-l { font-size: 8px; color: var(--t3); letter-spacing: .5px; text-transform: uppercase; margin-bottom: 5px; }
.rt-bar-wrap { height: 3px; background: rgba(255,255,255,.06); border-radius: 2px; overflow: hidden; }
.rt-bar-fill { height: 100%; border-radius: 2px; transition: width 1.2s ease; }

.mono { font-family: 'IBM Plex Mono',monospace; }

@media (max-width: 1200px) {
  .stats-kpi-row { grid-template-columns: repeat(3,1fr); }
  .stats-main { grid-template-columns: 1fr 1fr; }
}
</style>
