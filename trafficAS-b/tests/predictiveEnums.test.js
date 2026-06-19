import { describe, it, expect } from "vitest";
import {
  DataSource,
  AnomalyStatus,
  TicketStatus,
  HealthStatus,
  HEALTH_STATUS_LABEL,
  SEVERITY_LABEL,
  TICKET_STATUS_LABEL,
  ANOMALY_TYPE_LABEL,
  DETECTION_METHOD_LABEL,
  safeEnum,
  labelOf,
} from "@/api/predictiveEnums";

describe("Enum 정의 — 백엔드 계약 §2-4 14종", () => {
  it("DataSource 5개", () => {
    expect(Object.keys(DataSource)).toEqual([
      "REAL", "OPEN_DATA", "SIMULATED", "FAULT_INJECTED", "MOCK",
    ]);
  });

  it("AnomalyStatus 5단계", () => {
    expect(Object.values(AnomalyStatus)).toEqual([
      "OPEN", "ACKNOWLEDGED", "RECOVERED", "RESOLVED", "DISMISSED",
    ]);
  });

  it("TicketStatus 5단계 — CLOSED 포함", () => {
    expect(TicketStatus.OPEN).toBe("OPEN");
    expect(TicketStatus.CLOSED).toBe("CLOSED");
  });

  it("HealthStatus 6종 — BASELINE_LEARNING / INSUFFICIENT_DATA 포함", () => {
    expect(HealthStatus.BASELINE_LEARNING).toBe("BASELINE_LEARNING");
    expect(HealthStatus.INSUFFICIENT_DATA).toBe("INSUFFICIENT_DATA");
  });

  it("Enum 객체는 Object.freeze로 보호 (런타임 변경 X)", () => {
    expect(() => {
      "use strict";
      DataSource.NEW_VALUE = "x";
    }).toThrow();
  });
});

describe("safeEnum — 알 수 없는 값 fallback (백엔드 신규 값 대비)", () => {
  it("허용된 값은 그대로 반환", () => {
    expect(safeEnum("REAL", DataSource, DataSource.REAL)).toBe("REAL");
    expect(safeEnum("DISMISSED", AnomalyStatus, AnomalyStatus.OPEN)).toBe("DISMISSED");
  });

  it("알 수 없는 값은 fallback 반환", () => {
    expect(safeEnum("XYZ", DataSource, DataSource.REAL)).toBe("REAL");
    expect(safeEnum("FUTURE_STATUS", AnomalyStatus, AnomalyStatus.OPEN)).toBe("OPEN");
  });

  it("null / undefined도 fallback", () => {
    expect(safeEnum(null, DataSource, DataSource.MOCK)).toBe("MOCK");
    expect(safeEnum(undefined, DataSource, DataSource.MOCK)).toBe("MOCK");
  });

  it("빈 문자열도 fallback", () => {
    expect(safeEnum("", AnomalyStatus, AnomalyStatus.OPEN)).toBe("OPEN");
  });
});

describe("labelOf — 한글 라벨 매핑", () => {
  it("HealthStatus → 한글", () => {
    expect(labelOf(HEALTH_STATUS_LABEL, "NORMAL")).toBe("정상");
    expect(labelOf(HEALTH_STATUS_LABEL, "DEGRADED")).toBe("저하");
    expect(labelOf(HEALTH_STATUS_LABEL, "CRITICAL")).toBe("위험");
    expect(labelOf(HEALTH_STATUS_LABEL, "OFFLINE")).toBe("오프라인");
    expect(labelOf(HEALTH_STATUS_LABEL, "BASELINE_LEARNING")).toBe("기준선 학습 중");
  });

  it("Severity → 한글", () => {
    expect(labelOf(SEVERITY_LABEL, "WARNING")).toBe("경고");
    expect(labelOf(SEVERITY_LABEL, "CRITICAL")).toBe("심각");
  });

  it("TicketStatus → 한글", () => {
    expect(labelOf(TICKET_STATUS_LABEL, "IN_PROGRESS")).toBe("진행 중");
    expect(labelOf(TICKET_STATUS_LABEL, "RESOLVED")).toBe("해결");
    expect(labelOf(TICKET_STATUS_LABEL, "CLOSED")).toBe("종결");
  });

  it("AnomalyType 8종 모두 라벨 보유", () => {
    expect(labelOf(ANOMALY_TYPE_LABEL, "FPS_DEGRADATION")).toBe("FPS 저하");
    expect(labelOf(ANOMALY_TYPE_LABEL, "OCR_QUALITY_DEGRADATION")).toBe("OCR 품질 저하");
    expect(labelOf(ANOMALY_TYPE_LABEL, "RESOURCE_SATURATION")).toBe("리소스 과부하");
  });

  it("DetectionMethod 5종 라벨", () => {
    expect(labelOf(DETECTION_METHOD_LABEL, "RULE")).toBe("룰 기반");
    expect(labelOf(DETECTION_METHOD_LABEL, "TREND_PROJECTION")).toBe("추세 예측");
    expect(labelOf(DETECTION_METHOD_LABEL, "LSTM_AUTOENCODER")).toBe("LSTM AutoEncoder");
  });

  it("알 수 없는 키는 기본 fallback '—'", () => {
    expect(labelOf(HEALTH_STATUS_LABEL, "FUTURE_X")).toBe("—");
  });

  it("커스텀 fallback 지정 가능", () => {
    expect(labelOf(HEALTH_STATUS_LABEL, "FUTURE_X", "미분류")).toBe("미분류");
  });

  it("null / undefined도 fallback", () => {
    expect(labelOf(HEALTH_STATUS_LABEL, null)).toBe("—");
    expect(labelOf(HEALTH_STATUS_LABEL, undefined)).toBe("—");
  });
});
