<template>
  <div class="alert-layout">

    <!-- ── 좌측 패널 ── -->
    <aside class="alert-aside">

      <!-- 도넛 차트 -->
      <div class="donut-wrap">
        <svg viewBox="0 0 120 120" class="donut-svg">
          <circle cx="60" cy="60" r="48" fill="none" stroke="rgba(255,255,255,.05)" stroke-width="14"/>
          <!-- L -->
          <circle cx="60" cy="60" r="48" fill="none" stroke="#4caf7d" stroke-width="14"
            stroke-linecap="round"
            :stroke-dasharray="`${lvPct.L*3.016} 301.6`"
            :stroke-dashoffset="301.6 - lvPct.H*3.016 - lvPct.M*3.016"
            transform="rotate(-90 60 60)"/>
          <!-- M -->
          <circle cx="60" cy="60" r="48" fill="none" stroke="#d4845a" stroke-width="14"
            stroke-linecap="round"
            :stroke-dasharray="`${lvPct.M*3.016} 301.6`"
            :stroke-dashoffset="301.6 - lvPct.H*3.016"
            transform="rotate(-90 60 60)"/>
          <!-- H -->
          <circle cx="60" cy="60" r="48" fill="none" stroke="#e05260" stroke-width="14"
            stroke-linecap="round"
            :stroke-dasharray="`${lvPct.H*3.016} 301.6`"
            stroke-dashoffset="0"
            transform="rotate(-90 60 60)"/>
        </svg>
        <div class="donut-center">
          <div class="donut-n mono">{{ alerts.length }}</div>
          <div class="donut-l">전체</div>
        </div>
      </div>

      <!-- H / M / L 카운터 -->
      <div class="lv-row">
        <div class="lv-pill high">
          <div class="lv-pulse" v-if="lvCnt.H > 0"></div>
          <div class="lv-n mono">{{ lvCnt.H }}</div>
          <div class="lv-label">긴급</div>
        </div>
        <div class="lv-pill mid">
          <div class="lv-n mono">{{ lvCnt.M }}</div>
          <div class="lv-label">주의</div>
        </div>
        <div class="lv-pill low">
          <div class="lv-n mono">{{ lvCnt.L }}</div>
          <div class="lv-label">일반</div>
        </div>
      </div>

      <!-- 임계값 설정 -->
      <div class="panel-head"><span class="ph-bar"></span>임계값 설정</div>
      <div class="th-block">
        <div class="th-item">
          <div class="th-row">
            <span class="th-label">혼잡</span>
            <span class="th-val mono" style="color:#e05260">{{ thresholds.congSpeed }} km/h</span>
          </div>
          <input v-model.number="thresholds.congSpeed" type="range" min="5" max="40" class="th-slider red" />
        </div>
        <div class="th-item">
          <div class="th-row">
            <span class="th-label">지체</span>
            <span class="th-val mono" style="color:#d4845a">{{ thresholds.slowSpeed }} km/h</span>
          </div>
          <input v-model.number="thresholds.slowSpeed" type="range" min="20" max="70" class="th-slider orange" />
        </div>
      </div>

      <!-- 비율 바 -->
      <div class="panel-head" style="margin-top:14px"><span class="ph-bar"></span>심각도 분포</div>
      <div class="dist-bar">
        <div class="db-h" :style="{ flex: lvCnt.H }"></div>
        <div class="db-m" :style="{ flex: lvCnt.M }"></div>
        <div class="db-l" :style="{ flex: lvCnt.L || 1 }"></div>
      </div>
      <div class="dist-labels">
        <span style="color:#e05260">긴급 {{ lvCnt.H }}건</span>
        <span style="color:#d4845a">주의 {{ lvCnt.M }}건</span>
        <span style="color:#4caf7d">일반 {{ lvCnt.L }}건</span>
      </div>

    </aside>

    <!-- ── 우측 알림 목록 ── -->
    <div class="alert-main">
      <div class="am-head">
        <div class="panel-head" style="margin-bottom:0"><span class="ph-bar"></span>실시간 알림 로그</div>
        <div class="am-cnt mono">{{ alerts.length }}건 활성</div>
      </div>

      <div class="alert-list">
        <div v-if="alerts.length === 0" class="no-alerts mono">현재 활성 알림 없음</div>

        <div v-for="a in sortedAlerts" :key="a.id" class="al-card" :class="'lv-'+a.lv">
          <!-- 좌측 심각도 블록 -->
          <div class="al-sev" :style="{ background: sevBg(a.lv) }">
            <div class="al-sev-dot" :class="{ pulse: a.lv==='H' }" :style="{ background: levelColor(a.lv) }"></div>
            <div class="al-sev-txt" :style="{ color: levelColor(a.lv) }">
              {{ a.lv === 'H' ? '긴급' : a.lv === 'M' ? '주의' : '일반' }}
            </div>
          </div>
          <!-- 본문 -->
          <div class="al-body">
            <div class="al-title">{{ a.title }}</div>
            <div class="al-desc">{{ a.desc }}</div>
          </div>
          <!-- 우측 메타 -->
          <div class="al-meta">
            <div class="al-time mono">{{ a.time }}</div>
            <button class="al-dismiss" @click="$emit('dismiss', a.id)">✕</button>
          </div>
          <!-- 하단 컬러 라인 -->
          <div class="al-line" :style="{ background: levelColor(a.lv) }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { levelColor } from '@/utils/levelColor'

