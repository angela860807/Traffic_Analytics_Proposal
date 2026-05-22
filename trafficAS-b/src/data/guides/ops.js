/**
 * 시설운영팀 (OpsView) 사용자 가이드
 * 좌측 사이드 메뉴 전체 안내 + 대시보드(장비 현황) 상세 설명 + 헤더 도구
 */
export default [
  {
    tab: "status",
    selector: ".ops-shell .snav",
    title: "시설운영팀에 오신 것을 환영합니다",
    description: [
      "좌측 사이드 메뉴 6개 영역입니다.",
      "① 장비 현황 — 인프라 통합 대시보드 (네트워크/서버/장애)",
      "② 카메라 — 카메라 장비별 가동 상태",
      "③ 서버 — CPU/메모리/디스크/서비스 상세",
      "④ 네트워크 — 회선 지연 및 트래픽 추이",
      "⑤ 장애 관리 — 장애 티켓 처리 현황",
      "⑥ 설정 — 자동 갱신/임계값/점검 주기/현장 출동 설정",
    ],
  },
  {
    tab: "status",
    selector: ".hdr-bell-wrap",
    title: "헤더 실시간 알림",
    description:
      "헤더 종 아이콘에서 RTSP 타임아웃 · 디스크 임계 · 네트워크 지연 · 정기 점검 완료 등 인프라 알림 4건을 실시간 확인합니다. critical 알림이 있으면 빨간색으로 깜빡입니다.",
  },
  {
    tab: "status",
    selector: ".net-card",
    title: "네트워크 지연",
    description:
      "전체 네트워크의 평균/최대 지연을 차트로 보여줍니다. '전체 보기'로 네트워크 상세 탭으로 이동할 수 있습니다.",
  },
  {
    tab: "status",
    selector: ".srv-card",
    title: "서버 상태",
    description:
      "대표 서버의 CPU · 메모리 · 디스크 사용률과 서비스 상태를 한눈에 확인합니다.",
  },
  {
    tab: "status",
    selector: ".main-grid",
    title: "장애 상세 및 인프라",
    description:
      "현재 발생 중인 장애의 상세 정보와 우측 인프라 카드를 통해 전체 상태를 점검합니다.",
  },
  {
    tab: "status",
    selector: ".hdr-weather",
    title: "날씨 정보",
    description:
      "헤더의 날씨 칩에서 현장 작업과 관련된 강수·결빙 등 환경 정보를 빠르게 확인할 수 있습니다.",
  },
  {
    tab: "settings",
    selector: ".ops-set-grid",
    title: "환경 설정",
    description: [
      "4개 블록으로 구성: 자동 갱신/알림 · 장애 임계값 · 점검/로그 · 현장 출동.",
      "임계값(네트워크 지연/CPU/디스크/RTSP 타임아웃)을 조정해 알림 정책을 맞춤 설정합니다.",
      "현장 출동 기본 담당자 · SMS 발송 · 예비 부품 알림 옵션을 제공합니다.",
    ],
  },
];
