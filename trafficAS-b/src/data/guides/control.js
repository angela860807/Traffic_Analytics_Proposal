/**
 * 교통정보센터 (ControlView) 사용자 가이드
 * 좌측 사이드 메뉴 전체 안내 + 대시보드 상세 설명 + 헤더 도구
 */
export default [
  {
    tab: "center",
    selector: ".cc-shell .snav",
    title: "교통정보센터에 오신 것을 환영합니다",
    description: [
      "좌측 사이드 메뉴 4개 영역입니다.",
      "① 교통정보센터 — 실시간 흐름 지도 + AI 카메라 통합 관제",
      "② 카메라 — 운영 중인 모든 카메라 영상 확인",
      "③ 보고서 — 일일/주간 운영 보고서 CSV 다운로드",
      "④ 설정 — 알림 사운드, 큐 갱신 주기, 지도 기본 모드 설정",
    ],
  },
  {
    tab: "center",
    selector: ".hdr-bell-wrap",
    title: "헤더 실시간 알림",
    description:
      "교통사고 · 정체 심화 · 차량 고장 · 결빙 주의 등 실시간 알림을 확인합니다. 알림을 클릭하면 지도가 해당 위치로 자동 이동합니다. critical 알림이 있으면 빨간색으로 깜빡입니다.",
  },
  {
    tab: "center",
    selector: ".api-row",
    title: "ITS Open API 실시간 지표",
    description:
      "혼잡 악화 · 속도 급감 · 미처리 이벤트 · 정상 CCTV 비율 등 국토부 ITS API에서 받은 실시간 핵심 지표 4종을 한 줄로 요약합니다.",
  },
  {
    tab: "center",
    selector: ".map-card",
    title: "실시간 교통 흐름 지도",
    description: [
      "서울 주요 간선의 실시간 흐름 색상과 ITS CCTV 마커를 표시합니다.",
      "우상단 토글로 교통흐름 / CCTV 모드를 전환하고, CCTV 마커 클릭 시 라이브 스트림 모달이 열립니다.",
    ],
  },
  {
    tab: "center",
    selector: ".mc-weather-wrap",
    title: "날씨 요약",
    description:
      "지도 헤더의 날씨 칩을 클릭하면 강남 3구 상세 날씨 패널이 펼쳐집니다. 결빙·강수 등 도로 환경에 영향을 주는 요소를 빠르게 확인할 수 있습니다.",
  },
  {
    tab: "center",
    selector: ".right-stack .flow-cam",
    title: "교통 흐름 분석 카메라",
    description:
      "AI가 차량 통과율 · 평균 속도 · 혼잡 레벨을 영상 위에 오버레이로 표시합니다.",
  },
  {
    tab: "center",
    selector: ".right-stack .bot-card:last-child",
    title: "과속 단속 카메라",
    description: [
      "AI 단속 분석 라이브 영상과 제한속도 · 금일 단속 건수를 표시합니다.",
      "전송 버튼을 누르면 캡처 이미지가 단속관리팀 검토 큐로 즉시 전송됩니다.",
    ],
  },
];
