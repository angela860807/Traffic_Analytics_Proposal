import { describe, it, expect, beforeEach, vi } from "vitest";
import { ref } from "vue";

// useAuth를 mock — currentUser를 테스트마다 다른 role로 바꿔가며 검증
const currentUser = ref({});
vi.mock("@/composables/useAuth", () => ({
  useAuth: () => ({ currentUser }),
}));

let usePerm;
let hasPredictiveAccess;
beforeEach(async () => {
  localStorage.clear();
  const mod = await import("@/composables/usePredictivePerm");
  usePerm = mod.usePredictivePerm;
  hasPredictiveAccess = mod.hasPredictiveAccess;
});

describe("usePredictivePerm — role 매트릭스 (요구사항 정의서 2-4/7-2 + DB 협의 2026-06-12)", () => {
  it("USER는 어떤 액션도 불가", () => {
    currentUser.value = { role: "USER" };
    const p = usePerm();
    expect(p.canView.value).toBe(false);
    expect(p.canResolveAnomaly.value).toBe(false);
    expect(p.canEditPolicy.value).toBe(false);
  });

  it("OPERATOR는 정책 수정만 불가", () => {
    currentUser.value = { role: "OPERATOR" };
    const p = usePerm();
    expect(p.canView.value).toBe(true);
    expect(p.canAcknowledgeAnomaly.value).toBe(true);
    expect(p.canResolveAnomaly.value).toBe(true);
    expect(p.canDismissAnomaly.value).toBe(true);
    expect(p.canCreateTicket.value).toBe(true);
    expect(p.canAssignTicket.value).toBe(true);
    expect(p.canCloseTicket.value).toBe(true);
    expect(p.canChangeTicketStatus.value).toBe(true);
    expect(p.canEditPolicy.value).toBe(false);
  });

  it("MAINTAINER는 이벤트 처리·수동 티켓·CLOSED 불가", () => {
    currentUser.value = { role: "MAINTAINER" };
    const p = usePerm();
    expect(p.canView.value).toBe(true);
    expect(p.canChangeTicketStatus.value).toBe(true); // 상태 변경 가능
    expect(p.canAcknowledgeAnomaly.value).toBe(false); // 이벤트 처리 불가
    expect(p.canResolveAnomaly.value).toBe(false);
    expect(p.canDismissAnomaly.value).toBe(false);
    expect(p.canCreateTicket.value).toBe(false);
    expect(p.canAssignTicket.value).toBe(false);
    expect(p.canCloseTicket.value).toBe(false); // CLOSED는 OPERATOR/ADMIN만
    expect(p.canEditPolicy.value).toBe(false);
  });

  it("ADMIN은 모든 액션 가능", () => {
    currentUser.value = { role: "ADMIN" };
    const p = usePerm();
    expect(p.canView.value).toBe(true);
    expect(p.canResolveAnomaly.value).toBe(true);
    expect(p.canCloseTicket.value).toBe(true);
    expect(p.canEditPolicy.value).toBe(true);
  });
});

describe("usePredictivePerm — canTransitionTicket (티켓 상태 전이)", () => {
  it("MAINTAINER는 ASSIGNED → IN_PROGRESS, IN_PROGRESS → RESOLVED만 가능", () => {
    currentUser.value = { role: "MAINTAINER" };
    const { canTransitionTicket } = usePerm();
    expect(canTransitionTicket("ASSIGNED", "IN_PROGRESS")).toBe(true);
    expect(canTransitionTicket("IN_PROGRESS", "RESOLVED")).toBe(true);
    // 금지 전이
    expect(canTransitionTicket("OPEN", "ASSIGNED")).toBe(false); // 배정은 OPERATOR/ADMIN
    expect(canTransitionTicket("RESOLVED", "CLOSED")).toBe(false); // CLOSED 금지
    expect(canTransitionTicket("ASSIGNED", "RESOLVED")).toBe(false); // 중간 단계 건너뜀
  });

  it("OPERATOR는 OPEN→ASSIGNED, RESOLVED→CLOSED 등 전 전이 가능", () => {
    currentUser.value = { role: "OPERATOR" };
    const { canTransitionTicket } = usePerm();
    expect(canTransitionTicket("OPEN", "ASSIGNED")).toBe(true);
    expect(canTransitionTicket("ASSIGNED", "IN_PROGRESS")).toBe(true);
    expect(canTransitionTicket("IN_PROGRESS", "RESOLVED")).toBe(true);
    expect(canTransitionTicket("RESOLVED", "CLOSED")).toBe(true);
    // 되돌리기도 일부 허용
    expect(canTransitionTicket("ASSIGNED", "OPEN")).toBe(true);
    expect(canTransitionTicket("IN_PROGRESS", "ASSIGNED")).toBe(true);
  });

  it("ADMIN도 OPERATOR와 동일하게 전 전이 가능", () => {
    currentUser.value = { role: "ADMIN" };
    const { canTransitionTicket } = usePerm();
    expect(canTransitionTicket("RESOLVED", "CLOSED")).toBe(true);
    expect(canTransitionTicket("ASSIGNED", "IN_PROGRESS")).toBe(true);
  });

  it("USER는 어떤 전이도 불가", () => {
    currentUser.value = { role: "USER" };
    const { canTransitionTicket } = usePerm();
    expect(canTransitionTicket("ASSIGNED", "IN_PROGRESS")).toBe(false);
  });

  it("from / to 빈 값이면 false", () => {
    currentUser.value = { role: "ADMIN" };
    const { canTransitionTicket } = usePerm();
    expect(canTransitionTicket("", "RESOLVED")).toBe(false);
    expect(canTransitionTicket("ASSIGNED", "")).toBe(false);
  });
});

describe("hasPredictiveAccess — 라우터 가드", () => {
  it("backend JWT가 있으면 OPERATOR / MAINTAINER / ADMIN 허용", () => {
    localStorage.setItem("tas_access_token", "header.payload.signature");
    expect(hasPredictiveAccess({ role: "OPERATOR" })).toBe(true);
    expect(hasPredictiveAccess({ role: "MAINTAINER" })).toBe(true);
    expect(hasPredictiveAccess({ role: "ADMIN" })).toBe(true);
  });

  it("USER / null 차단", () => {
    expect(hasPredictiveAccess({ role: "USER" })).toBe(false);
    expect(hasPredictiveAccess(null)).toBe(false);
    expect(hasPredictiveAccess(undefined)).toBe(false);
  });

  it("roles 배열 형태 지원 (백엔드 JWT 호환)", () => {
    localStorage.setItem("tas_access_token", "header.payload.signature");
    expect(hasPredictiveAccess({ roles: ["MAINTAINER"] })).toBe(true);
    expect(hasPredictiveAccess({ roles: ["USER"] })).toBe(false);
  });

  it("predictiveRole 키가 있으면 우선", () => {
    localStorage.setItem("tas_access_token", "header.payload.signature");
    expect(hasPredictiveAccess({ predictiveRole: "ADMIN", role: "USER" })).toBe(true);
  });

  it("local fallback 토큰은 predictive 라우터 접근을 차단", () => {
    localStorage.setItem("tas_access_token", "local-123");
    expect(hasPredictiveAccess({ role: "ADMIN" })).toBe(false);
  });
});
