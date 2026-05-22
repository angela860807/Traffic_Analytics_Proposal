<template>
  <div class="ct">
    <div class="head">
      <span class="olabel"><span class="odot"></span>실시간 관제 어시스턴트</span>
      <span v-if="isDemoMode" class="demo-badge" title="백엔드 미연동 — 샘플 이벤트 시뮬레이션 중">DEMO</span>
      <span class="meta mono">{{ nowTime }} · 카메라 {{ stats.online }}/{{ totalCamCount }} 가동</span>
      <button class="auto-toggle" :class="{ on: autoPush }" @click="autoPush = !autoPush"
              :title="autoPush ? '이벤트 자동 표시 끄기' : '이벤트 자동 표시 켜기'">
        <i :class="autoPush ? 'bi bi-broadcast' : 'bi bi-broadcast-pin'"></i>
        {{ autoPush ? 'LIVE' : 'OFF' }}
      </button>
      <button class="reset" @click="reset" title="대화 초기화">
        <i class="bi bi-arrow-counterclockwise"></i>
      </button>
    </div>

    <!-- 빠른 명령 칩 -->
    <div class="quick">
      <button v-for="q in quickActions" :key="q.label" class="qchip" @click="send(q.q)">
        <i :class="q.icon"></i> {{ q.label }}
      </button>
    </div>

    <div ref="scrollEl" class="msgs">
      <div v-for="m in msgs" :key="m.id" class="msg" :class="{ mine: m.mine }">
        <div class="av">{{ m.mine ? '😀' : '🤖' }}</div>
        <div class="body">
          <div class="name">{{ m.mine ? '나' : 'TAS' }}</div>
          <div class="bubble" :class="{ 'data-bubble': m.isData }">
            <span v-html="m.text"></span>
          </div>
          <div class="time mono">{{ m.time }}</div>
        </div>
      </div>
      <div v-if="typing" class="msg">
        <div class="av">🤖</div>
        <div class="body"><div class="bubble typing"><span></span><span></span><span></span></div></div>
      </div>
    </div>

    <div class="bar">
      <input
        v-model="input"
        class="ci"
        placeholder="실시간 시스템에 질문 (예: 지금 가동 카메라, 혼잡 도로, 오늘 진입)"
        @keydown.enter="() => send()"
      />
      <button class="sbtn" :disabled="!input.trim() || typing" @click="() => send()">
        <i class="bi bi-send-fill"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted, watch } from "vue"
import { useDashboardData } from "@/composables/useDashboardData"

const {
  totalVehicles, inCount, outCount, dupRemoved,
  plates, cameraGroups, stats, totalCamCount,
  camCongestion, notifications, mutedCameras, todayStr,
  pushNotification,
} = useDashboardData()

