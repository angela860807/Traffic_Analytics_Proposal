// 예지보전 모듈 권한 헬퍼 — 백엔드 계약 §6 권한 매트릭스
// USER 못함 / OPERATOR / MAINTAINER / ADMIN

import { computed } from 'vue'
import { useAuth } from './useAuth'

const ROLE = Object.freeze({
  USER: 'USER',
  OPERATOR: 'OPERATOR',
  MAINTAINER: 'MAINTAINER',
  ADMIN: 'ADMIN',
})

export function usePredictivePerm() {
  const { currentUser } = useAuth()

  const role = computed(() => {
    const u = currentUser.value || {}
    // useAuth가 어떤 키로 role을 노출하는지에 따라 우선순위 — 호환성 위해 여러 키 시도
    return u.predictiveRole || u.role || (Array.isArray(u.roles) ? u.roles[0] : null) || ROLE.USER
  })

  const isOperator = computed(() => role.value === ROLE.OPERATOR)
  const isMaintainer = computed(() => role.value === ROLE.MAINTAINER)
  const isAdmin = computed(() => role.value === ROLE.ADMIN)

  // §6 권한 매트릭스
  // 예지보전 대시보드 조회: OPERATOR / MAINTAINER / ADMIN
  const canView = computed(() => isOperator.value || isMaintainer.value || isAdmin.value)

  // 이벤트 acknowledge / resolve / dismiss: OPERATOR + ADMIN
  const canAcknowledgeAnomaly = computed(() => isOperator.value || isAdmin.value)
  const canResolveAnomaly = computed(() => isOperator.value || isAdmin.value)
  const canDismissAnomaly = computed(() => isOperator.value || isAdmin.value)

  // 티켓 배정: OPERATOR + ADMIN
  const canAssignTicket = computed(() => isOperator.value || isAdmin.value)

  // 티켓 상태·조치 변경: OPERATOR + MAINTAINER + ADMIN
  const canChangeTicketStatus = computed(
    () => isOperator.value || isMaintainer.value || isAdmin.value,
  )

  // 정책 수정: ADMIN 전용
  const canEditPolicy = computed(() => isAdmin.value)

  return {
    role,
    isOperator, isMaintainer, isAdmin,
    canView,
    canAcknowledgeAnomaly, canResolveAnomaly, canDismissAnomaly,
    canAssignTicket, canChangeTicketStatus,
    canEditPolicy,
    ROLE,
  }
}

// 라우터 가드용 — 역할 기반 진입 차단
export function hasPredictiveAccess(user) {
  if (!user) return false
  const role = user.predictiveRole
    || user.role
    || (Array.isArray(user.roles) ? user.roles[0] : null)
  return role === ROLE.OPERATOR || role === ROLE.MAINTAINER || role === ROLE.ADMIN
}
