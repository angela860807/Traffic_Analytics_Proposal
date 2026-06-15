// 예지보전 모듈 API 클라이언트 — 백엔드 계약 §3 외부 API 15개 함수
// 모든 호출은 공유 apiClient를 경유 (view/component에서 axios 직접 호출 금지)

import { apiClient } from './client'

const BASE = '/api/v1/predictive'

// ────────────────────────────────────────────────────────────
// 시간/페이지/쿼리 헬퍼
// ────────────────────────────────────────────────────────────

// ISO-8601 with offset (예: 2026-06-09T14:05:00+09:00) — toISOString()이 UTC만 주므로 직접 포맷
export function isoWithOffset(date = new Date()) {
  const d = date instanceof Date ? date : new Date(date)
  const tzMin = -d.getTimezoneOffset()
  const sign = tzMin >= 0 ? '+' : '-'
  const abs = Math.abs(tzMin)
  const hh = String(Math.floor(abs / 60)).padStart(2, '0')
  const mm = String(abs % 60).padStart(2, '0')
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T`
    + `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}${sign}${hh}:${mm}`
}

// null/undefined 제거 + Array는 콤마 join
function cleanParams(params = {}) {
  const out = {}
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === '') continue
    out[k] = Array.isArray(v) ? v.join(',') : v
  }
  return out
}

// ────────────────────────────────────────────────────────────
// 정렬 화이트리스트 (§7) — 클라에서 미리 차단해 400 호출 방지
// ────────────────────────────────────────────────────────────

export const SORT_ALLOWED = Object.freeze({
  cameras: ['cameraName', 'healthScore', 'latestSampledAt'],
  anomalyEvents: ['firstDetectedAt', 'lastDetectedAt', 'severity', 'anomalyScore'],
  maintenanceTickets: ['createdAt', 'dueAckAt', 'dueStartAt', 'priority'],
})

function validateSort(sort, allowed) {
  if (!sort) return undefined
  const [field] = String(sort).split(',')
  return allowed.includes(field) ? sort : undefined
}

// ────────────────────────────────────────────────────────────
// 3-1. 운영 요약
// ────────────────────────────────────────────────────────────
export function getSummary({ dataSource = 'REAL' } = {}) {
  return apiClient
    .get(`${BASE}/summary`, { params: cleanParams({ dataSource }) })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-2. 카메라 운영 상태 (페이지)
// ────────────────────────────────────────────────────────────
export function listCameras({
  zoneId,
  healthStatus,
  dataSource = 'REAL',
  page = 0,
  size = 20,
  sort = 'healthScore,asc',
} = {}) {
  return apiClient
    .get(`${BASE}/cameras`, {
      params: cleanParams({
        zoneId, healthStatus, dataSource, page, size,
        sort: validateSort(sort, SORT_ALLOWED.cameras),
      }),
    })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-3. 카메라 상태 이력
// ────────────────────────────────────────────────────────────
export function getCameraHealthHistory(cameraId, { from, to, dataSource = 'REAL' } = {}) {
  return apiClient
    .get(`${BASE}/cameras/${cameraId}/health-history`, {
      params: cleanParams({ from, to, dataSource }),
    })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-4. 교통 맥락 이력
// ────────────────────────────────────────────────────────────
export function getTrafficContext({ cameraId, zoneId, from, to, dataSource = 'REAL' } = {}) {
  return apiClient
    .get(`${BASE}/traffic-context`, {
      params: cleanParams({ cameraId, zoneId, from, to, dataSource }),
    })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-5. 이상 이벤트 목록 (페이지)
// ────────────────────────────────────────────────────────────
export function listAnomalyEvents({
  cameraId,
  severity,
  status,
  anomalyType,
  detectionMethod,
  dataSource = 'REAL',
  from,
  to,
  page = 0,
  size = 20,
  sort = 'firstDetectedAt,desc',
} = {}) {
  return apiClient
    .get(`${BASE}/anomaly-events`, {
      params: cleanParams({
        cameraId, severity, status, anomalyType, detectionMethod,
        dataSource, from, to, page, size,
        sort: validateSort(sort, SORT_ALLOWED.anomalyEvents),
      }),
    })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-6. 이상 이벤트 상세
// ────────────────────────────────────────────────────────────
export function getAnomalyEvent(eventId) {
  return apiClient.get(`${BASE}/anomaly-events/${eventId}`).then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-7. 이상 이벤트 확인 (OPERATOR/ADMIN)
// ────────────────────────────────────────────────────────────
export function acknowledgeAnomaly(eventId, { note = '' } = {}) {
  return apiClient
    .post(`${BASE}/anomaly-events/${eventId}/acknowledge`, { note })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-8. 이상 이벤트 해결 — confirmedCause + resolutionNote 필수
// ────────────────────────────────────────────────────────────
export function resolveAnomaly(eventId, { confirmedCause, resolutionNote }) {
  if (!confirmedCause || !resolutionNote) {
    return Promise.reject(new Error('confirmedCause와 resolutionNote는 필수입니다.'))
  }
  return apiClient
    .post(`${BASE}/anomaly-events/${eventId}/resolve`, { confirmedCause, resolutionNote })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-9. 이상 이벤트 오탐 종료 — reason 필수 (OPERATOR/ADMIN)
// ────────────────────────────────────────────────────────────
export function dismissAnomaly(eventId, { reason }) {
  if (!reason) return Promise.reject(new Error('reason은 필수입니다.'))
  return apiClient
    .post(`${BASE}/anomaly-events/${eventId}/dismiss`, { reason })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-10. 정비 티켓 목록 (페이지)
// ────────────────────────────────────────────────────────────
export function listMaintenanceTickets({
  priority,
  status,
  assigneeId,
  page = 0,
  size = 20,
  sort = 'createdAt,desc',
} = {}) {
  return apiClient
    .get(`${BASE}/maintenance-tickets`, {
      params: cleanParams({
        priority, status, assigneeId, page, size,
        sort: validateSort(sort, SORT_ALLOWED.maintenanceTickets),
      }),
    })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-11. 수동 정비 티켓 생성
// ────────────────────────────────────────────────────────────
export function createMaintenanceTicket({ anomalyEventId, priority, actionNote = '' }) {
  return apiClient
    .post(`${BASE}/maintenance-tickets`, { anomalyEventId, priority, actionNote })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-12. 정비 티켓 배정 (OPERATOR/ADMIN)
// ────────────────────────────────────────────────────────────
export function assignMaintenanceTicket(ticketId, { assigneeId, note = '' }) {
  return apiClient
    .post(`${BASE}/maintenance-tickets/${ticketId}/assign`, { assigneeId, note })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-13. 정비 티켓 상태 변경 — RESOLVED 시 note 필수
// ────────────────────────────────────────────────────────────
export function changeTicketStatus(ticketId, { toStatus, note = '' }) {
  if (toStatus === 'RESOLVED' && !note) {
    return Promise.reject(new Error('RESOLVED 전환 시 조치 메모(note)는 필수입니다.'))
  }
  return apiClient
    .post(`${BASE}/maintenance-tickets/${ticketId}/status`, { toStatus, note })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-14. 정책 목록
// ────────────────────────────────────────────────────────────
export function listPolicies({ enabled } = {}) {
  return apiClient
    .get(`${BASE}/policies`, { params: cleanParams({ enabled }) })
    .then((r) => r.data)
}

// ────────────────────────────────────────────────────────────
// 3-15. 정책 수정 (ADMIN 전용)
// ────────────────────────────────────────────────────────────
export function updatePolicy(policyCode, payload) {
  return apiClient.patch(`${BASE}/policies/${policyCode}`, payload).then((r) => r.data)
}
