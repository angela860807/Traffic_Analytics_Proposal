<template>
  <div class="v2-tab-page">
    <div class="v2-page-h">
      <h2><i class="bi bi-search"></i> 차량 검색 / 전체 OCR 로그</h2>
      <div class="v2-page-actions">
        <span class="v2-live-badge" :class="{ off: paused }">
          <span class="v2-live-dot"></span>
          {{ paused ? '고정됨' : 'LIVE' }}
          <em v-if="!paused">· {{ secAgo }}초 전 갱신</em>
          <em v-else>· {{ snapshotCount }}건 스냅샷</em>
          <button
            v-if="paused && pendingCount > 0"
            class="v2-live-pending"
            @click="togglePause"
            :title="'대기 중인 신규 결과 ' + pendingCount + '건 — 클릭 시 실시간 복귀'"
          >
            +{{ pendingCount }}건 대기 <i class="bi bi-arrow-clockwise"></i>
          </button>
        </span>
        <button class="v2-btn-secondary" @click="togglePause" style="font-size:11px">
          <i :class="paused ? 'bi bi-unlock-fill' : 'bi bi-lock-fill'"></i>
          {{ paused ? '실시간 복귀' : '결과 고정' }}
        </button>
        <span style="font-size:12px;color:rgba(228,238,255,.6)">
          전체 {{ source.length }}건 · 결과 {{ filtered.length }}건
        </span>
      </div>
    </div>

    <section class="v2-card">
      <div class="v2-card-h">
        <span><i class="bi bi-funnel-fill"></i> 검색 조건</span>
        <button class="v2-btn-secondary" @click="resetSearch" style="font-size:11px">
          <i class="bi bi-arrow-counterclockwise"></i> 초기화
        </button>
      </div>
      <div class="v2-search-form">
        <div class="v2-form-row v2-form-row-range">
          <label>날짜 범위</label>
          <input type="date" v-model="q.dateFrom" />
          <span>~</span>
          <input type="date" v-model="q.dateTo" />
          <div class="v2-form-presets">
            <button type="button" class="v2-preset" @click="presetToday">오늘</button>
            <button type="button" class="v2-preset" @click="presetRecent7">최근 7일</button>
          </div>
        </div>
        <div class="v2-form-row v2-form-row-range">
          <label>시간 범위</label>
          <input type="time" v-model="q.timeFrom" step="1" />
          <span>~</span>
          <input type="time" v-model="q.timeTo" step="1" />
        </div>
        <div class="v2-form-row">
          <label>차량 번호</label>
          <input type="text" v-model="q.plate" placeholder="예: 128가 4567" />
        </div>
        <div class="v2-form-row">
          <label>카메라</label>
          <select v-model="q.cam">
            <option value="">전체</option>
            <option v-for="c in cameraFeeds" :key="c.name" :value="c.name">{{ c.name }}</option>
          </select>
        </div>
        <div class="v2-form-row">
          <label>흐름 방향</label>
          <select v-model="q.dir">
            <option value="">전체</option>
            <option value="in">진입 (IN)</option>
            <option value="out">이탈 (OUT)</option>
          </select>
        </div>
        <div class="v2-form-row">
          <label>인식 상태</label>
          <select v-model="q.status">
            <option value="">전체</option>
            <option value="FLOW_EVENT_CREATED">정상</option>
            <option value="OCR_FAILED">OCR 실패</option>
            <option value="DUPLICATE_SKIPPED">중복</option>
          </select>
        </div>
        <div class="v2-form-row">
          <label>최소 신뢰도</label>
          <input type="number" v-model.number="q.minConf" min="0" max="100" placeholder="0~100" />
        </div>
      </div>
    </section>

    <section class="v2-card" :class="{ 'v2-card-frozen': paused }">
      <div class="v2-card-h">
        <span><i class="bi bi-card-list"></i> 결과 ({{ filtered.length }}건)</span>
      </div>
      <div class="v2-log-table">
        <div class="v2-lt-head">
          <span>번호</span><span>인식 시간</span><span>카메라</span>
          <span>차량 번호</span><span>상태</span><span>흐름 방향</span><span>신뢰도</span>
        </div>
        <div
          v-for="(p, i) in filtered" :key="p.id"
          class="v2-lt-row"
          :class="{ 'v2-lt-new': !paused && newIds.has(p.id) }"
          @click="modalPlate = p"
          title="클릭하면 OCR 인식 상세 보기"
        >
          <span>{{ i + 1 }}</span>
          <span class="mono">{{ todayStr }} {{ p.time }}</span>
          <span>{{ p.cam }}</span>
          <span class="mono">{{ p.status === 'OCR_FAILED' ? '미인식' : p.num }}</span>
          <span class="v2-plate-status" :class="`v2-plate-status-${plateStatus(p.status).cls}`">
            <i :class="plateStatus(p.status).icon"></i> {{ plateStatus(p.status).label }}
          </span>
          <span class="v2-lt-dir" :class="p.dir">
            <i :class="p.dir === 'in' ? 'bi bi-arrow-down-left-circle-fill' : 'bi bi-arrow-up-right-circle-fill'"></i>
            {{ dirLabel(p.dir) }}
          </span>
          <span class="v2-lt-conf">{{ p.conf }}%</span>
        </div>
        <div v-if="filtered.length === 0" class="v2-empty">해당 조건의 인식 결과가 없습니다.</div>
      </div>
    </section>

    <!-- OCR 인식 상세 모달 -->
    <Teleport to="body">
      <div v-if="modalPlate" class="v2-modal" @click.self="modalPlate = null">
        <div class="v2-modal-box v2-ocr-modal">
          <div class="v2-modal-h">
            <span>
              <i class="bi bi-upc-scan"></i> OCR 인식 상세
              <span class="v2-plate-status" :class="`v2-plate-status-${plateStatus(modalPlate.status).cls}`" style="margin-left:8px">
                <i :class="plateStatus(modalPlate.status).icon"></i>
                {{ plateStatus(modalPlate.status).label }}
              </span>
            </span>
            <button @click="modalPlate = null"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="v2-ocr-body">
            <div class="v2-ocr-photo">
              <img v-if="plateImg(modalPlate)" :src="plateImg(modalPlate)" class="v2-ocr-photo-img" :alt="modalPlate.num" />
              <div v-else class="v2-ocr-photo-empty">
                <i class="bi bi-image"></i>
                <span>이미지 없음</span>
              </div>
              <div class="v2-plate-vis">
                <div class="v2-plate-num mono">
                  {{ modalPlate.status === 'OCR_FAILED' ? '미인식' : modalPlate.num }}
                </div>
              </div>
            </div>
            <div class="v2-ocr-info">
              <div class="v2-ocr-row">
                <span class="v2-ocr-k">인식 시간</span>
                <span class="v2-ocr-v">{{ todayStr }} {{ modalPlate.time }}</span>
              </div>
              <div class="v2-ocr-row">
                <span class="v2-ocr-k">카메라</span>
                <span class="v2-ocr-v">{{ modalPlate.cam }}</span>
              </div>
              <div class="v2-ocr-row">
                <span class="v2-ocr-k">흐름 방향</span>
                <span class="v2-ocr-v" :class="`v2-ocr-dir-${modalPlate.dir}`">
                  <i :class="modalPlate.dir === 'in' ? 'bi bi-arrow-down-left-circle-fill' : 'bi bi-arrow-up-right-circle-fill'"></i>
                  {{ dirLabel(modalPlate.dir) }}
                </span>
              </div>
              <div class="v2-ocr-row">
                <span class="v2-ocr-k">신뢰도</span>
                <span class="v2-ocr-v v2-ocr-conf">{{ modalPlate.conf }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { reactive, computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useDashboardData } from '@/composables/useDashboardData'

const { plates, cameraFeeds, todayStr, dirLabel, plateImg, plateStatus } = useDashboardData()

const q = reactive({
  dateFrom: '', dateTo: '',
  timeFrom: '', timeTo: '',
  plate: '', cam: '', dir: '', status: '', minConf: null,
})

function presetToday() {
  q.dateFrom = todayStr
  q.dateTo = todayStr
}
function presetRecent7() {
  const base = new Date(todayStr + 'T00:00:00')
  const from = new Date(base.getTime() - 6 * 24 * 60 * 60 * 1000)
  q.dateFrom = from.toISOString().slice(0, 10)
  q.dateTo = todayStr
}

/* 실시간 / 고정 모드 */
const paused = ref(false)
const frozenPlates = ref([])
const lastUpdate = ref(Date.now())
const now = ref(Date.now())
const newIds = ref(new Set())
const pendingCount = ref(0)

const source = computed(() => paused.value ? frozenPlates.value : plates.value)
const snapshotCount = computed(() => frozenPlates.value.length)
const secAgo = computed(() => Math.max(0, Math.floor((now.value - lastUpdate.value) / 1000)))

let prevIds = new Set(plates.value.map(p => p.id))
let tickTimer = null
let highlightTimer = null

watch(() => plates.value.map(p => p.id).join(','), () => {
  const cur = new Set(plates.value.map(p => p.id))
  const added = [...cur].filter(id => !prevIds.has(id))
  if (paused.value) {
    if (added.length) pendingCount.value += added.length
  } else {
    lastUpdate.value = Date.now()
    if (added.length) {
      newIds.value = new Set(added)
      clearTimeout(highlightTimer)
      highlightTimer = setTimeout(() => { newIds.value = new Set() }, 1800)
    }
  }
  prevIds = cur
})

function onEsc(e) { if (e.key === 'Escape') modalPlate.value = null }
onMounted(() => {
  tickTimer = setInterval(() => now.value = Date.now(), 1000)
  document.addEventListener('keydown', onEsc)
})
onUnmounted(() => {
  clearInterval(tickTimer)
  clearTimeout(highlightTimer)
  document.removeEventListener('keydown', onEsc)
})

function togglePause() {
  if (!paused.value) {
    frozenPlates.value = [...plates.value]
    pendingCount.value = 0
    paused.value = true
  } else {
    paused.value = false
    pendingCount.value = 0
    lastUpdate.value = Date.now()
    prevIds = new Set(plates.value.map(p => p.id))
  }
}

const filtered = computed(() => source.value.filter(p => {
  const pDate = p.date || todayStr
  const pTime = p.time || ''
  return (
    (!q.dateFrom || pDate >= q.dateFrom) &&
    (!q.dateTo   || pDate <= q.dateTo) &&
    (!q.timeFrom || pTime >= q.timeFrom) &&
    (!q.timeTo   || pTime <= q.timeTo) &&
    (!q.plate    || (p.num || '').includes(q.plate.trim())) &&
    (!q.cam      || p.cam === q.cam) &&
    (!q.dir      || p.dir === q.dir) &&
    (!q.status   || (p.status || 'FLOW_EVENT_CREATED') === q.status) &&
    (q.minConf == null || q.minConf === '' || p.conf >= q.minConf)
  )
}))

const modalPlate = ref(null)

function resetSearch() {
  Object.assign(q, {
    dateFrom: '', dateTo: '',
    timeFrom: '', timeTo: '',
    plate: '', cam: '', dir: '', status: '', minConf: null,
  })
}
</script>
