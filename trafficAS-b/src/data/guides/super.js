/**
 * 경영전략본부 (SuperView) 사용자 가이드
 * 좌측 사이드 메뉴 전체 안내 + 대시보드 + 14개 통합 탭
 */
export default [
  {
    tab: "dashboard",
    selector: ".sa-shell .snav",
    title: "경영전략본부에 오신 것을 환영합니다",
    description: [
      "좌측 사이드 메뉴는 두 그룹으로 나뉩니다.",
      "[일반 운영 — 전사 통합 뷰]",
      "운영현황 · 지도 · 이벤트 · 카메라 · OCR · 통계 · 보고서 · 설정",
      "[경영전략본부 전용]",
      "① 대시보드 — 전사 통합 KPI 및 부서별 성과",
      "② 권한 관리 · ③ 사용자 관리 · ④ 조직 관리",
      "⑤ 시스템 설정 · ⑥ 감사 로그",
    ],
  },
  {
    tab: "dashboard",
    selector: ".hdr-bell-wrap",
    title: "헤더 실시간 알림",
    description:
      "헤더 종 아이콘에서 권한 승격 요청 · 월간 결재 · 예산 집행률 · 전 부서 SLA 달성 등 경영 알림 4건을 실시간 확인합니다. critical 알림이 있으면 빨간색으로 깜빡입니다.",
  },
  {
    tab: "dashboard",
    selector: ".sa-shell .kpis",
    title: "글로벌 KPI",
    description:
      "전체 시스템의 핵심 지표(가동률 · 처리량 · SLA · 알람 등)를 한 줄로 요약합니다. 카드의 색상은 상태(정상/경고/위험)를 나타냅니다.",
  },
  {
    tab: "dashboard",
    selector: ".sa-shell .tbl-dept",
    title: "부서별 성과 요약",
    description:
      "교통정보센터 · 교통분석팀 · 시설운영팀 · 단속관리팀의 상태 · 이벤트 수 · SLA 준수율 · 핵심 지표를 한눈에 비교합니다. 최하단 '전체 평균' 행으로 전사 평균을 빠르게 확인할 수 있습니다.",
  },
  {
    tab: "dashboard",
    selector: ".sa-shell .tbl-app",
    title: "승인 대기 목록",
    description:
      "결재가 필요한 요청(예산 · 권한 · 정책 변경 등) 목록입니다. 우선순위와 요청 시간 기준으로 빠른 의사결정을 지원합니다.",
  },
  {
    tab: "ops",
    selector: ".sa-shell .kpis",
    title: "운영현황 — 시설운영팀 통합",
    description:
      "전사 가동률 · 온라인 카메라 비율 · 평균 네트워크 지연 · 활성 장애 건수와 대표 서버 4대의 CPU/메모리/디스크 사용률을 한 화면에 요약합니다.",
  },
  {
    tab: "map",
    selector: ".map-overview",
    title: "지도 — 교통정보센터 통합",
    description:
      "서울 주요 간선 5개 도로의 실시간 평균 속도와 혼잡도, 활성 이벤트 건수를 표로 확인합니다. 상세 인터랙티브 지도는 교통정보센터 대시보드에서 사용하세요.",
  },
  {
    tab: "events",
    selector: ".sa-shell .pnl",
    title: "이벤트 — 전 부서 통합 이력",
    description:
      "교통정보센터 · 단속관리팀 · 시설운영팀 · 교통분석팀에서 발생한 모든 이벤트를 시각 순으로 한 표에 통합 표시합니다. 부서·유형 컬럼으로 출처를 즉시 식별합니다.",
  },
  {
    tab: "cams",
    selector: ".sa-shell .kpis",
    title: "카메라 — 전 부서 통합",
    description: [
      "전체 247대 중 정상 · 오프라인 · 오류 비율을 KPI 카드로 표시합니다.",
      "하단에서 부서별 카메라 배분(교통정보센터 / 시설운영팀)과 최근 이슈 카메라 목록을 확인합니다.",
    ],
  },
  {
    tab: "ocr",
    selector: ".sa-shell .kpis",
    title: "OCR — 단속관리팀 통합",
    description:
      "오늘 처리량 · 인식 성공률 · 평균 신뢰도 · 인식 실패 건수를 KPI로 표시하고, 최근 OCR 인식 로그 5건을 시각/번호/카메라/방향/신뢰도/상태로 확인합니다.",
  },
  {
    tab: "stats",
    selector: ".sa-shell .kpis",
    title: "통계 — 교통분석팀 통합",
    description:
      "총 감지 차량 · 진입(IN) · 이탈(OUT) · 평균 통과 속도 KPI 4종과 7개 시간대(00~24시)별 통행량 분포를 막대 바와 함께 시각화합니다.",
  },
  {
    tab: "reports",
    selector: ".su-rep-grid",
    title: "보고서",
    description:
      "월간 종합 운영 보고서 · 보안/감사 로그 보고서 · 분기 KPI 종합 보고서 3종을 CSV로 다운로드합니다. 각 보고서는 자동 생성 또는 수동 발행이 가능합니다.",
  },
  {
    tab: "settings",
    selector: ".su-set-grid",
    title: "설정 — 전사 시스템",
    description:
      "알림/백업 · 로그/API · 보안 3개 블록으로 분류된 전사 시스템 설정입니다. 경영전략본부 권한이 있어야 변경 가능하며, 모든 부서에 즉시 적용됩니다.",
  },
  {
    tab: "perms",
    selector: ".perm-matrix",
    title: "권한 관리",
    description:
      "5단계 계층(슈퍼어드민/부장급/과장급/대리급/사원급)별 권한 범위와 인원, 그리고 기능별 사용자 접근 권한 매트릭스를 표시합니다.",
  },
  {
    tab: "users",
    selector: ".users-grid",
    title: "사용자 관리",
    description:
      "총 236명 사용자의 역할 분포를 도넛 차트로 확인하고, 검색/필터 가능한 사용자 목록에서 권한을 직접 편집할 수 있습니다.",
  },
  {
    tab: "audit",
    selector: ".sa-shell .pnl",
    title: "감사 로그",
    description:
      "전 사용자의 활동 이력(설정 변경 · 데이터 접근 · 보고서 발행 등)을 추적하고 CSV로 다운로드합니다. 감사 목적이므로 임의 수정이 불가능합니다.",
  },
];