const props = defineProps({ alerts: Array, thresholds: Object })
defineEmits(['dismiss'])

const lvCnt = computed(() => ({
  H: props.alerts.filter(a => a.lv === 'H').length,
  M: props.alerts.filter(a => a.lv === 'M').length,
  L: props.alerts.filter(a => a.lv === 'L').length,
}))

const lvPct = computed(() => {
  const total = props.alerts.length || 1
  return {
    H: (lvCnt.value.H / total) * 100,
    M: (lvCnt.value.M / total) * 100,
    L: (lvCnt.value.L / total) * 100,
  }
})

const sortedAlerts = computed(() =>
  [...props.alerts].sort((a, b) => {
    const order = { H: 0, M: 1, L: 2 }
    return order[a.lv] - order[b.lv]
  })
)

function sevBg(lv) {
  if (lv === 'H') return 'rgba(224,82,96,.08)'
  if (lv === 'M') return 'rgba(212,132,90,.08)'
  return 'rgba(76,175,125,.08)'
}
</script>

<style scoped>
.alert-layout { display: grid; grid-template-columns: 220px 1fr; gap: 10px; flex: 1; min-height: 0; padding-bottom: 12px; }

.panel-head { display: flex; align-items: center; gap: 8px; font-size: 11px; font-weight: 700; color: var(--t); letter-spacing: .04em; margin-bottom: 10px; }
.ph-bar { width: 3px; height: 13px; background: var(--a); border-radius: 2px; flex-shrink: 0; }

/* ── 좌측 ── */
.alert-aside { background: var(--bg2); border: 1px solid var(--b); border-radius: 10px; padding: 16px 14px; display: flex; flex-direction: column; overflow-y: auto; gap: 0; }

