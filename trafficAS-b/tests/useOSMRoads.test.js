import { describe, it, expect } from "vitest";
import { congestionColor, congestionLabel } from "@/composables/useOSMRoads";

describe("congestion helpers", () => {
  it("returns 정체 color/label for >= 0.85", () => {
    expect(congestionColor(0.9)).toBe("#e74c3c");
    expect(congestionLabel(0.9)).toBe("정체");
  });
  it("returns 원활 for < 0.25", () => {
    expect(congestionColor(0.1)).toBe("#2ecc71");
    expect(congestionLabel(0.1)).toBe("원활");
  });
  it("boundaries", () => {
    expect(congestionLabel(0.65)).toBe("혼잡");
    expect(congestionLabel(0.45)).toBe("보통");
    expect(congestionLabel(0.25)).toBe("양호");
  });
});
