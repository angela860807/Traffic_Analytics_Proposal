<template>
  <div class="cam-layout">

    <!-- ── 상단: 메인 피드 + 카메라 목록 ── -->
    <div class="cam-top">

      <!-- 메인 CCTV 화면 -->
      <div class="feat-screen">
        <div class="scanlines"></div>

        <!-- 상단 오버레이 -->
        <div class="fs-top">
          <span class="fs-id mono">{{ sel.id }}</span>
          <span class="fs-live" v-if="sel.ok"><span class="live-dot"></span>LIVE</span>
          <span class="fs-err" v-else>● OFFLINE</span>
        </div>

        <!-- 중앙 콘텐츠 -->
        <div v-if="!sel.ok" class="fs-ns">
          <div class="ns-txt mono">NO SIGNAL</div>
          <div class="ns-sub mono">{{ sel.id }} — 응답 없음</div>
        </div>
        <div v-else class="fs-body">
          <div class="fs-road">
            <div class="road-line"></div>
            <div class="road-line"></div>
          </div>
          <div class="fs-info">
            <div class="fs-cnt mono" :style="{ color: vc(sel.cnt) }">{{ sel.cnt }}</div>
            <div class="fs-cnt-l">대 감지 중</div>
          </div>
          <!-- 미니 activity 바 -->
          <div class="fs-bars">
            <div v-for="(h,i) in bars(sel)" :key="i" class="fs-bar"
              :style="{ height: h+'%', background: vc(sel.cnt), opacity: 0.2+i*0.09 }">
            </div>
          </div>
        </div>

        <!-- 하단 오버레이 -->
        <div class="fs-bot">
          <span class="fs-loc">{{ sel.loc }}</span>
          <span class="fs-time mono">{{ timeStr }}</span>
          <span class="fs-acc mono" style="color:var(--a)">97% 인식률</span>
        </div>
      </div>

      <!-- 우측: 카메라 목록 + 집계 -->
      <aside class="cam-aside">
        <div class="panel-head"><span class="ph-bar"></span>카메라 선택</div>
        <div class="cam-selector">
          <div v-for="cam in cameras" :key="cam.id"
            class="csi" :class="{ active: selectedId === cam.id, offline: !cam.ok }"
            @click="selectedId = cam.id">
            <div class="csi-thumb">
              <div class="csi-scan"></div>
              <span class="csi-id mono">{{ cam.id.split('-')[1] }}</span>
              <span class="csi-st" :class="cam.ok ? 'ok' : 'err'">{{ cam.ok ? '●' : '●' }}</span>
            </div>
            <div class="csi-info">
              <div class="csi-name mono">{{ cam.id }}</div>
              <div class="csi-loc">{{ cam.loc }}</div>
              <div class="csi-cnt mono" :style="{ color: vc(cam.cnt) }">{{ cam.cnt }}대</div>
            </div>
          </div>
        </div>

        <div class="panel-head" style="margin-top:12px"><span class="ph-bar"></span>현황 요약</div>
        <div class="agg-row">
          <div class="ag"><div class="ag-v" style="color:var(--a)">{{ cameras.length }}</div><div class="ag-l">전체</div></div>
          <div class="ag"><div class="ag-v" style="color:#4caf7d">{{ cameras.filter(c=>c.ok).length }}</div><div class="ag-l">정상</div></div>
          <div class="ag"><div class="ag-v" style="color:#e05260">{{ cameras.filter(c=>!c.ok).length }}</div><div class="ag-l">장애</div></div>
          <div class="ag"><div class="ag-v">{{ totalV.toLocaleString() }}</div><div class="ag-l">감지 차량</div></div>
        </div>

        <div class="acc-wrap">
          <div class="acc-track"><div class="acc-fill"></div></div>
          <span class="mono acc-val">97.0%</span>
        </div>
      </aside>
    </div>

    <!-- ── 하단: 차량 인식 캡처 그리드 (WISENET 스타일) ── -->
    <div class="cap-section">
      <div class="cap-header">
        <div class="panel-head" style="margin-bottom:0"><span class="ph-bar"></span>최근 차량 인식</div>
        <span class="cap-cnt mono">{{ plates.length }}건 인식됨</span>
      </div>
      <div class="cap-grid">
        <div v-for="p in plates" :key="p.id" class="cap-card" :class="{ 'latest': p === plates[0] }">
          <!-- 캡처 썸네일 -->
          <div class="cap-thumb">
            <div class="cap-scan"></div>
            <!-- 타임스탬프 -->
            <div class="cap-ts-bar">
              <span class="cap-ts mono">{{ p.time }}</span>
              <span class="cap-cam mono">{{ p.cam }}</span>
            </div>
            <!-- 차량 아이콘 영역 -->
            <div class="cap-vehicle">
              <div class="veh-silhouette"></div>
            </div>
            <!-- 번호판 오버레이 -->
            <div class="cap-plate">
              <span class="cap-plate-num mono">{{ p.num }}</span>
            </div>
            <!-- 최신 배지 -->
            <div v-if="p === plates[0]" class="cap-new mono">NEW</div>
          </div>
          <!-- 메타데이터 -->
          <div class="cap-meta">
            <div class="cm-row">
              <span class="cm-k">방향</span>
              <span class="dir-badge" :class="p.dir">{{ p.dir }}</span>
            </div>
            <div class="cm-row">
              <span class="cm-k">카메라</span>
              <span class="cm-v mono">{{ p.cam }}</span>
            </div>
            <div class="cm-row">
              <span class="cm-k">신뢰도</span>
              <span class="cm-v mono" style="color:var(--a)">{{ p.conf }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'

const props = defineProps({ cameras: Array, plates: Array })
const timeStr = inject('timeStr', '')

const selectedId = ref(props.cameras[0]?.id)
const sel = computed(() => props.cameras.find(c => c.id === selectedId.value) ?? props.cameras[0])
const totalV = computed(() => props.cameras.reduce((s,c) => s+c.cnt, 0))

function vc(cnt) {
  return cnt > 250 ? '#e05260' : cnt > 150 ? '#d4845a' : '#4caf7d'
}
function bars(cam) {
  const seed = cam.id.charCodeAt(cam.id.length - 1)
  return Array.from({ length: 12 }, (_,i) => Math.max(10, ((seed*17+i*31+cam.cnt*0.4)%80)))
}
</script>

<style scoped>
.cam-layout { display: flex; flex-direction: column; flex: 1; min-height: 0; gap: 10px; padding-bottom: 12px; }

.panel-head { display: flex; align-items: center; gap: 8px; font-size: 11px; font-weight: 700; color: var(--t); letter-spacing: .04em; margin-bottom: 10px; }
.ph-bar { width: 3px; height: 13px; background: var(--a); border-radius: 2px; flex-shrink: 0; }

/* ── 상단 ── */
.cam-top { display: grid; grid-template-columns: 1fr 230px; gap: 10px; height: 280px; flex-shrink: 0; }

/* 메인 피드 */
.feat-screen { position: relative; background: #03050c; border: 1px solid rgba(255,255,255,.08); border-radius: 10px; overflow: hidden; }
.scanlines { position: absolute; inset: 0; background: repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.22) 2px,rgba(0,0,0,.22) 4px); pointer-events: none; z-index: 2; }

