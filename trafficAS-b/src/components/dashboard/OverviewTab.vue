<template>
  <!-- Fragment: kpi-panel + road-grid are direct flex children of .overview-layout -->
  <div class="kpi-panel">
    <div v-for="k in kpis" :key="k.label" :class="['kpi', k.type === 'arc' ? 'kpi-gauge' : 'kpi-stat']">
      <template v-if="k.type === 'arc'">
        <svg class="gauge-svg" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="46" fill="rgba(2,8,20,0.97)" stroke="rgba(62,201,214,0.1)" stroke-width="0.8" />
          <circle cx="50" cy="50" r="28" fill="rgba(0,4,14,0.9)" />
          <line v-for="t in 24" :key="t"
            :x1="50 + 33 * Math.cos(((135 + ((t-1)/23)*270)*Math.PI/180))"
            :y1="50 + 33 * Math.sin(((135 + ((t-1)/23)*270)*Math.PI/180))"
            :x2="50 + 44 * Math.cos(((135 + ((t-1)/23)*270)*Math.PI/180))"
            :y2="50 + 44 * Math.sin(((135 + ((t-1)/23)*270)*Math.PI/180))"
            :stroke="((t-1)/23)*100 <= k.pct ? k.color : 'rgba(255,255,255,0.05)'"
            stroke-width="3.5" stroke-linecap="round"
          />
          <line x1="50" y1="50"
            :x2="50 + 23*Math.cos(((135+(k.pct/100)*270)*Math.PI/180))"
            :y2="50 + 23*Math.sin(((135+(k.pct/100)*270)*Math.PI/180))"
            :stroke="k.color" stroke-width="2.5" stroke-linecap="round"
          />
          <line x1="50" y1="50"
            :x2="50 + 7*Math.cos(((135+(k.pct/100)*270+180)*Math.PI/180))"
            :y2="50 + 7*Math.sin(((135+(k.pct/100)*270+180)*Math.PI/180))"
            :stroke="k.color" stroke-width="2" stroke-linecap="round" opacity="0.4"
          />
          <circle cx="50" cy="50" r="5" fill="#060e22" :stroke="k.color" stroke-width="1.5" />
          <circle cx="50" cy="50" r="2" :fill="k.color" />
          <rect x="22" y="65" width="56" height="17" rx="2" fill="rgba(0,8,22,0.95)" :stroke="k.color" stroke-width="0.6" />
          <text x="50" y="77" text-anchor="middle" font-family="'JetBrains Mono',monospace" font-size="10" font-weight="700" :fill="k.color">{{ k.value }}</text>
        </svg>
        <div class="gauge-meta">
          <div class="gauge-lbl">{{ k.label }}</div>
          <div class="gauge-unit" v-if="k.unit">{{ k.unit }}</div>
          <div class="gauge-bar"><div class="gauge-bar-fill" :style="{ width: k.pct+'%', background: k.color, boxShadow: `0 0 5px ${k.color}88` }"></div></div>
          <div class="gauge-pct mono" :style="{ color: k.color }">{{ k.pct }}%</div>
        </div>
      </template>
      <template v-else>
        <div class="stat-lbl">{{ k.label }}</div>
        <div class="stat-val mono" :style="{ color: k.color }">{{ k.value }}<span class="stat-unit">{{ k.unit }}</span></div>
        <div class="stat-track"><div class="stat-fill" :style="{ width: k.pct+'%', background: k.color, boxShadow: `0 0 5px ${k.color}55` }"></div></div>
        <div class="stat-pct mono" :style="{ color: k.color }">{{ k.pct }}%</div>
      </template>
    </div>
  </div>

  <div class="road-grid">
    <div v-for="seg in segments.slice(0,4)" :key="seg.id" class="rcard" :class="seg.lv" @click="$emit('openFullscreen', seg)">
      <div class="rc-top">
        <div class="rc-lv-bar" :style="{ background: levelColor(seg.lv) }"></div>
        <div class="rc-info">
          <div class="rc-name">{{ seg.name }}</div>
          <div class="rc-cam mono"><span class="rc-cam-dot" :style="{ color: levelColor(seg.lv) }">●</span>{{ seg.cam }}</div>
        </div>
        <div class="rc-badge" :class="'lv-'+seg.lv">{{ seg.lv === 'H' ? '혼잡' : seg.lv === 'M' ? '지체' : '원활' }}</div>
      </div>
      <div class="rc-media-wrap">
        <video v-if="seg.videoUrl" class="rc-video" :src="seg.videoUrl" autoplay muted loop playsinline></video>
        <canvas v-else :ref="el => { if (el) canvasRefs[seg.id] = el }" class="rc-canvas"></canvas>
        <div class="rc-speed-overlay">
          <span class="mono rc-spd-num" :style="{ color: levelColor(seg.lv) }">{{ Math.round(seg.spd) }}</span>
          <span class="rc-spd-unit">km/h</span>
        </div>
        <div class="rc-fullscreen-hint mono">클릭하여 확대</div>
      </div>
      <div class="rc-bottom">
        <div class="rc-stat">
          <div class="rc-sl">감지 차량</div>
          <div class="rc-sv mono" :style="{ color: levelColor(seg.lv) }">{{ seg.cnt }}<span class="rc-sv-u">대</span></div>
        </div>
        <div class="rc-divider"></div>
        <div class="rc-stat">
          <div class="rc-sl">인식률</div>
          <div class="rc-sv mono">{{ seg.conf }}<span class="rc-sv-u">%</span></div>
        </div>
        <div class="rc-divider"></div>
        <div class="rc-stat">
          <div class="rc-sl">소통 상태</div>
          <div class="rc-sv mono" :style="{ color: levelColor(seg.lv) }">{{ seg.lv === 'H' ? '정체' : seg.lv === 'M' ? '서행' : '원활' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { levelColor } from '@/utils/levelColor'

const props = defineProps({ segments: Array, kpis: Array })
defineEmits(['openFullscreen'])

const canvasRefs = {}
const segCars = {}
const VCOLORS = { H: '#e05260', M: '#d4845a', L: '#4caf7d' }

function initCars(seg) {
  const n = seg.lv === 'H' ? 6 : seg.lv === 'M' ? 4 : 2
  const s = seg.lv === 'H' ? 0.35 : seg.lv === 'M' ? 1.4 : 2.8
  const cars = []
  ;[1, -1].forEach(dir => {
    for (let i = 0; i < n; i++)
      cars.push({ pos: Math.random(), dir, spd: s*(0.8+Math.random()*0.4), stop: 0, lv: seg.lv, col: VCOLORS[seg.lv] })
  })
  segCars[seg.id] = cars
}

function drawCanvas(canvas, seg) {
  const W = canvas.width, H = canvas.height
  if (!W || !H) return
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, W, H)
  ctx.fillStyle = '#06080f'; ctx.fillRect(0, 0, W, H)
  const isV = seg.dir === 'V', RW = isV ? W*0.42 : H*0.42, LW = RW/2, rc = isV ? W/2 : H/2
  const rdBg = { H: 'rgba(224,82,96,0.14)', M: 'rgba(212,132,90,0.12)', L: 'rgba(76,175,125,0.11)' }
  const edCol = { H: 'rgba(224,82,96,0.75)', M: 'rgba(212,132,90,0.70)', L: 'rgba(76,175,125,0.70)' }
  ctx.fillStyle = rdBg[seg.lv]
  if (isV) ctx.fillRect(rc-RW/2, 0, RW, H); else ctx.fillRect(0, rc-RW/2, W, RW)
  ctx.strokeStyle = edCol[seg.lv]; ctx.lineWidth = 1.5
  if (isV) {
    [[rc-RW/2],[rc+RW/2]].forEach(([x]) => { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke() })
  } else {
    [[rc-RW/2],[rc+RW/2]].forEach(([y]) => { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke() })
  }
  ctx.strokeStyle = 'rgba(200,170,0,0.55)'; ctx.lineWidth = 1
  if (isV) { ctx.beginPath(); ctx.moveTo(rc,0); ctx.lineTo(rc,H); ctx.stroke() }
  else { ctx.beginPath(); ctx.moveTo(0,rc); ctx.lineTo(W,rc); ctx.stroke() }
  const cars = segCars[seg.id]||[], CL = LW*0.72, CW = LW*0.46
  cars.forEach(car => {
    if (car.lv === 'H') {
      if (car.stop > 0) { car.stop--; return }
      if (Math.random() < 0.004) car.stop = 30 + Math.floor(Math.random()*80)
    }
    car.pos += (car.spd/1000)*car.dir
    if (car.pos > 1.02) car.pos = -0.02
    if (car.pos < -0.02) car.pos = 1.02
    const cx = isV ? rc+(car.dir*LW)/2 : car.pos*W, cy = isV ? car.pos*H : rc+(car.dir*LW)/2
    ctx.save(); ctx.shadowColor = car.col; ctx.shadowBlur = 7; ctx.fillStyle = car.col
    ctx.globalAlpha = car.stop > 0 ? 0.38 : 0.9; ctx.translate(cx, cy)
    if (isV) ctx.fillRect(-CW/2, -CL/2, CW, CL); else ctx.fillRect(-CL/2, -CW/2, CL, CW)
    ctx.restore()
  })
}

let animId = null
onMounted(() => {
  props.segments.forEach(s => initCars(s))
  const animate = () => {
    props.segments.forEach(seg => {
      if (!seg.videoUrl) {
        const canvas = canvasRefs[seg.id]
        if (canvas) {
          const wrap = canvas.parentElement
          if (wrap) {
            const nw = wrap.clientWidth||200, nh = wrap.clientHeight||100
            if (canvas.width !== nw || canvas.height !== nh) { canvas.width = nw; canvas.height = nh }
          }
          drawCanvas(canvas, seg)
        }
      }
    })
    animId = requestAnimationFrame(animate)
  }
  setTimeout(() => { animId = requestAnimationFrame(animate) }, 200)
})
onUnmounted(() => { if (animId) cancelAnimationFrame(animId) })
</script>

<style scoped>
/* ── KPI 패널 ── */
.kpi-panel { width: 268px; flex-shrink: 0; display: flex; flex-direction: column; gap: 5px; overflow: hidden; }
.kpi { background: var(--card); border: 1px solid var(--b); border-radius: 10px; position: relative; overflow: hidden; transition: border-color .2s; }
.kpi::after { content: ''; position: absolute; inset: 0; border-radius: 10px; background: linear-gradient(135deg,rgba(255,255,255,.018),transparent 55%); pointer-events: none; }
.kpi-gauge { flex: 1.6; min-height: 0; display: flex; flex-direction: row; align-items: center; gap: 8px; padding: 6px 10px; }
.kpi-stat { flex: 1; min-height: 0; display: flex; flex-direction: column; justify-content: center; gap: 4px; padding: 10px 14px; }
.stat-lbl { font-size: 8px; color: var(--t3); letter-spacing: 1.2px; text-transform: uppercase; }
.stat-val { font-family: 'JetBrains Mono',monospace; font-size: 28px; font-weight: 700; line-height: 1; }
.stat-unit { font-size: 10px; font-weight: 400; color: var(--t3); margin-left: 4px; font-family: inherit; }
.stat-track { height: 4px; background: rgba(255,255,255,.05); border-radius: 2px; overflow: hidden; }
.stat-fill { height: 100%; border-radius: 2px; transition: width 1.2s ease; }
.stat-pct { font-family: 'JetBrains Mono',monospace; font-size: 9px; opacity: .55; }
.gauge-svg { flex-shrink: 0; width: 100px; height: 100px; filter: drop-shadow(0 0 8px rgba(62,201,214,.22)); }
.gauge-meta { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px; }
.gauge-lbl { font-size: 7.5px; color: var(--t3); letter-spacing: 1.2px; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.gauge-unit { font-size: 10px; color: var(--t2); }
.gauge-bar { height: 3px; background: rgba(255,255,255,.05); border-radius: 2px; overflow: hidden; margin-top: 2px; }
.gauge-bar-fill { height: 100%; border-radius: 2px; transition: width 1.2s ease; }
.gauge-pct { font-family: 'JetBrains Mono',monospace; font-size: 9px; opacity: .6; }

/* ── 도로 그리드 ── */
.road-grid { flex: 1; display: grid; grid-template-columns: repeat(2,1fr); grid-template-rows: repeat(2,1fr); gap: 7px; min-height: 0; }
.rcard { background: var(--card); border: 1px solid var(--b); border-radius: 8px; display: flex; flex-direction: column; overflow: hidden; cursor: pointer; transition: border-color .25s, transform .2s; }
.rcard:hover { transform: translateY(-1px); }
.rcard:hover .rc-fullscreen-hint { opacity: 1; }
.rcard.H { border-color: rgba(224,82,96,.3); }
.rcard.M { border-color: rgba(212,132,90,.26); }
.rcard.L { border-color: rgba(76,175,125,.26); }
.rc-top { display: flex; align-items: center; flex-shrink: 0; }
.rc-lv-bar { width: 3px; align-self: stretch; flex-shrink: 0; }
.rc-info { flex: 1; padding: 8px 10px; min-width: 0; }
.rc-name { font-size: 12px; font-weight: 600; color: var(--t); overflow: hidden; white-space: nowrap; text-overflow: ellipsis; letter-spacing: -.2px; }
.rc-cam { font-family: 'JetBrains Mono',monospace; font-size: 9px; color: var(--t3); margin-top: 3px; display: flex; align-items: center; gap: 4px; }
.rc-cam-dot { font-size: 6px; line-height: 1; }
.rc-badge { font-family: 'JetBrains Mono',monospace; font-size: 8px; font-weight: 600; padding: 3px 9px; border: 1px solid; border-radius: 100px; white-space: nowrap; flex-shrink: 0; margin-right: 10px; letter-spacing: .5px; }
.lv-H { color: #e05260; border-color: rgba(224,82,96,.45); background: rgba(224,82,96,.1); }
.lv-M { color: #d4845a; border-color: rgba(212,132,90,.4); background: rgba(212,132,90,.08); }
.lv-L { color: #4caf7d; border-color: rgba(76,175,125,.4); background: rgba(76,175,125,.08); }
.rc-media-wrap { flex: 1; min-height: 0; position: relative; overflow: hidden; }
.rc-video { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 1; }
.rc-canvas { display: block; width: 100%; height: 100%; }
.rc-speed-overlay { position: absolute; top: 7px; right: 9px; display: flex; align-items: baseline; gap: 3px; background: rgba(6,8,15,.8); padding: 3px 7px; border-radius: 4px; z-index: 15; }
.rc-spd-num { font-family: 'JetBrains Mono',monospace; font-size: 20px; font-weight: 700; line-height: 1; }
.rc-spd-unit { font-size: 9px; color: var(--t3); font-family: 'JetBrains Mono',monospace; }
.rc-fullscreen-hint { position: absolute; bottom: 8px; left: 50%; transform: translateX(-50%); font-family: 'IBM Plex Mono',monospace; font-size: 8px; letter-spacing: 1.5px; color: rgba(62,201,214,.7); background: rgba(0,0,0,.7); padding: 3px 10px; border-radius: 2px; z-index: 15; opacity: 0; transition: opacity .2s; white-space: nowrap; }
.rc-bottom { display: flex; align-items: stretch; flex-shrink: 0; border-top: 1px solid var(--b); min-height: 52px; }
.rc-stat { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; padding: 8px 4px; }
.rc-divider { width: 1px; background: var(--b); align-self: stretch; }
.rc-sv { font-family: 'JetBrains Mono',monospace; font-size: 15px; font-weight: 700; color: var(--t); line-height: 1; }
.rc-sv-u { font-size: 9px; font-weight: 400; color: var(--t3); margin-left: 2px; }
.rc-sl { font-size: 7px; color: var(--t3); letter-spacing: .6px; text-transform: uppercase; }
.mono { font-family: 'IBM Plex Mono', monospace; }
</style>
