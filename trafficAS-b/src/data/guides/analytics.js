/**
 * 교통분석팀 (AnalyticsView) 사용자 가이드
 * 좌측 사이드 메뉴 전체 안내 + 대시보드 상세 설명 + 헤더 도구
 */
export default [
  {
    tab: "dashboard",
    selector: ".an-shell .snav",
    title: "교통분석팀에 오신 것을 환영합니다",
    description: [
      "좌측 사이드 메뉴 6개 영역입니다.",
      "① 대시보드 — 4개 영역을 한 화면에 통합 표시",
      "② 분석 기준 — 비교/기간/시간대 설정 + 저장된 프리셋",
      "③ 분석 인사이트 — AI가 감지한 핵심 변화와 권장 조치",
      "④ 구간 성능 비교 — 구간별·시간대별 속도 차트와 표",
      "⑤ 혼잡 지도 · 지표 — 도로 혼잡 지도 + 교차로·사고 분석",
      "⑥ 설정 — 분석 기본값/임계값/데이터 보관 등 환경 설정",
    ],
  },
  {
    tab: "dashboard",
    selector: ".hdr-bell-wrap",
    title: "헤더 실시간 알림",
    description:
      "헤더의 종 아이콘에서 피크 악화 · 속도 저하 · 흐름 개선 · 리포트 예약 등 부서 알림 4건을 실시간 확인할 수 있습니다. critical 알림이 있으면 빨간색으로 깜빡입니다.",
  },
  {
    tab: "dashboard",
    selector: ".an-shell .ctx-bar",
    title: "공통 분석 기준 바",
    description:
      "비교 기준(전일/전주/평균) · 기간 · 시간대를 한 곳에서 설정합니다. 우측 4개 액션 버튼으로 통계 조회 · 기간 비교 · 리포트 생성 · CSV 다운로드를 즉시 실행할 수 있습니다.",
  },
  {
    tab: "dashboard",
    selector: ".an-shell .insight-strip",
    title: "AI 분석 인사이트",
    description:
      "AI가 자동 감지한 핵심 변화 4건(피크 악화 · 속도 저하 · 흐름 개선 · 사고 영향)을 카드로 요약합니다. 아이콘 색상으로 심각도를 표시합니다.",
  },
  {
    tab: "dashboard",
    selector: ".an-shell .row-cmp",
    title: "구간 성능 비교 차트",
    description:
      "구간별 속도(좌)와 시간대별 속도 추이(우) 두 ECharts 차트입니다. 파랑=금일, 회색=전일, 초록=7일 평균. 빨간 음영은 AI가 식별한 정체 구간입니다.",
  },
  {
    tab: "dashboard",
    selector: ".an-shell .jam-map-card",
    title: "도로 구간 혼잡 현황 지도",
    description:
      "OSM 도로 데이터 기반 실시간 혼잡 지도입니다. 도로 색상은 평균 속도(빨강=정체, 초록=원활)를 의미합니다.",
  },
  {
    tab: "dashboard",
    selector: ".an-shell .kpi-tbl-card",
    title: "구간 주요 지표",
    description:
      "평균 속도 · 혼잡 구간 · 피크 악화 · 보고서 KPI 4종과 구간별 상세 표를 함께 표시합니다. 좌측 지도의 색상을 숫자로 검증할 수 있습니다.",
  },
  {
    tab: "settings",
    selector: ".an-shell .settings-panel",
    title: "환경 설정",
    description: [
      "4개 블록으로 구성: 분석 기본값 · 자동 갱신/알림 · 알람 임계값 · 데이터 보관.",
      "여기서 변경한 기본 비교 기준/시간대는 대시보드 ctx-bar에 자동 반영됩니다.",
      "하단 저장 버튼으로 적용 완료 토스트를 확인할 수 있습니다.",
    ],
  },
];