/* 도넛 */
.donut-wrap { position: relative; width: 110px; height: 110px; margin: 0 auto 14px; }
.donut-svg { width: 100%; height: 100%; }
.donut-center { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.donut-n { font-size: 26px; font-weight: 700; color: var(--t); line-height: 1; }
.donut-l { font-size: 8px; color: var(--t3); margin-top: 2px; letter-spacing: .5px; }

/* H/M/L 카운터 */
.lv-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; margin-bottom: 16px; }
.lv-pill { border-radius: 8px; padding: 10px 6px; text-align: center; border: 1px solid; position: relative; overflow: hidden; }
.lv-pill.high { background: rgba(224,82,96,.10); border-color: rgba(224,82,96,.3); }
.lv-pill.mid  { background: rgba(212,132,90,.10); border-color: rgba(212,132,90,.28); }
.lv-pill.low  { background: rgba(76,175,125,.10); border-color: rgba(76,175,125,.28); }
.lv-n { font-size: 22px; font-weight: 700; line-height: 1; margin-bottom: 3px; }
.lv-pill.high .lv-n { color: #e05260; }
.lv-pill.mid .lv-n  { color: #d4845a; }
.lv-pill.low .lv-n  { color: #4caf7d; }
.lv-label { font-size: 8px; color: var(--t3); letter-spacing: .5px; }
.lv-pulse { position: absolute; top: 5px; right: 5px; width: 6px; height: 6px; border-radius: 50%; background: #e05260; animation: pulse 1.4s ease-in-out infinite; }

/* 임계값 */
.th-block { display: flex; flex-direction: column; gap: 12px; margin-bottom: 0; }
.th-item { display: flex; flex-direction: column; gap: 4px; }
.th-row { display: flex; justify-content: space-between; align-items: center; }
.th-label { font-size: 10px; color: var(--t2); }
.th-val { font-size: 11px; font-weight: 700; }
.th-slider { width: 100%; cursor: pointer; }
.th-slider.red   { accent-color: #e05260; }
.th-slider.orange { accent-color: #d4845a; }

/* 분포 바 */
.dist-bar { height: 8px; border-radius: 4px; display: flex; overflow: hidden; gap: 2px; margin-bottom: 6px; }
.db-h { background: #e05260; border-radius: 3px; transition: flex 1s ease; }
.db-m { background: #d4845a; border-radius: 3px; transition: flex 1s ease; }
.db-l { background: #4caf7d; border-radius: 3px; transition: flex 1s ease; }
.dist-labels { display: flex; justify-content: space-between; font-size: 8.5px; font-weight: 600; }

/* ── 우측 ── */
.alert-main { background: var(--bg2); border: 1px solid var(--b); border-radius: 10px; padding: 14px; display: flex; flex-direction: column; min-height: 0; }
.am-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.am-cnt { font-size: 10px; color: var(--t3); }

.alert-list { display: flex; flex-direction: column; gap: 7px; flex: 1; overflow-y: auto; }
.no-alerts { text-align: center; color: var(--t2); font-size: 11px; padding: 40px; }

.al-card { display: flex; align-items: stretch; background: var(--card); border: 1px solid var(--b); border-radius: 8px; overflow: hidden; position: relative; transition: border-color .2s, transform .15s; }
.al-card:hover { transform: translateX(2px); border-color: var(--ba); }
.al-card.lv-H { border-color: rgba(224,82,96,.3); }
.al-card.lv-M { border-color: rgba(212,132,90,.22); }

/* 심각도 블록 */
.al-sev { width: 56px; flex-shrink: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 5px; padding: 12px 4px; }
.al-sev-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.al-sev-txt { font-size: 9px; font-weight: 700; letter-spacing: .5px; text-align: center; font-family: 'IBM Plex Mono', monospace; }

/* 본문 */
.al-body { flex: 1; min-width: 0; padding: 12px 10px; border-left: 1px solid rgba(255,255,255,.05); border-right: 1px solid rgba(255,255,255,.05); }
.al-title { font-size: 12px; font-weight: 600; color: var(--t); margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.al-desc { font-size: 10.5px; color: var(--t2); line-height: 1.4; }

/* 메타 */
.al-meta { display: flex; flex-direction: column; align-items: flex-end; justify-content: space-between; padding: 12px 12px; flex-shrink: 0; gap: 6px; }
.al-time { font-size: 9px; color: var(--t3); white-space: nowrap; }
.al-dismiss { background: none; border: 1px solid rgba(255,255,255,.1); border-radius: 4px; color: var(--t3); cursor: pointer; font-size: 10px; padding: 3px 7px; transition: all .2s; }
.al-dismiss:hover { border-color: #f87171; color: #f87171; background: rgba(248,113,113,.06); }

/* 하단 컬러 라인 */
.al-line { position: absolute; bottom: 0; left: 0; right: 0; height: 2px; opacity: .5; }

@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.3;transform:scale(1.5)} }

.mono { font-family: 'IBM Plex Mono', monospace; }
</style>
