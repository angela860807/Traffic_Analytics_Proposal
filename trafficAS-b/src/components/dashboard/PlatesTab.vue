<template>
  <div class="plate-layout">

    <!-- ── 좌측 KPI ── -->
    <aside class="plate-aside">
      <div class="panel-head"><span class="ph-bar"></span>입출차 현황</div>

      <div class="flow-card in">
        <div class="flow-icon">↑</div>
        <div class="flow-body">
          <div class="flow-v mono" style="color:#4caf7d">{{ flowIn.toLocaleString() }}</div>
          <div class="flow-l">입차 (대/시)</div>
        </div>
      </div>
      <div class="flow-card out">
        <div class="flow-icon" style="color:#d4845a">↓</div>
        <div class="flow-body">
          <div class="flow-v mono" style="color:#d4845a">{{ flowOut.toLocaleString() }}</div>
          <div class="flow-l">출차 (대/시)</div>
        </div>
      </div>

      <div class="kpi-stack">
        <div class="kp"><div class="kp-l">총 통행량</div><div class="kp-v mono">{{ (flowIn+flowOut).toLocaleString() }}</div></div>
        <div class="kp"><div class="kp-l">평균 인식률</div><div class="kp-v mono" style="color:var(--a)">96.2%</div></div>
        <div class="kp"><div class="kp-l">입차 비율</div><div class="kp-v mono" style="color:#4caf7d">{{ inRatio }}%</div></div>
        <div class="kp"><div class="kp-l">출차 비율</div><div class="kp-v mono" style="color:#d4845a">{{ outRatio }}%</div></div>
      </div>

      <div class="panel-head" style="margin-top:14px"><span class="ph-bar"></span>방향별 비율</div>
      <div class="ratio-bar">
        <div class="r-in" :style="{ flex: inRatio }"></div>
        <div class="r-out" :style="{ flex: outRatio }"></div>
      </div>
      <div class="ratio-row">
        <span style="color:#4caf7d">IN {{ inRatio }}%</span>
        <span style="color:#d4845a">OUT {{ outRatio }}%</span>
      </div>
    </aside>

    <!-- ── 우측 메인 ── -->
    <div class="plate-main">

      <!-- 최신 인식 카드 -->
      <div class="latest-capture" v-if="plates.length">
        <div class="lc-label mono">LATEST CAPTURE</div>
        <div class="lc-body">
          <div class="lc-plate">
            <span class="plate-num mono">{{ plates[0].num }}</span>
          </div>
          <div class="lc-meta">
            <div class="lm-row">
              <span class="lm-key">카메라</span><span class="lm-val mono">{{ plates[0].cam }}</span>
            </div>
            <div class="lm-row">
              <span class="lm-key">시각</span><span class="lm-val mono">{{ plates[0].time }}</span>
            </div>
            <div class="lm-row">
              <span class="lm-key">신뢰도</span>
              <span class="lm-val mono" style="color:var(--a)">{{ plates[0].conf }}%</span>
            </div>
            <div class="lm-row">
              <span class="lm-key">방향</span>
              <span class="dir-badge" :class="plates[0].dir">{{ plates[0].dir }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 테이블 -->
      <div class="plate-table-wrap">
        <div class="pt-toolbar">
          <div class="panel-head" style="margin-bottom:0"><span class="ph-bar"></span>번호판 인식 로그</div>
          <div class="search-wrap">
            <input v-model="search" class="search-input mono" placeholder="번호판 검색..." />
            <span class="search-cnt mono">{{ filtered.length }}건</span>
          </div>
        </div>
        <div class="pt-inner">
          <div class="pt-head">
            <div>번호판</div><div>방향</div><div>카메라</div><div>시각</div><div>신뢰도</div>
          </div>
          <div class="pt-body">
            <transition-group name="row-slide" tag="div">
              <div class="pt-row" v-for="p in filtered" :key="p.id">
                <div class="pt-num mono">{{ p.num }}</div>
                <div><span class="dir-badge" :class="p.dir">{{ p.dir }}</span></div>
                <div class="pt-meta mono">{{ p.cam }}</div>
                <div class="pt-meta mono">{{ p.time }}</div>
                <div class="pt-conf mono">{{ p.conf }}%</div>
              </div>
            </transition-group>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
const props = defineProps({ plates: Array, flowIn: Number, flowOut: Number })
const search = ref('')
const filtered = computed(() =>
  search.value ? props.plates.filter(p => p.num.includes(search.value)) : props.plates
)
const total    = computed(() => props.flowIn + props.flowOut)
const inRatio  = computed(() => total.value ? Math.round(props.flowIn  / total.value * 100) : 0)
const outRatio = computed(() => total.value ? Math.round(props.flowOut / total.value * 100) : 0)
</script>

<style scoped>
.plate-layout { display: grid; grid-template-columns: 200px 1fr; gap: 10px; flex: 1; min-height: 0; padding-bottom: 12px; }

.panel-head { display: flex; align-items: center; gap: 8px; font-size: 11px; font-weight: 700; color: var(--t); letter-spacing: .04em; margin-bottom: 10px; }
.ph-bar { width: 3px; height: 13px; background: var(--a); border-radius: 2px; flex-shrink: 0; }

/* 좌측 */
.plate-aside { background: var(--bg2); border: 1px solid var(--b); border-radius: 10px; padding: 14px; display: flex; flex-direction: column; overflow-y: auto; }

.flow-card { display: flex; align-items: center; gap: 10px; border-radius: 8px; padding: 10px 12px; margin-bottom: 7px; border: 1px solid; }
.flow-card.in  { background: rgba(76,175,125,.07); border-color: rgba(76,175,125,.22); }
.flow-card.out { background: rgba(212,132,90,.07);  border-color: rgba(212,132,90,.2); }
.flow-icon { font-size: 20px; font-weight: 900; width: 24px; text-align: center; flex-shrink: 0; color: #4caf7d; }
.flow-v { font-size: 18px; font-weight: 700; line-height: 1; }
.flow-l { font-size: 8.5px; color: var(--t3); margin-top: 2px; letter-spacing: .5px; text-transform: uppercase; }

.kpi-stack { display: flex; flex-direction: column; gap: 5px; }
.kp { display: flex; justify-content: space-between; align-items: center; padding: 6px 9px; background: var(--card); border: 1px solid var(--b); border-radius: 5px; }
.kp-l { font-size: 9.5px; color: var(--t2); }
.kp-v { font-size: 12px; font-weight: 700; color: var(--t); }

.ratio-bar { height: 8px; border-radius: 4px; display: flex; overflow: hidden; gap: 2px; margin-bottom: 5px; }
.r-in  { background: #4caf7d; border-radius: 3px; transition: flex 1s; }
.r-out { background: #d4845a; border-radius: 3px; transition: flex 1s; }
.ratio-row { display: flex; justify-content: space-between; font-size: 8.5px; font-weight: 600; }

/* 우측 */
.plate-main { background: var(--bg2); border: 1px solid var(--b); border-radius: 10px; padding: 14px; display: flex; flex-direction: column; gap: 10px; min-height: 0; }

/* 최신 인식 카드 */
.latest-capture { background: #080d18; border: 1px solid rgba(62,201,214,.2); border-radius: 8px; padding: 12px 14px; flex-shrink: 0; }
.lc-label { font-size: 8px; color: var(--a); letter-spacing: 2.5px; margin-bottom: 10px; }
.lc-body { display: flex; align-items: center; gap: 14px; }
.lc-plate { background: #f5c518; border-radius: 5px; padding: 8px 18px; flex-shrink: 0; box-shadow: 0 0 16px rgba(245,197,24,.25); }
.plate-num { font-size: 18px; font-weight: 800; color: #111; letter-spacing: .04em; }
.lc-meta { display: flex; flex-direction: column; gap: 4px; }
.lm-row { display: flex; align-items: center; gap: 8px; }
.lm-key { font-size: 9px; color: var(--t3); width: 42px; flex-shrink: 0; }
.lm-val { font-size: 10px; color: var(--t2); }

/* 테이블 */
.plate-table-wrap { display: flex; flex-direction: column; flex: 1; min-height: 0; }
.pt-toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.search-wrap { display: flex; align-items: center; gap: 7px; }
.search-input { background: var(--card); border: 1px solid var(--b); color: var(--t); padding: 5px 10px; font-size: 10.5px; border-radius: 4px; outline: none; transition: border-color .2s; width: 160px; }
.search-input:focus { border-color: var(--a); }
.search-input::placeholder { color: var(--t3); }
.search-cnt { font-size: 9.5px; color: var(--t3); }

.pt-inner { display: flex; flex-direction: column; flex: 1; min-height: 0; background: var(--card); border: 1px solid var(--b); border-radius: 7px; overflow: hidden; }
.pt-head { display: grid; grid-template-columns: 2.2fr .8fr 1.1fr .9fr .9fr; padding: 8px 14px; font-size: 8px; color: var(--a); letter-spacing: 1.2px; text-transform: uppercase; border-bottom: 1px solid var(--b); background: rgba(62,201,214,.04); flex-shrink: 0; }
.pt-body { flex: 1; overflow-y: auto; }
.pt-row { display: grid; grid-template-columns: 2.2fr .8fr 1.1fr .9fr .9fr; padding: 8px 14px; border-bottom: 1px solid rgba(255,255,255,.03); align-items: center; transition: background .15s; }
.pt-row:hover { background: rgba(255,255,255,.04); }
.pt-row:last-child { border-bottom: none; }
.pt-num { font-size: 12px; font-weight: 600; color: var(--t); }
.pt-meta { font-size: 9px; color: var(--t3); }
.pt-conf { font-size: 10px; color: var(--a); font-weight: 600; }

.dir-badge { font-size: 8px; padding: 2px 7px; border: 1px solid; border-radius: 2px; letter-spacing: .8px; font-family: 'IBM Plex Mono',monospace; }
.dir-badge.IN  { color: #4caf7d; border-color: rgba(76,175,125,.4);  background: rgba(76,175,125,.08); }
.dir-badge.OUT { color: #d4845a; border-color: rgba(212,132,90,.4);  background: rgba(212,132,90,.08); }

.row-slide-enter-active { transition: all .3s ease; }
.row-slide-enter-from   { transform: translateY(-6px); opacity: 0; }

.mono { font-family: 'IBM Plex Mono',monospace; }
</style>
