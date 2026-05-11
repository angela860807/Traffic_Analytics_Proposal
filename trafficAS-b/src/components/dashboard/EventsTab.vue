<template>
  <div class="v2-tab-page">
    <div class="v2-page-h">
      <h2><i class="bi bi-bell-fill"></i> 이벤트 관리</h2>
      <div class="v2-page-actions">
        <select v-model="eventFilter" class="v2-select">
          <option value="all">전체 이벤트</option>
          <option value="critical">중요</option>
          <option value="warning">경고</option>
          <option value="info">정보</option>
        </select>
        <button class="v2-btn-primary"><i class="bi bi-arrow-clockwise"></i> 새로고침</button>
      </div>
    </div>

    <div class="v2-events-summary">
      <div class="v2-evs-card v2-evs-critical">
        <i class="bi bi-exclamation-octagon-fill"></i>
        <div><div class="v2-evs-n">{{ eventsByLevel.critical }}</div><div class="v2-evs-l">중요</div></div>
      </div>
      <div class="v2-evs-card v2-evs-warning">
        <i class="bi bi-exclamation-triangle-fill"></i>
        <div><div class="v2-evs-n">{{ eventsByLevel.warning }}</div><div class="v2-evs-l">경고</div></div>
      </div>
      <div class="v2-evs-card v2-evs-info">
        <i class="bi bi-info-circle-fill"></i>
        <div><div class="v2-evs-n">{{ eventsByLevel.info }}</div><div class="v2-evs-l">정보</div></div>
      </div>
      <div class="v2-evs-card v2-evs-total">
        <i class="bi bi-bell-fill"></i>
        <div><div class="v2-evs-n">{{ eventsByLevel.total }}</div><div class="v2-evs-l">전체</div></div>
      </div>
    </div>

    <section class="v2-card">
      <div class="v2-card-h">
        <span><i class="bi bi-list-ul"></i> 이벤트 로그</span>
      </div>
      <div class="v2-event-table">
        <div class="v2-et-head">
          <span>시각</span><span>등급</span><span>카메라</span><span>이벤트</span><span>조치</span>
        </div>
        <div v-for="e in filteredEvents" :key="e.id" class="v2-et-row">
          <span class="mono">{{ e.time }}</span>
          <span class="v2-et-level" :class="e.level">{{ levelLabel(e.level) }}</span>
          <span>{{ e.cam }}</span>
          <span>{{ e.msg }}</span>
          <button class="v2-et-btn">상세</button>
        </div>
        <div v-if="filteredEvents.length === 0" class="v2-empty">해당하는 이벤트가 없습니다.</div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDashboardData } from '@/composables/useDashboardData'

const { levelLabel } = useDashboardData()

const eventFilter = ref('all')

const eventsList = [
  { id: 1, time: '2024-05-28 14:32:18', level: 'critical', cam: '테헤란로 교차로', msg: '교차로 혼잡 감지 — 진입 +42%' },
  { id: 2, time: '2024-05-28 14:28:42', level: 'warning',  cam: '강남역 사거리',   msg: 'CAM-03 OCR 인식률 저하 (78%)' },
  { id: 3, time: '2024-05-28 14:15:09', level: 'warning',  cam: '반포IC',          msg: '이탈 차량 급증 — 평소 대비 +35%' },
  { id: 4, time: '2024-05-28 13:58:21', level: 'info',     cam: '올림픽대로',      msg: '교통 흐름 원활 전환' },
  { id: 5, time: '2024-05-28 13:45:33', level: 'info',     cam: '시스템',          msg: 'OCR 파이프라인 정상 가동' },
  { id: 6, time: '2024-05-28 13:30:11', level: 'warning',  cam: '잠실역 사거리',   msg: '진입 트래픽 급증 — +42%' },
  { id: 7, time: '2024-05-28 13:02:08', level: 'info',     cam: '양재역 사거리',   msg: '흐름 정상화' },
  { id: 8, time: '2024-05-28 12:36:02', level: 'critical', cam: '남부터미널',      msg: '정체 시작 — 흐름 정체율 88%' },
  { id: 9, time: '2024-05-28 12:14:48', level: 'info',     cam: '석촌역 사거리',   msg: '이탈 차량 통행 증가 추세' },
  { id:10, time: '2024-05-28 11:55:30', level: 'info',     cam: '강남구',          msg: '전역 평균 정상 운행' },
  { id:11, time: '2024-05-28 11:30:12', level: 'info',     cam: '시스템',          msg: '중복 감지 178건 자동 제거 완료' },
  { id:12, time: '2024-05-28 11:00:05', level: 'info',     cam: '시스템',          msg: 'WebSocket 연결 정상' },
]

const filteredEvents = computed(() =>
  eventFilter.value === 'all' ? eventsList : eventsList.filter(e => e.level === eventFilter.value)
)
const eventsByLevel = computed(() => ({
  critical: eventsList.filter(e => e.level === 'critical').length,
  warning:  eventsList.filter(e => e.level === 'warning').length,
  info:     eventsList.filter(e => e.level === 'info').length,
  total:    eventsList.length,
}))
</script>
