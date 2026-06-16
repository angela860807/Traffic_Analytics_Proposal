import { describe, it, expect, vi, beforeEach } from "vitest";

// apiClient를 mock — 실제 네트워크 호출 없이 호출된 인자만 검증
const mockGet = vi.fn(() => Promise.resolve({ data: { content: [] } }));
const mockPost = vi.fn(() => Promise.resolve({ data: { ok: true } }));
const mockPatch = vi.fn(() => Promise.resolve({ data: { ok: true } }));

vi.mock("@/api/client", () => ({
  apiClient: {
    get: mockGet,
    post: mockPost,
    patch: mockPatch,
  },
}));

// 동적 import — mock 적용 후 로드
let api;
beforeEach(async () => {
  mockGet.mockClear();
  mockPost.mockClear();
  mockPatch.mockClear();
  api = await import("@/api/predictiveApi");
});

describe("predictiveApi — URL / payload", () => {
  it("getSummary는 /api/v1/predictive/summary + dataSource=REAL 기본", async () => {
    await api.getSummary();
    expect(mockGet).toHaveBeenCalledWith("/api/v1/predictive/summary", {
      params: { dataSource: "REAL" },
    });
  });

  it("getCameraHealthHistory는 cameraId가 path에, from/to는 query", async () => {
    await api.getCameraHealthHistory(7, { from: "2026-06-11T00:00:00+09:00", to: "2026-06-11T01:00:00+09:00" });
    expect(mockGet).toHaveBeenCalledWith(
      "/api/v1/predictive/cameras/7/health-history",
      {
        params: {
          from: "2026-06-11T00:00:00+09:00",
          to: "2026-06-11T01:00:00+09:00",
          dataSource: "REAL",
        },
      },
    );
  });

  it("listCameras는 페이지 + sort 화이트리스트 검증 — healthScore,asc 허용", async () => {
    await api.listCameras({ sort: "healthScore,asc" });
    const args = mockGet.mock.calls[0][1];
    expect(args.params.sort).toBe("healthScore,asc");
  });

  it("listCameras는 sort 화이트리스트 외 필드는 undefined로 제거 (백엔드 400 방지)", async () => {
    await api.listCameras({ sort: "fakeField,desc" });
    const args = mockGet.mock.calls[0][1];
    expect(args.params.sort).toBeUndefined();
  });

  it("listAnomalyEvents는 firstDetectedAt,desc 기본 + 다른 필드 통과", async () => {
    await api.listAnomalyEvents({ sort: "severity,desc", cameraId: 5 });
    const args = mockGet.mock.calls[0][1];
    expect(args.params.sort).toBe("severity,desc");
    expect(args.params.cameraId).toBe(5);
  });

  it("listMaintenanceTickets는 priority sort 허용", async () => {
    await api.listMaintenanceTickets({ sort: "priority,desc" });
    expect(mockGet.mock.calls[0][1].params.sort).toBe("priority,desc");
  });
});

describe("predictiveApi — 필수값 검증 (resolve / dismiss / RESOLVED)", () => {
  it("resolveAnomaly는 confirmedCause 없으면 reject", async () => {
    await expect(
      api.resolveAnomaly(101, { resolutionNote: "memo only" }),
    ).rejects.toThrow();
    expect(mockPost).not.toHaveBeenCalled();
  });

  it("resolveAnomaly는 resolutionNote 없으면 reject", async () => {
    await expect(
      api.resolveAnomaly(101, { confirmedCause: "cause only" }),
    ).rejects.toThrow();
  });

  it("resolveAnomaly는 둘 다 있으면 정상 호출", async () => {
    await api.resolveAnomaly(101, {
      confirmedCause: "AI overload",
      resolutionNote: "restarted",
    });
    expect(mockPost).toHaveBeenCalledWith(
      "/api/v1/predictive/anomaly-events/101/resolve",
      { confirmedCause: "AI overload", resolutionNote: "restarted" },
    );
  });

  it("dismissAnomaly는 reason 없으면 reject", async () => {
    await expect(api.dismissAnomaly(101, {})).rejects.toThrow();
  });

  it("changeTicketStatus는 RESOLVED + note 빈 문자면 reject", async () => {
    await expect(
      api.changeTicketStatus(501, { toStatus: "RESOLVED", note: "" }),
    ).rejects.toThrow();
  });

  it("changeTicketStatus는 다른 상태로 가면 note 없어도 통과", async () => {
    await api.changeTicketStatus(501, { toStatus: "IN_PROGRESS" });
    expect(mockPost).toHaveBeenCalledWith(
      "/api/v1/predictive/maintenance-tickets/501/status",
      { toStatus: "IN_PROGRESS", note: "" },
    );
  });
});

describe("predictiveApi — 시간 포맷 (ISO + offset)", () => {
  it("isoWithOffset은 toISOString의 UTC Z가 아니라 로컬 offset(+/-HH:MM)을 붙임", () => {
    const d = new Date("2026-06-11T05:00:00Z");
    const out = api.isoWithOffset(d);
    // 정규식: yyyy-MM-ddTHH:mm:ss(+|-)HH:MM
    expect(out).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$/);
    // UTC Z가 들어가면 안 됨
    expect(out).not.toMatch(/Z$/);
  });
});

describe("predictiveApi — SORT_ALLOWED 화이트리스트", () => {
  it("3개 리소스 모두 정의됨", () => {
    expect(api.SORT_ALLOWED.cameras).toContain("healthScore");
    expect(api.SORT_ALLOWED.anomalyEvents).toContain("firstDetectedAt");
    expect(api.SORT_ALLOWED.maintenanceTickets).toContain("priority");
  });
});
