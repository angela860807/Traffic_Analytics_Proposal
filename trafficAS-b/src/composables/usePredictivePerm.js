// 예지보전 모듈 권한 헬퍼
//
// 출처: 요구사항 정의서 2-4 / 7-2절 + DB 파트 협의 문서(2026-06-12)
// 이전 API 계약서 §6 권한표에서 누락/암묵된 항목을 명시화한 최종 권한표 기준.
//
// 핵심 변경:
//  - 이벤트 resolve: OPERATOR/ADMIN (MAINTAINER 불가) — 권한 명시 추가
//  - 수동 티켓 생성(POST /maintenance-tickets): OPERATOR/ADMIN — 권한 명시 추가
//  - 티켓 CLOSED 처리: OPERATOR/ADMIN만 가능 (MAINTAINER는 RESOLVED까지)
//  - MAINTAINER 상태 변경 범위: ASSIGNED → IN_PROGRESS → RESOLVED 만 가능

import { computed } from 'vue'
import { useAuth } from './useAuth'

const ROLE = Object.freeze({
  USER: 'USER',
  OPERATOR: 'OPERATOR',
  MAINTAINER: 'MAINTAINER',
  ADMIN: 'ADMIN',
})

function normalizeRole(rawRole) {
  if (!rawRole) return ROLE.USER
  const firstRole = Array.isArray(rawRole) ? rawRole[0] : String(rawRole).split(',')[0]
  return firstRole.replace(/^ROLE_/, '') || ROLE.USER
}

// MAINTAINER 허용 상태 전이 (요구사항 정의서 7-2)
const MAINTAINER_ALLOWED_TRANSITIONS = Object.freeze({
  ASSIGNED:    ['IN_PROGRESS'],
  IN_PROGRESS: ['RESOLVED'],
})
// OPERATOR / ADMIN 허용 전이 — CLOSED 포함 전 범위
const OPERATOR_ALLOWED_TRANSITIONS = Object.freeze({
  OPEN:        ['ASSIGNED'],
  ASSIGNED:    ['IN_PROGRESS', 'OPEN'],
  IN_PROGRESS: ['RESOLVED', 'ASSIGNED'],
  RESOLVED:    ['CLOSED', 'IN_PROGRESS'],
})

export function usePredictivePerm() {
  const { currentUser } = useAuth()

  const role = computed(() => {
    const u = currentUser.value || {}
    return normalizeRole(u.predictiveRole || u.role || (Array.isArray(u.roles) ? u.roles[0] : null))
  })

  const isOperator = computed(() => role.value === ROLE.OPERATOR)
  const isMaintainer = computed(() => role.value === ROLE.MAINTAINER)
  const isAdmin = computed(() => role.value === ROLE.ADMIN)

  // 대시보드 조회: OPERATOR/MAINTAINER/ADMIN
  const canView = computed(() => isOperator.value || isMaintainer.value || isAdmin.value)

  // ─── 이상 이벤트 ───
  // 확인(acknowledge) / 해결(resolve) / 오탐 종료(dismiss): OPERATOR + ADMIN
  // (MAINTAINER는 이벤트 자체를 직접 처리하지 않고 티켓을 처리)
  const canAcknowledgeAnomaly = computed(() => isOperator.value || isAdmin.value)
  const canResolveAnomaly     = computed(() => isOperator.value || isAdmin.value)
  const canDismissAnomaly     = computed(() => isOperator.value || isAdmin.value)

  // ─── 정비 티켓 ───
  // 수동 생성(POST /maintenance-tickets): OPERATOR + ADMIN
  const canCreateTicket = computed(() => isOperator.value || isAdmin.value)
  // 담당자 배정: OPERATOR + ADMIN
  const canAssignTicket = computed(() => isOperator.value || isAdmin.value)
  // CLOSED 처리: OPERATOR + ADMIN (MAINTAINER 불가)
  const canCloseTicket  = computed(() => isOperator.value || isAdmin.value)
  // 일반 상태 변경: OPERATOR + MAINTAINER + ADMIN — 단 MAINTAINER 전이는 제한
  const canChangeTicketStatus = computed(
    () => isOperator.value || isMaintainer.value || isAdmin.value,
  )

  // 특정 상태 전이가 현재 역할에 허용되는지 — UI 버튼 노출 여부 결정용
  function canTransitionTicket(fromStatus, toStatus) {
    if (!fromStatus || !toStatus) return false
    if (isAdmin.value || isOperator.value) {
      return OPERATOR_ALLOWED_TRANSITIONS[fromStatus]?.includes(toStatus) ?? false
    }
    if (isMaintainer.value) {
      return MAINTAINER_ALLOWED_TRANSITIONS[fromStatus]?.includes(toStatus) ?? false
    }
    return false
  }

  // ─── 정책 ───
  // 수정: ADMIN 전용
  const canEditPolicy = computed(() => isAdmin.value)

  return {
    role,
    isOperator, isMaintainer, isAdmin,
    canView,
    canAcknowledgeAnomaly, canResolveAnomaly, canDismissAnomaly,
    canCreateTicket, canAssignTicket, canCloseTicket, canChangeTicketStatus,
    canTransitionTicket,
    canEditPolicy,
    ROLE,
    MAINTAINER_ALLOWED_TRANSITIONS,
    OPERATOR_ALLOWED_TRANSITIONS,
  }
}

// 라우터 가드용 — 역할 기반 진입 차단
export function hasPredictiveAccess(user) {
  if (!user) return false
  const role = normalizeRole(user.predictiveRole
    || user.role
    || (Array.isArray(user.roles) ? user.roles[0] : null))
  return role === ROLE.OPERATOR || role === ROLE.MAINTAINER || role === ROLE.ADMIN
}
