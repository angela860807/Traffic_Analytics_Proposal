<template>
  <div class="ev-layout">

    <!-- ── 좌측 타임라인 ── -->
    <div class="ev-main">
      <div class="panel-head"><span class="ph-bar"></span>실시간 이벤트 로그</div>
      <div class="ev-list">
        <div class="ev-item" v-for="inc in incidents" :key="inc.id" :class="'lv-'+inc.lv">
          <div class="ev-tl">
            <div class="ev-node" :style="{ background: levelColor(inc.lv), boxShadow:'0 0 8px '+levelColor(inc.lv) }" :class="{ pulse: inc.lv==='H' }"></div>
            <div class="ev-line"></div>
          </div>
          <div class="ev-card">
            <!-- 좌측 컬러 바 -->
            <div class="ev-bar" :style="{ background: levelColor(inc.lv) }"></div>
            <div class="ev-content">
              <div class="ev-top">
                <span class="ev-badge" :class="'lv-'+inc.lv">{{ inc.type }}</span>
                <span class="ev-sev" :style="{ color: levelColor(inc.lv) }">{{ inc.lv==='H'?'긴급':inc.lv==='M'?'주의':'일반' }}</span>
                <span class="ev-time mono">{{ inc.time }}</span>
                <span class="ev-live" v-if="inc.lv==='H'"><span class="live-dot"></span>처리 중</span>
              </div>
              <div class="ev-loc">{{ inc.loc }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── 우측 요약 ── -->
    <aside class="ev-aside">
      <div class="panel-head"><span class="ph-bar"></span>이벤트 현황</div>

      <div class="ev-sum">
        <div class="es-card high"><div class="es-n mono">{{ incidents.filter(i=>i.lv==='H').length }}</div><div class="es-l">긴급</div><div class="es-dot" style="background:#e05260"></div></div>
        <div class="es-card mid"><div class="es-n mono">{{ incidents.filter(i=>i.lv==='M').length }}</div><div class="es-l">주의</div><div class="es-dot" style="background:#d4845a"></div></div>
        <div class="es-card low"><div class="es-n mono">{{ incidents.filter(i=>i.lv==='L').length }}</div><div class="es-l">일반</div><div class="es-dot" style="background:#4caf7d"></div></div>
      </div>

      <!-- 도넛 -->
      <div class="panel-head" style="margin-top:14px"><span class="ph-bar"></span>처리 현황</div>
      <div class="donut-wrap">
        <svg viewBox="0 0 80 80" class="donut-svg">
          <circle cx="40" cy="40" r="30" fill="none" stroke="rgba(255,255,255,.06)" stroke-width="9"/>
          <circle cx="40" cy="40" r="30" fill="none" stroke="#e05260" stroke-width="9"
            stroke-linecap="round"
            :stroke-dasharray="`${incidents.filter(i=>i.lv==='H').length/incidents.length*188.5} 188.5`"
            transform="rotate(-90 40 40)"/>
        </svg>
        <div class="donut-c">
          <div class="donut-n mono">{{ incidents.length }}</div>
          <div class="donut-l">전체</div>
        </div>
      </div>
      <div class="donut-leg">
        <div class="dl-row"><span class="dl-dot" style="background:#e05260"></span><span class="dl-t">긴급 {{ incidents.filter(i=>i.lv==='H').length }}건</span></div>
        <div class="dl-row"><span class="dl-dot" style="background:#d4845a"></span><span class="dl-t">주의 {{ incidents.filter(i=>i.lv==='M').length }}건</span></div>
        <div class="dl-row"><span class="dl-dot" style="background:#4caf7d"></span><span class="dl-t">일반 {{ incidents.filter(i=>i.lv==='L').length }}건</span></div>
      </div>

      <!-- 유형별 -->
      <div class="panel-head" style="margin-top:14px"><span class="ph-bar"></span>유형별 분류</div>
      <div class="type-list">
        <div class="tr" v-for="t in typeStats" :key="t.name">
          <div class="tr-dot" :style="{ background: t.color }"></div>
          <div class="tr-name">{{ t.name }}</div>
          <div class="tr-bar-wrap"><div class="tr-bar-fill" :style="{ width:(t.cnt/incidents.length*100)+'%', background:t.color }"></div></div>
          <div class="tr-cnt mono">{{ t.cnt }}</div>
        </div>
      </div>

      <div class="panel-head" style="margin-top:14px"><span class="ph-bar"></span>최근 감지</div>
      <div class="recent-time mono">{{ incidents[0]?.time ?? '--:--' }}</div>
      <div class="recent-sub">마지막 이벤트</div>
    </aside>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { levelColor } from '@/utils/levelColor'
const props = defineProps({ incidents: Array })

const typeStats = computed(() => {
  const map = {}
  props.incidents.forEach(i => {
    if (!map[i.type]) map[i.type] = { name: i.type, cnt: 0, color: levelColor(i.lv) }
    map[i.type].cnt++
  })
  return Object.values(map)
})
</script>

<style scoped>
.ev-layout { display: grid; grid-template-columns: 1fr 190px; gap: 10px; flex: 1; min-height: 0; padding-bottom: 12px; }

.panel-head { display: flex; align-items: center; gap: 8px; font-size: 11px; font-weight: 700; color: var(--t); letter-spacing: .04em; margin-bottom: 10px; }
.ph-bar { width: 3px; height: 13px; background: var(--a); border-radius: 2px; flex-shrink: 0; }

/* 좌측 */
.ev-main { background: var(--bg2); border: 1px solid var(--b); border-radius: 10px; padding: 14px; display: flex; flex-direction: column; overflow: hidden; }
.ev-list { display: flex; flex-direction: column; flex: 1; overflow-y: auto; }

.ev-item { display: flex; gap: 10px; }
.ev-tl { display: flex; flex-direction: column; align-items: center; width: 16px; flex-shrink: 0; }
.ev-node { width: 11px; height: 11px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
.ev-node.pulse { animation: nodePulse 1.6s ease-in-out infinite; }
.ev-line { flex: 1; width: 1px; background: var(--b); margin: 4px 0; min-height: 8px; }
.ev-item:last-child .ev-line { display: none; }

.ev-card { flex: 1; display: flex; background: var(--card); border: 1px solid var(--b); border-radius: 8px; margin-bottom: 8px; overflow: hidden; transition: border-color .2s, transform .15s; }
.ev-card:hover { transform: translateX(2px); }
.lv-H .ev-card { border-color: rgba(224,82,96,.3); background: rgba(224,82,96,.04); }
.lv-M .ev-card { border-color: rgba(212,132,90,.22); }

.ev-bar { width: 4px; flex-shrink: 0; }
.ev-content { flex: 1; padding: 9px 12px; min-width: 0; }
.ev-top { display: flex; align-items: center; gap: 7px; margin-bottom: 5px; flex-wrap: wrap; }

.ev-badge { font-size: 8px; padding: 2px 8px; border: 1px solid; border-radius: 2px; letter-spacing: .8px; font-family: 'IBM Plex Mono',monospace; flex-shrink: 0; }
.lv-H .ev-badge { color: #e05260; border-color: rgba(224,82,96,.4); background: rgba(224,82,96,.08); }
.lv-M .ev-badge { color: #d4845a; border-color: rgba(212,132,90,.35); background: rgba(212,132,90,.06); }
.lv-L .ev-badge { color: #4caf7d; border-color: rgba(76,175,125,.35); background: rgba(76,175,125,.06); }

.ev-sev { font-size: 9px; font-weight: 700; letter-spacing: .5px; font-family: 'IBM Plex Mono',monospace; }
.ev-time { font-size: 9px; color: var(--t3); font-family: 'IBM Plex Mono',monospace; }
.ev-live { display: flex; align-items: center; gap: 4px; font-size: 8px; color: #e05260; margin-left: auto; letter-spacing: .5px; }
.live-dot { width: 5px; height: 5px; border-radius: 50%; background: #e05260; animation: lp 1.4s ease-in-out infinite; flex-shrink: 0; }
.ev-loc { font-size: 12px; color: var(--t); font-weight: 500; }

/* 우측 */
.ev-aside { background: var(--bg2); border: 1px solid var(--b); border-radius: 10px; padding: 14px; display: flex; flex-direction: column; overflow-y: auto; }

.ev-sum { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; }
.es-card { border-radius: 7px; padding: 8px 6px; text-align: center; position: relative; border: 1px solid; }
.es-card.high { background: rgba(224,82,96,.08); border-color: rgba(224,82,96,.25); }
.es-card.mid  { background: rgba(212,132,90,.08); border-color: rgba(212,132,90,.22); }
.es-card.low  { background: rgba(76,175,125,.08); border-color: rgba(76,175,125,.22); }
.es-n { font-size: 18px; font-weight: 700; line-height: 1; }
.es-card.high .es-n { color: #e05260; }
.es-card.mid .es-n  { color: #d4845a; }
.es-card.low .es-n  { color: #4caf7d; }
.es-l { font-size: 7.5px; color: var(--t3); margin-top: 2px; letter-spacing: .5px; }
.es-dot { position: absolute; top: 5px; right: 5px; width: 4px; height: 4px; border-radius: 50%; }

.donut-wrap { position: relative; width: 80px; height: 80px; margin: 0 auto 8px; }
.donut-svg { width: 100%; height: 100%; }
.donut-c { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.donut-n { font-size: 18px; font-weight: 700; color: var(--t); line-height: 1; }
.donut-l { font-size: 7px; color: var(--t3); margin-top: 1px; }
.donut-leg { display: flex; flex-direction: column; gap: 4px; margin-bottom: 0; }
.dl-row { display: flex; align-items: center; gap: 5px; }
.dl-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.dl-t { font-size: 9px; color: var(--t2); }

.type-list { display: flex; flex-direction: column; gap: 6px; }
.tr { display: flex; align-items: center; gap: 6px; }
.tr-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.tr-name { font-size: 9.5px; color: var(--t2); width: 46px; flex-shrink: 0; }
.tr-bar-wrap { flex: 1; height: 4px; background: rgba(255,255,255,.06); border-radius: 2px; overflow: hidden; }
.tr-bar-fill { height: 100%; border-radius: 2px; transition: width 1s ease; }
.tr-cnt { font-size: 9.5px; color: var(--t2); width: 12px; text-align: right; flex-shrink: 0; }

.recent-time { font-size: 20px; font-weight: 700; color: var(--a); line-height: 1; font-family: 'IBM Plex Mono',monospace; }
.recent-sub { font-size: 8.5px; color: var(--t3); margin-top: 2px; }

.mono { font-family: 'IBM Plex Mono',monospace; }
@keyframes lp { 0%,100%{opacity:1} 50%{opacity:.15} }
@keyframes nodePulse { 0%,100%{transform:scale(1);opacity:1} 50%{transform:scale(1.5);opacity:.6} }
</style>