/* ── 실시간 데이터 응답 (Q&A와의 차별화 핵심) ── */
const liveAnswers = [
  { kw: ['지금', '현재 상태', '시스템 상태'], a: () =>
    `🟢 <b>현재 시스템 정상 가동 중</b><br>· 카메라: ${stats.value.online} / ${totalCamCount.value}대 가동<br>· 오프라인: ${stats.value.offline}대, 오류: ${stats.value.error}대<br>· 총 감지 차량(오늘): ${totalVehicles.value.toLocaleString()}대` },

  { kw: ['카메라', '몇대', '몇 대', '가동'], a: () =>
    `📷 <b>카메라 현황</b><br>· 강남구 ${cameraGroups[0].cams.filter(c=>c.status==='online').length}/${cameraGroups[0].cams.length}<br>· 서초구 ${cameraGroups[1].cams.filter(c=>c.status==='online').length}/${cameraGroups[1].cams.length}<br>· 송파구 ${cameraGroups[2].cams.filter(c=>c.status==='online').length}/${cameraGroups[2].cams.length}<br>· 총 가동률: <b>${Math.round((stats.value.online / totalCamCount.value) * 100)}%</b>` },

  { kw: ['진입', '이탈', '통행', '차량 수', '오늘 차량'], a: () =>
    `🚗 <b>오늘 차량 통행 (${todayStr})</b><br>· 진입(IN): ${inCount.value.toLocaleString()}대<br>· 이탈(OUT): ${outCount.value.toLocaleString()}대<br>· 중복 제거: ${dupRemoved.value}건<br>· 순 통행량: <b>${(inCount.value + outCount.value).toLocaleString()}대</b>` },

  { kw: ['혼잡', '정체', '막힘'], a: () => {
    const sorted = Object.entries(camCongestion.value).sort((a,b) => b[1]-a[1]).slice(0, 3)
    return `🔥 <b>현재 가장 혼잡한 지점 TOP 3</b><br>${sorted.map((c,i) => `${i+1}. ${c[0]} — <b>${Math.round(c[1]*100)}%</b>`).join('<br>')}` } },

  { kw: ['알림', '경고', '알람'], a: () => {
    const recent = notifications.value.slice(0, 3)
    return recent.length === 0
      ? '✅ 현재 활성 알림이 없습니다.'
      : `🔔 <b>최근 알림 ${recent.length}건</b><br>${recent.map(n => `· [${n.time}] ${n.msg}`).join('<br>')}`
  } },

  { kw: ['ocr', '인식', '번호판 몇'], a: () => {
    const ok = plates.value.filter(p => p.status === 'FLOW_EVENT_CREATED').length
    const fail = plates.value.filter(p => p.status === 'OCR_FAILED').length
    const dup = plates.value.filter(p => p.status === 'DUPLICATE_SKIPPED').length
    const total = plates.value.length
    return `🔍 <b>최근 OCR 인식 현황</b><br>· 정상: ${ok}건<br>· 실패: ${fail}건<br>· 중복: ${dup}건<br>· 인식률: <b>${total ? Math.round((ok/total)*100) : 0}%</b>` } },

  { kw: ['마지막', '최근 차량', '최근 번호판'], a: () => {
    const last = plates.value[0]
    if (!last) return '아직 인식된 차량이 없습니다.'
    return `🚘 <b>마지막 인식 차량</b><br>· 번호: <b>${last.num}</b><br>· 카메라: ${last.cam}<br>· 시각: ${last.time}<br>· 신뢰도: ${last.conf}%<br>· 방향: ${last.dir === 'in' ? '진입' : '이탈'}` } },

  { kw: ['오프라인', '끊김', '죽은 카메라'], a: () => {
    const off = cameraGroups.flatMap(g => g.cams).filter(c => c.status !== 'online')
    return off.length === 0
      ? '✅ 모든 카메라가 정상 가동 중입니다.'
      : `⚠️ <b>비정상 카메라 ${off.length}대</b><br>${off.map(c => `· ${c.name} — ${c.status === 'offline' ? '오프라인' : '오류'}`).join('<br>')}`
  } },

  { kw: ['시간', '몇시', '몇 시'], a: () => `⏰ 현재 시각은 <b>${new Date().toLocaleString('ko-KR')}</b> 입니다.` },

  { kw: ['음소거', '뮤트', '점검'], a: () =>
    mutedCameras.value.size === 0
      ? '🔔 현재 음소거된 카메라가 없습니다.'
      : `🔕 음소거 중인 카메라 ${mutedCameras.value.size}대:<br>${[...mutedCameras.value].map(n => `· ${n}`).join('<br>')}`
  },
]

/* ── 정적 FAQ (시스템 사용법 등) ── */
const staticAnswers = [
  { kw: ['안녕', 'hello', '하이'], a: '안녕하세요! 실시간 관제 어시스턴트입니다. 위 빠른 명령을 누르거나 "지금 가동 카메라", "혼잡 도로" 같이 물어보세요.' },
  { kw: ['로그인', '계정'], a: '관리자 계정: admin@trafficAS.com / admin1234' },
  { kw: ['대시보드 사용', '대시보드 어디', '사용법'], a: '관리자 로그인 후 헤더의 부서별 대시보드(교통정보센터/단속관리팀/교통분석팀/시설운영팀/경영전략본부)로 진입하세요.' },
  { kw: ['지도', '히트맵', '도로'], a: '교통정보센터 등 부서 대시보드에서 Leaflet 기반 실시간 혼잡도 지도를 제공합니다. OSM 도로 데이터 사용.' },
  { kw: ['기술', '스택'], a: 'Vue 3 + Vite, Spring Boot, FastAPI, YOLO·OCR, Leaflet, ECharts. 외부 의존성 4개로 최소화.' },
  { kw: ['연락', '문의', '이메일'], a: '문의: chlehdgb123@naver.com / GitHub: angela860807/Traffic_Analytics_Proposal' },
  { kw: ['감사', '고마', 'thank'], a: '도움이 되었다면 다행입니다 😊' },
]