.fs-top { position: absolute; top: 0; left: 0; right: 0; z-index: 3; display: flex; align-items: center; gap: 10px; padding: 10px 14px; background: linear-gradient(rgba(0,0,0,.75),transparent); }
.fs-id  { font-size: 11px; color: rgba(255,255,255,.8); letter-spacing: .08em; }
.fs-live { display: flex; align-items: center; gap: 5px; font-size: 9px; color: #4caf7d; letter-spacing: 1.5px; margin-left: auto; }
.fs-err  { font-size: 9px; color: #e05260; letter-spacing: 1.5px; margin-left: auto; }
.live-dot { width: 6px; height: 6px; border-radius: 50%; background: #4caf7d; animation: lp 1.4s ease-in-out infinite; }

.fs-bot { position: absolute; bottom: 0; left: 0; right: 0; z-index: 3; display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: linear-gradient(transparent, rgba(0,0,0,.82)); }
.fs-loc { font-size: 12px; color: rgba(255,255,255,.75); font-weight: 500; flex: 1; }
.fs-time { font-size: 10px; color: rgba(255,255,255,.45); }
.fs-acc  { font-size: 9px; letter-spacing: .5px; }

.fs-ns { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; z-index: 1; }
.ns-txt { font-size: 14px; color: rgba(224,82,96,.6); letter-spacing: 3px; }
.ns-sub { font-size: 9px; color: rgba(255,255,255,.2); }

.fs-body { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 1; }
.fs-road { position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; gap: 0; opacity: .06; }
.road-line { flex: 1; border-bottom: 2px dashed #fff; margin: 0 20%; }
.fs-info { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.fs-cnt { font-size: 52px; font-weight: 700; line-height: 1; text-shadow: 0 0 30px currentColor; }
.fs-cnt-l { font-size: 11px; color: rgba(255,255,255,.4); letter-spacing: .5px; }
.fs-bars { position: absolute; right: 14px; bottom: 44px; display: flex; align-items: flex-end; gap: 2px; height: 40px; }
.fs-bar { width: 4px; border-radius: 1px 1px 0 0; min-height: 3px; }

/* 우측 사이드바 */
.cam-aside { background: var(--bg2); border: 1px solid var(--b); border-radius: 10px; padding: 12px; display: flex; flex-direction: column; overflow-y: auto; }

.cam-selector { display: flex; flex-direction: column; gap: 4px; flex: 1; overflow-y: auto; }
.csi { display: flex; align-items: center; gap: 8px; padding: 5px 7px; border-radius: 6px; border: 1px solid transparent; cursor: pointer; transition: all .2s; }
.csi:hover { background: rgba(255,255,255,.04); border-color: var(--b); }
.csi.active { background: rgba(62,201,214,.07); border-color: rgba(62,201,214,.25); }
.csi.offline { opacity: .6; }

.csi-thumb { width: 38px; height: 28px; background: #05080f; border-radius: 4px; overflow: hidden; position: relative; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.csi-scan { position: absolute; inset: 0; background: repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.3) 2px,rgba(0,0,0,.3) 4px); }
.csi-id { font-size: 10px; color: rgba(255,255,255,.5); position: relative; z-index: 1; }
.csi-st { position: absolute; top: 3px; right: 4px; font-size: 5px; z-index: 2; }
.csi-st.ok  { color: #4caf7d; }
.csi-st.err { color: #e05260; animation: lp 1.4s infinite; }

.csi-info { flex: 1; min-width: 0; }
.csi-name { font-size: 9px; color: var(--a); }
.csi-loc  { font-size: 9.5px; color: var(--t2); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.csi-cnt  { font-size: 9.5px; font-weight: 600; }

.agg-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px; margin-bottom: 10px; }
.ag { background: var(--card); border: 1px solid var(--b); border-radius: 5px; padding: 6px 4px; text-align: center; }
.ag-v { font-family: 'IBM Plex Mono',monospace; font-size: 14px; font-weight: 700; color: var(--t); line-height: 1; }
.ag-l { font-size: 7.5px; color: var(--t3); margin-top: 2px; text-transform: uppercase; letter-spacing: .4px; }

.acc-wrap { display: flex; align-items: center; gap: 7px; }
.acc-track { flex: 1; height: 6px; background: rgba(255,255,255,.06); border-radius: 3px; overflow: hidden; }
.acc-fill { height: 100%; width: 97%; background: linear-gradient(90deg, var(--a), #4caf7d); }
.acc-val { font-size: 11px; font-weight: 700; color: var(--a); flex-shrink: 0; }

/* ── 하단 캡처 그리드 ── */
.cap-section { background: var(--bg2); border: 1px solid var(--b); border-radius: 10px; padding: 12px 14px; display: flex; flex-direction: column; flex: 1; min-height: 0; }
.cap-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.cap-cnt { font-size: 10px; color: var(--t3); }

.cap-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(155px, 1fr)); gap: 8px; flex: 1; overflow-y: auto; align-content: start; }

.cap-card { background: var(--card); border: 1px solid var(--b); border-radius: 7px; overflow: hidden; transition: border-color .2s, transform .15s; }
.cap-card:hover { border-color: var(--a); transform: translateY(-1px); }
.cap-card.latest { border-color: rgba(62,201,214,.35); }

.cap-thumb { position: relative; height: 100px; background: #03050c; overflow: hidden; }
.cap-scan { position: absolute; inset: 0; background: repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.18) 2px,rgba(0,0,0,.18) 4px); pointer-events: none; z-index: 2; }

.cap-ts-bar { position: absolute; top: 0; left: 0; right: 0; z-index: 3; display: flex; justify-content: space-between; padding: 5px 7px; background: linear-gradient(rgba(0,0,0,.7),transparent); }
.cap-ts  { font-size: 8px; color: rgba(255,255,255,.7); }
.cap-cam { font-size: 8px; color: rgba(62,201,214,.8); }

.cap-vehicle { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; z-index: 1; }
.veh-silhouette { width: 80px; height: 36px; background: rgba(255,255,255,.04); border-radius: 6px 6px 3px 3px; border: 1px solid rgba(255,255,255,.06); position: relative; }
.veh-silhouette::before { content:''; position:absolute; top:-12px; left:12px; right:12px; height:12px; background:rgba(255,255,255,.04); border-radius:4px 4px 0 0; border:1px solid rgba(255,255,255,.06); border-bottom:none; }
.veh-silhouette::after  { content:''; position:absolute; bottom:-8px; left:6px; right:6px; height:8px; background:rgba(255,255,255,.03); border-radius:0 0 3px 3px; }

.cap-plate { position: absolute; bottom: 0; left: 0; right: 0; z-index: 3; padding: 4px 7px; background: linear-gradient(transparent, rgba(0,0,0,.85)); display: flex; justify-content: center; }
.cap-plate-num { font-size: 11px; font-weight: 700; color: #f5c518; letter-spacing: .04em; text-shadow: 0 0 10px rgba(245,197,24,.5); }

.cap-new { position: absolute; top: 6px; right: 6px; z-index: 4; font-size: 7px; color: var(--a); border: 1px solid var(--a); padding: 1px 5px; border-radius: 2px; background: rgba(62,201,214,.1); letter-spacing: 1px; animation: lp 1.4s infinite; }

.cap-meta { padding: 7px 9px; display: flex; flex-direction: column; gap: 3px; }
.cm-row { display: flex; align-items: center; justify-content: space-between; gap: 6px; }
.cm-k { font-size: 8.5px; color: var(--t3); flex-shrink: 0; }
.cm-v { font-size: 9.5px; color: var(--t2); }

.dir-badge { font-size: 7.5px; padding: 1px 6px; border: 1px solid; border-radius: 2px; letter-spacing: .8px; font-family: 'IBM Plex Mono',monospace; }
.dir-badge.IN  { color: #4caf7d; border-color: rgba(76,175,125,.4);  background: rgba(76,175,125,.08); }
.dir-badge.OUT { color: #d4845a; border-color: rgba(212,132,90,.4);  background: rgba(212,132,90,.08); }

.mono { font-family: 'IBM Plex Mono',monospace; }
.blink { animation: lp 1.4s ease-in-out infinite; }
@keyframes lp { 0%,100%{opacity:1} 50%{opacity:.15} }
</style>
