import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import DataState from "@/components/dashboard/DataState.vue";

describe("DataState", () => {
  it("renders loading", () => {
    const w = mount(DataState, { props: { state: "loading" } });
    expect(w.text()).toContain("불러오는 중");
    expect(w.find('[role="status"]').exists()).toBe(true);
  });

  it("renders error with retry button + emits retry", async () => {
    const w = mount(DataState, { props: { state: "error" } });
    expect(w.find('[role="alert"]').exists()).toBe(true);
    await w.find(".ds-retry").trigger("click");
    expect(w.emitted("retry")).toBeTruthy();
  });

  it("renders empty state", () => {
    const w = mount(DataState, {
      props: { state: "empty", emptyText: "검색 결과 없음" },
    });
    expect(w.text()).toContain("검색 결과 없음");
  });

  it("renders slot content when state is ok", () => {
    const w = mount(DataState, {
      props: { state: "ok" },
      slots: { default: "<p>실제 내용</p>" },
    });
    expect(w.html()).toContain("실제 내용");
  });
});