const DEFAULT_A = '실시간 시스템 정보를 물어보세요. 예: "지금 가동 카메라", "혼잡 도로 TOP 3", "오늘 진입 차량", "최근 알림", "마지막 인식 차량"'

const quickActions = [
  { label: '시스템 상태', q: '지금 시스템 상태', icon: 'bi bi-activity' },
  { label: '카메라 현황', q: '카메라 가동', icon: 'bi bi-camera-video-fill' },
  { label: '혼잡 도로 TOP3', q: '혼잡 도로', icon: 'bi bi-fire' },
  { label: '오늘 통행량', q: '오늘 진입 이탈', icon: 'bi bi-car-front-fill' },
  { label: '최근 알림', q: '최근 알림', icon: 'bi bi-bell-fill' },
]

const now = () => new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
const nowTime = ref(now())
let clockT = null

function answer(q) {
  const lo = q.toLowerCase()
  const live = liveAnswers.find(k => k.kw.some(kw => lo.includes(kw)))
  if (live) return { text: live.a(), isData: true }
  const stat = staticAnswers.find(k => k.kw.some(kw => lo.includes(kw)))
  if (stat) return { text: stat.a, isData: false }
  return { text: DEFAULT_A, isData: false }
}

const scrollEl = ref(null)
const input = ref('')
const typing = ref(false)
const autoPush = ref(true)   // 시스템 이벤트 자동 푸시 ON/OFF
const msgs = ref([
  { id: 1, mine: false, text: '안녕하세요! 실시간 관제 어시스턴트입니다. 위 빠른 명령 버튼을 누르거나 시스템 상태를 직접 물어보세요.<br><small>💡 우측 상단 LIVE 버튼이 켜져있으면 새 이벤트가 자동으로 표시됩니다.</small>', time: now(), isData: false },
])
let nextId = 2

async function scroll() {
  await nextTick()
  if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight
}

function pushBotMessage(text, isData = false) {
  msgs.value.push({ id: nextId++, mine: false, text, time: now(), isData })
  // 메시지 너무 많이 쌓이지 않게 100개 제한
  if (msgs.value.length > 100) msgs.value = msgs.value.slice(-100)
  scroll()
}

async function send(prefilled) {
  const q = (prefilled ?? input.value).trim()
  if (!q || typing.value) return
  msgs.value.push({ id: nextId++, mine: true, text: q, time: now(), isData: false })
  input.value = ''
  typing.value = true
  await scroll()
  await new Promise(r => setTimeout(r, 300 + Math.random() * 250))
  const { text, isData } = answer(q)
  typing.value = false
  pushBotMessage(text, isData)
}

function reset() {
  msgs.value = [{ id: 1, mine: false, text: '대화가 초기화되었습니다.', time: now(), isData: false }]
  nextId = 2
}

/* ── 자동 이벤트 푸시 (실시간 채팅의 핵심) ──
 * notifications 배열에 새 항목 들어오면 봇이 자동으로 메시지로 표시
 * autoPush off면 무시. 채팅 마운트 후 들어온 알림만 푸시(과거 알림은 제외).
 */
const seenNotifIds = new Set()
onMounted(() => {
  // 마운트 시점 알림은 "이미 본 것"으로 등록 (과거 알림 폭주 방지)
  notifications.value.forEach(n => seenNotifIds.add(n.id))
})

watch(notifications, (curr) => {
  if (!autoPush.value) return
  curr.forEach(n => {
    if (seenNotifIds.has(n.id)) return
    seenNotifIds.add(n.id)
    const icon = n.color === '#e05260' ? '🚨' : n.color === '#d4845a' ? '⚠️' : 'ℹ️'
    pushBotMessage(`${icon} <b>새 이벤트</b> [${n.time}]<br>${n.msg}`, true)
  })
}, { deep: true })

/* 헤더 상태 칩 — 5초마다 갱신 */
onMounted(() => { clockT = setInterval(() => nowTime.value = now(), 5000) })
onUnmounted(() => clearInterval(clockT))

/* ── 데모 시뮬레이터 (조건부 활성화) ──
 * 백엔드 미연동 상태에서만 가짜 이벤트 생성. 운영 환경에선 자동으로 OFF.
 *
 * 활성 조건:
 *   - DEV 모드 (npm run dev) 이거나
 *   - PROD인데 VITE_FASTAPI_BASE_URL이 비어있는 경우 (백엔드 미연동)
 *
 * 백엔드 URL이 설정되면 = 실제 알림이 흘러올 거라 시뮬레이터 자동 비활성.
 */
const isDemoMode = import.meta.env.DEV || !import.meta.env.VITE_FASTAPI_BASE_URL

const SAMPLE_EVENTS = [
  { msg: () => `테헤란로 교차로 인식률 ${88 + Math.floor(Math.random() * 10)}%`, lv: 'info' },
  { msg: () => `CAM-${String(Math.floor(Math.random()*8)+1).padStart(2,'0')} 강남역 OCR 신뢰도 ${65 + Math.floor(Math.random()*15)}%로 저하`, lv: 'warning' },
  { msg: () => `잠실역 사거리 진입 차량 +${10 + Math.floor(Math.random()*30)}대 (5분 평균 대비)`, lv: 'warning' },
  { msg: () => `반포IC 이탈 트래픽 정상화`, lv: 'info' },
  { msg: () => `남부터미널 정체 시작 — 평균 ${8 + Math.floor(Math.random()*10)} km/h`, lv: 'critical' },
  { msg: () => `${['역삼','선릉','삼성','강남구청'][Math.floor(Math.random()*4)]}역 사거리 차량 감지 +${5 + Math.floor(Math.random()*15)}대`, lv: 'info' },
  { msg: () => `OCR 파이프라인 처리 ${1200 + Math.floor(Math.random()*300)}건/분`, lv: 'info' },
  { msg: () => `CAM-${String(Math.floor(Math.random()*8)+1).padStart(2,'0')} 프레임 수신 지연 ${5 + Math.floor(Math.random()*15)}초`, lv: 'warning' },
  { msg: () => `중복 차량 ${5 + Math.floor(Math.random()*20)}건 자동 제거`, lv: 'info' },
  { msg: () => `올림픽대로 흐름 ${['원활', '서행', '정체'][Math.floor(Math.random()*3)]} 전환`, lv: 'info' },
]
let simT = null
function scheduleNext() {
  const delay = 8000 + Math.random() * 7000  // 8~15초 랜덤
  simT = setTimeout(() => {
    if (autoPush.value) {
      const e = SAMPLE_EVENTS[Math.floor(Math.random() * SAMPLE_EVENTS.length)]
      pushNotification(e.msg(), e.lv)
    }
    scheduleNext()
  }, delay)
}
onMounted(() => {
  // 시뮬레이터는 DEMO 모드(개발 환경 or 백엔드 미연결)에서만 동작
  if (isDemoMode) scheduleNext()
})
onUnmounted(() => clearTimeout(simT))
</script>

<style scoped>
.ct { display: flex; flex-direction: column; height: 100%; }
.head {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 20px; border-bottom: 1px solid var(--b); background: var(--bg2);
}
.olabel { font-family: "JetBrains Mono", monospace; font-size: 11.5px; color: var(--in); display: flex; align-items: center; gap: 5px; }
.odot { width: 5px; height: 5px; border-radius: 50%; background: var(--in); animation: livePulse 1.5s ease-in-out infinite; }
.meta { font-family: "JetBrains Mono", monospace; font-size: 11px; color: var(--t3); flex: 1; }
.demo-badge {
  font-family: "JetBrains Mono", monospace;
  font-size: 10px; font-weight: 700; letter-spacing: 0.1em;
  padding: 3px 8px; border-radius: 3px;
  background: rgba(251, 146, 60, 0.15);
  color: #fb923c;
  border: 1px solid rgba(251, 146, 60, 0.35);
  cursor: help;
}
.reset {
  display: inline-flex; align-items: center;
  padding: 6px 9px; background: none; border: 1px solid var(--b); border-radius: 4px;
  font-family: "JetBrains Mono", monospace; font-size: 11px; color: var(--t3);
  cursor: pointer; transition: all 0.2s;
}
.reset:hover { border-color: var(--ba); color: var(--a); }

.auto-toggle {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 5px 10px; border-radius: 4px;
  font-family: "JetBrains Mono", monospace; font-size: 11px; font-weight: 700;
  letter-spacing: 0.05em;
  background: rgba(148, 163, 184, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.3);
  color: rgba(148, 163, 184, 0.9);
  cursor: pointer; transition: all 0.18s;
}
.auto-toggle.on {
  background: rgba(52, 211, 153, 0.12);
  border-color: rgba(52, 211, 153, 0.4);
  color: #34d399;
}
.auto-toggle.on i { animation: livePulse 1.4s ease-in-out infinite; }
.auto-toggle:hover { transform: translateY(-1px); }

/* 빠른 명령 칩 */
.quick {
  display: flex; gap: 6px; padding: 12px 20px;
  background: var(--bg2); border-bottom: 1px solid var(--b);
  flex-wrap: wrap;
}
.qchip {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 7px 12px; border-radius: 6px;
  background: rgba(96, 165, 250, 0.08);
  border: 1px solid rgba(96, 165, 250, 0.25);
  color: var(--a); font-size: 12.5px; font-weight: 500;
  cursor: pointer; transition: all 0.18s; white-space: nowrap;
}
.qchip:hover { background: rgba(96, 165, 250, 0.18); border-color: rgba(96, 165, 250, 0.5); transform: translateY(-1px); }
.qchip i { font-size: 12px; }

.msgs { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.msgs::-webkit-scrollbar { width: 3px; }
.msgs::-webkit-scrollbar-thumb { background: var(--b); border-radius: 2px; }

.msg { display: flex; gap: 10px; align-items: flex-start; }
.msg.mine { flex-direction: row-reverse; }
.av {
  width: 36px; height: 36px; border-radius: 50%; border: 1px solid var(--b);
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; flex-shrink: 0; background: var(--bg2);
}
.body { max-width: 75%; }
.name { font-family: "JetBrains Mono", monospace; font-size: 11.5px; color: var(--t3); margin-bottom: 4px; }
.msg.mine .name { text-align: right; }

.bubble {
  padding: 12px 16px; border-radius: 10px; font-size: 14.5px; line-height: 1.7;
  background: var(--card); border: 1px solid var(--b); color: var(--t);
  white-space: pre-wrap; word-break: break-word;
}
.bubble :deep(b) { color: var(--a); font-weight: 700; }
.msg.mine .bubble { background: var(--a); border-color: var(--a); color: #fff; }
.msg.mine .bubble :deep(b) { color: #fff; }

/* 실시간 데이터 응답은 다른 스타일 */
.bubble.data-bubble {
  background: rgba(96, 165, 250, 0.05);
  border-color: rgba(96, 165, 250, 0.25);
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  line-height: 1.85;
}

.bubble.typing { display: flex; align-items: center; gap: 4px; padding: 14px 18px; min-width: 56px; }
.bubble.typing span { width: 6px; height: 6px; border-radius: 50%; background: var(--t3); animation: bounce 1.2s ease-in-out infinite; }
.bubble.typing span:nth-child(2) { animation-delay: 0.2s; }
.bubble.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-5px); opacity: 1; }
}

.time { font-family: "JetBrains Mono", monospace; font-size: 11px; color: var(--t3); margin-top: 5px; }
.msg.mine .time { text-align: right; }

.bar { padding: 14px 20px; border-top: 1px solid var(--b); display: flex; gap: 10px; background: var(--bg2); }
.ci {
  flex: 1; background: var(--bg); border: 1px solid var(--b); border-radius: 6px;
  padding: 12px 16px; font-size: 14.5px; color: var(--t);
  font-family: "Noto Sans KR", sans-serif; outline: none; transition: border-color 0.2s;
}
.ci:focus { border-color: var(--ba); }
.ci::placeholder { color: var(--t3); }
.sbtn {
  padding: 12px 22px; background: var(--a); color: var(--bg);
  border: none; border-radius: 6px;
  font-family: "JetBrains Mono", monospace; font-size: 13.5px; font-weight: 500;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  min-width: 60px; transition: opacity 0.2s;
}
.sbtn:hover:not(:disabled) { opacity: 0.87; }
.sbtn:disabled { opacity: 0.45; cursor: not-allowed; }
</style>
