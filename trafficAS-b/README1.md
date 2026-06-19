# TAS 2차 — 예지보전 작업 문서

> 2026-06-11 · 실무자용 핸드북. 한 화면 안에서 필요한 것 다 찾을 수 있게 구성.

---

## ⚡ TL;DR — 지금 알아야 할 것

| 질문 | 답 |
|---|---|
| 별도 부서야? | **아니. 시설운영팀(OpsView)에 흡수.** /admin/ops 안에서 모든 게 일어남 |
| 어떤 탭에 뭐가 들어가? | status (KPI 스트립) / cams (KPI+모달 헬스 패널) / fault (이상·티켓) / settings (정책) |
| 어디까지 됐어? | Step 1·2 완료 (status / cams 탭) — 다음은 Step 3 (fault 탭) |
| 백엔드 없어도 돼? | OK. mock 폴백 자동 동작. `admin` / `1234`로 로그인 후 /admin/ops |
| 어디 가서 코드 봐야 해? | `src/api/predictiveApi.js` (15개 함수) + `src/views/admin/OpsView.vue` (UI) |
| 외부 라이브러리 추가? | 0. 차트는 SVG 직접, polling은 자체 composable. |

---

## 📁 파일 맵 — "X 하려면 어디?"

### 신규 파일 (4개)
| 파일 | 무엇 | 언제 건드리나 |
|---|---|---|
| `src/api/predictiveEnums.js` | Enum 14종 + 한글 라벨 + safeEnum | Enum 추가 / 라벨 변경 |
| `src/api/predictiveApi.js` | 15개 함수 + 정렬 화이트리스트 | API 추가 / payload 변경 |
| `src/composables/usePolling.js` | 30초 polling + 탭 비활성 중단 | polling 주기 조정 |
| `src/composables/usePredictivePerm.js` | 권한 헬퍼 7개 | 권한 분기 추가 |

### 수정 파일 (2개)
| 파일 | 변경 |
|---|---|
| `src/api/client.js` | `X-Request-Id` 자동 + 에러 정규화 + `apiPost` 추가 |
| `src/views/admin/OpsView.vue` | status/cams 탭 + 카메라 모달에 예지 흡수 |

### 제거 파일 (방향 전환으로 폐기)
- ~~`src/views/admin/predictive/`~~ 폴더 전체
- ~~`src/components/predictive/DataSourceBadge.vue`~~

---

## 🧭 어디에 뭐 있나 — 화면 ↔ 파일 ↔ 위치

| 보고 싶은 것 | 어느 화면 | 어느 탭 | 어느 줄(약) |
|---|---|---|---|
| 평균 Health Score | `/admin/ops` | status | OpsView.vue: `pm-strip` 5박스 |
| 악화 예측 N건 | `/admin/ops` | status | OpsView.vue: `pm-strip` 2번째 |
| 카메라 표 Health 컬럼 | `/admin/ops` | status / cams | `pm-cam-tbl` |
| 악화 예측 배지 | 카메라명 옆 | status / cams | `.pm-pred-bdg` |
| 카메라별 시계열 차트 | 카메라 모달 | cams (행 클릭) | `.cm-pm` 섹션 |
| 4지표 카드 (FPS/지연/CPU/OCR) | 카메라 모달 | cams (행 클릭) | `.cm-pm-mtx` |
| 이상 이벤트 목록 ⏳ | `/admin/ops` | fault | 아직 미구현 |
| 정비 티켓 ⏳ | `/admin/ops` | fault | 아직 미구현 |
| 탐지 정책 ⏳ | `/admin/ops` | settings | 아직 미구현 |

---

## 🛣 라우트 — 권한 매트릭스

### 현재 라우트 (변경 없음, 흡수형)
| Path | 화면 | 가드 |
|---|---|---|
| `/admin/ops` | OpsView (시설운영 + 예지보전 통합) | ADMIN |
| `/admin/predictive/*` (옛) | → `/admin/ops` 308 redirect | — |

### 권한 매트릭스 (요구사항 정의서 2-4 / 7-2절 기준, DB 협의 2026-06-12 반영)
| 액션 | USER | OPERATOR | MAINTAINER | ADMIN |
|---|:-:|:-:|:-:|:-:|
| 대시보드 조회 | ✗ | ✓ | ✓ | ✓ |
| 이벤트 acknowledge | ✗ | ✓ | ✗ | ✓ |
| 이벤트 resolve | ✗ | ✓ | ✗ | ✓ |
| 이벤트 dismiss(오탐 종료) | ✗ | ✓ | ✗ | ✓ |
| **수동 정비 티켓 생성** | ✗ | ✓ | ✗ | ✓ |
| 티켓 배정 | ✗ | ✓ | ✗ | ✓ |
| 티켓 상태 변경 (ASSIGNED→IN_PROGRESS→RESOLVED) | ✗ | ✓ | ✓ | ✓ |
| **티켓 CLOSED 처리** | ✗ | ✓ | ✗ | ✓ |
| 정책 수정 | ✗ | ✗ | ✗ | ✓ |

**MAINTAINER 상태 전이 제한**:
- `ASSIGNED → IN_PROGRESS` (작업 시작)
- `IN_PROGRESS → RESOLVED` (작업 완료, note 필수)
- `CLOSED`로 전환 불가 — OPERATOR/ADMIN이 확인 후 처리

```js
// 사용법
import { usePredictivePerm } from '@/composables/usePredictivePerm'
const {
  canResolveAnomaly,
  canCreateTicket,
  canCloseTicket,
  canChangeTicketStatus,
  canTransitionTicket,   // (fromStatus, toStatus) → boolean
  canEditPolicy,
} = usePredictivePerm()

// 티켓 행에서 다음 가능한 전이 버튼 노출
<button v-if="canTransitionTicket(ticket.status, 'IN_PROGRESS')">작업 시작</button>
<button v-if="canTransitionTicket(ticket.status, 'CLOSED')">최종 종결</button>
```

---

## 🍳 레시피 — 자주 쓰는 패턴

### 1. polling 화면 만들기
```js
import { usePolling } from '@/composables/usePolling'
import { getSummary } from '@/api/predictiveApi'

const { data, loading, error, stale, refresh } = usePolling(
  () => getSummary({ dataSource: 'REAL' }),
  { intervalMs: 30000 }
)
```

### 2. 페이지 API 호출
```js
import { listCameras } from '@/api/predictiveApi'

const result = await listCameras({
  healthStatus: 'DEGRADED',
  page: 0,
  size: 20,
  sort: 'healthScore,asc',  // 화이트리스트 밖이면 무시
})
// result: { content, page, size, totalElements, totalPages, sort }
```

### 3. 시간 포맷 (offset 포함)
```js
import { isoWithOffset } from '@/api/predictiveApi'

const from = isoWithOffset(new Date())
// → 2026-06-11T14:05:00+09:00 (Z 아님)
```

### 4. Enum 비교 / 라벨
```js
import { AnomalyStatus, HEALTH_STATUS_LABEL, safeEnum, labelOf } from '@/api/predictiveEnums'

// 비교 — 문자열 직접 X
if (status === AnomalyStatus.OPEN) ...

// 미지의 값 대비
const s = safeEnum(raw.status, AnomalyStatus, AnomalyStatus.OPEN)

// 한글 라벨
labelOf(HEALTH_STATUS_LABEL, 'DEGRADED')  // → "저하"
```

### 5. 에러 처리
```js
try {
  await acknowledgeAnomaly(101, { note: '현장 점검 요청' })
} catch (err) {
  const n = err.normalized
  if (n.code === 'CONFLICT')             alert('이미 처리됨')
  else if (n.code === 'FORBIDDEN')       alert('권한 없음')
  else if (n.code === 'INVALID_STATE_TRANSITION') alert('지금은 전환 불가')
  else                                    alert(n.message)
}
```

### 6. fieldErrors → 폼 매핑
```js
import { fieldErrorMap } from '@/api/client'

const errMap = fieldErrorMap(err.normalized)
// errMap.toStatus = '허용되지 않은 상태 전이입니다.'
```

### 7. mock 폴백 (백엔드 미연동)
`OpsView.vue` 패턴 — try/catch로 호출하고 catch에서 로컬 더미 사용. `loadError`는 set하지 않아 화면 비지 않음.

---

## 🎨 UI 컨벤션 (예지 추가 요소)

### 색상 분기
| 톤 | 의미 | 색 |
|---|---|---|
| `gr` 녹색 | 정상 (Health 70+) | `#059669` |
| `yl` 노랑 | 저하 (Health 50~70) | `#d97706` |
| `rd` 빨강 | 위험 (Health <50) | `#dc2626` |
| `gy` 회색 | 오프라인 / 데이터 없음 | `#9aa6b8` |
| 주황 | **악화 예측** (10분 내 임계) | `#ea580c` |
| 파란 | **예지 운영 점수** (Health 평균 등) | `#2563eb` |
| 보라 | 기준선 학습 / SHADOW | `#7c3aed` |

### 배지 / 칩
| 클래스 | 용도 |
|---|---|
| `.pm-hs` | Health Score 숫자 배지 (색 분기) |
| `.pm-pred-bdg` | 악화 예측 주황 배지 (카메라명 옆) |
| `.pm-kpi` | status 탭 상단 KPI 칩 (5개) |
| `.cm-pm-score` | 모달 헤더 Health 점수 배지 |
| `.cm-pm-pred` | 모달 헤더 악화 예측 알림 박스 |

---

## 🔌 API 15개 — 한눈에

### 운영 요약 / 카메라
| 함수 | 메서드 + 경로 | 권한 |
|---|---|---|
| `getSummary()` | GET `/summary` | OPERATOR+ |
| `listCameras()` | GET `/cameras` | OPERATOR+ |
| `getCameraHealthHistory(id)` | GET `/cameras/{id}/health-history` | OPERATOR+ |
| `getTrafficContext()` | GET `/traffic-context` | OPERATOR+ |

### 이상 이벤트
| 함수 | 메서드 + 경로 | 권한 |
|---|---|---|
| `listAnomalyEvents()` | GET `/anomaly-events` | OPERATOR+ |
| `getAnomalyEvent(id)` | GET `/anomaly-events/{id}` | OPERATOR+ |
| `acknowledgeAnomaly(id, {note})` | POST `.../acknowledge` | OPERATOR/ADMIN |
| `resolveAnomaly(id, {confirmedCause, resolutionNote})` | POST `.../resolve` | OPERATOR/ADMIN |
| `dismissAnomaly(id, {reason})` | POST `.../dismiss` | OPERATOR/ADMIN |

### 정비 티켓
| 함수 | 메서드 + 경로 | 권한 |
|---|---|---|
| `listMaintenanceTickets()` | GET `/maintenance-tickets` | OPERATOR+ |
| `createMaintenanceTicket()` | POST `/maintenance-tickets` | OPERATOR/ADMIN |
| `assignMaintenanceTicket(id, {assigneeId, note})` | POST `.../assign` | OPERATOR/ADMIN |
| `changeTicketStatus(id, {toStatus, note})` | POST `.../status` | OPERATOR/MAINTAINER/ADMIN |

### 정책
| 함수 | 메서드 + 경로 | 권한 |
|---|---|---|
| `listPolicies()` | GET `/policies` | OPERATOR+ |
| `updatePolicy(code, payload)` | PATCH `/policies/{code}` | **ADMIN 전용** |

---

## 🔤 Enum 14종 — 한눈에

| Enum | 값 |
|---|---|
| `DataSource` | REAL · OPEN_DATA · SIMULATED · FAULT_INJECTED · MOCK |
| `QualityStatus` | COMPLETE · PARTIAL · INSUFFICIENT |
| `TargetType` | CAMERA |
| `DetectionMethod` | RULE · ROBUST_Z_SCORE · TREND_PROJECTION · CROSS_VALIDATION · LSTM_AUTOENCODER |
| `DetectorOperatingMode` | ACTIVE · SHADOW · EXPERIMENTAL |
| `AnomalyType` | CAMERA_OFFLINE · FPS_DEGRADATION · FRAME_DROP_DEGRADATION · LATENCY_DEGRADATION · BLUR_DEGRADATION · OCR_QUALITY_DEGRADATION · RESOURCE_SATURATION · NETWORK_INSTABILITY |
| `Severity` | WARNING · CRITICAL |
| `AnomalyStatus` | OPEN · ACKNOWLEDGED · RECOVERED · RESOLVED · DISMISSED |
| `TicketPriority` | P1 · P2 · P3 |
| `TicketStatus` | OPEN · ASSIGNED · IN_PROGRESS · RESOLVED · CLOSED |
| `HealthStatus` | NORMAL · DEGRADED · CRITICAL · OFFLINE · BASELINE_LEARNING · INSUFFICIENT_DATA |
| `BaselineStatus` | READY · LEARNING |

한글 라벨은 `*_LABEL` 형태로 모두 노출 (예: `HEALTH_STATUS_LABEL`).

---

## ⚠️ 에러 코드 → UI 대응

| code (HTTP) | UI 처리 |
|---|---|
| `UNAUTHORIZED` (401) | 토큰 만료 → 로그인 이동 |
| `FORBIDDEN` (403) | "권한 부족" 메시지 + 버튼 숨김 |
| `RESOURCE_NOT_FOUND` (404) | "존재하지 않음" + 목록 복귀 |
| `CONFLICT` (409) | "이미 처리됨" + 새로고침 |
| `INVALID_STATE_TRANSITION` | 전환 버튼 비활성화 |
| `BASELINE_NOT_READY` | "기준선 학습 중 (X/Y 표본)" |
| `INTERNAL_DETECTOR_UNAVAILABLE` | polling 유지 + STALE 배지 |
| 5xx 일반 | 에러 메시지 + 재시도 버튼 |

---

## 🚫 절대 하면 안 되는 것

1. **view/component에서 axios 직접 호출** — 무조건 `predictiveApi.js` 함수 경유
2. **Enum 문자열 직접 비교** — `if (s === 'OPEN')` X → `if (s === AnomalyStatus.OPEN)` O
3. **`Date.toISOString()` 그대로 query 사용** — UTC `Z`가 들어감. `isoWithOffset()` 사용
4. **SHADOW 결과로 운영 이벤트 만들기** — `shadowCandidates`는 비교용. AnomalyEvent / Ticket 생성 금지
5. **`shadowCandidates.topFeatures`를 "기여도"로 표시** — 평균 재구성 오차 상위일 뿐
6. **정렬 화이트리스트 밖 필드** — 400 떨어짐. `predictiveApi.js`의 `SORT_ALLOWED` 참고
7. **resolve/dismiss/RESOLVED에 빈 메모 제출** — 클라에서 막아야 함
8. **MAINTAINER에게 CLOSED 버튼 노출** — MAINTAINER는 RESOLVED까지만. `canTransitionTicket()`로 차단
9. **`thresholdDirection` 화면 표시 (B방안)** — DB·백엔드 내부값. 프론트는 임계값 숫자만 표시
10. **정책 화면에서 단일 `consecutiveWindows` 가정** — `warningConsecutiveWindows` / `criticalConsecutiveWindows` 2개로 분리됨

---

## ✅ 작업 진행 상태

### 완료
- [x] **Step 0** API client + Enum + polling/perm composable (커밋 `ab48a16`)
- [x] **Step 1** status 탭: KPI 스트립 5개 + 카메라 표 Health 컬럼 (커밋 `9709afe`)
- [x] **Step 2** cams 탭: KPI 9박스 + 카메라 모달 헬스 패널 (sparkline + 4지표) (커밋 `a0386ee`)

### 미완료
- [ ] **Step 3** fault 탭 통합
  - [ ] 알람 타임라인에 `악화 예측` 배지 + 카운트다운
  - [ ] 진행 중 장애 카드에 SHADOW `비교 모델` 영역
  - [ ] 관측값/기준값/임계값 비교 표 + 원인 후보
  - [ ] 전체 장애 목록에 priority(P1/P2/P3) + SLA 잔여 시간
  - [ ] 허용 상태 전이만 노출 (`INVALID_STATE_TRANSITION` 클라 차단)
  - [ ] RESOLVED 전환 시 조치 메모 필수 modal
- [ ] **Step 4** settings 탭 통합
  - [ ] "탐지 정책" 5번째 블록
  - [ ] 정책 코드별 임계치 + 활성 토글
  - [ ] Rule / z-score / 추세 입력 항목 분리
  - [ ] 수정 전 확인 modal + ADMIN 외 read-only
- [ ] **Step 5** 마무리
  - [ ] 권한별 분기 동작 실증
  - [ ] 에러 UI 텍스트 확정
  - [ ] 반응형 (1024~1920px)
  - [ ] 단위 테스트 3종

---

## 🧪 시연 시나리오

1. `admin` / `1234` 로 로그인
2. **시설운영팀** 진입 (`/admin/ops` 또는 부서 이동)
3. **장비 현황(status)** 탭 — 상단 예지 KPI 5개 확인 (Health 평균 73.2 / 악화 예측 2건 등)
4. 카메라 표에서 **가양IC_본선_C2** 클릭 → 모달 열림
5. 모달 하단 **헬스 분석** 섹션 — SVG 차트 + 4지표 카드 확인
   - 파란 실선: 30분 추세
   - 회색 점선: 기준선 75
   - 빨간 점선: 임계 50
   - 주황 점선: 향후 10분 예측 (악화 예측 카메라만)
6. **카메라(cams)** 탭 — KPI 9박스 + 전체 목록 표 Health 컬럼 확인

---

## 🧮 mock 데이터 구조

```js
// OpsView.vue의 cams 배열 (5건)
{
  // 기존 운영 필드
  name, loc, st, stTone, lat, ts, id,
  // 예지 필드 (추가)
  healthScore,      // 0~100
  healthStatus,     // NORMAL/DEGRADED/CRITICAL/OFFLINE/BASELINE_LEARNING
  predictedRisk,    // 0 또는 1
  predictedType,    // "FPS 저하" / "OCR 품질 저하" (predictedRisk > 0일 때만)
  predictedAt,      // "10:44" (임계 도달 예상 시각)
}
```

| 카메라 | 상태 | Health | 예측 |
|---|---|---|---|
| 한남대교_남단_A4 | 정상 | 88.4 | — |
| 가양IC_본선_C2 | 지연 | 67.2 | FPS 저하 / 10:44 |
| 정릉터널_입구_B1 | 장애 | 0 | — |
| 잠실대교_북단_D2 | 정상 | 91.8 | — |
| 강변북로_여의도_E1 | 지연 | 58.6 | OCR 품질 저하 / 10:51 |

---

## 🌳 브랜치

```
main
└─ feat/predictive-infra      [원격 ✓]   API client 인프라
   └─ feat/predictive-routes  [로컬]     OpsView 통합 (Step 1·2)
                              push 보류 — 명시 전까지 안 함
```

| 커밋 | 내용 |
|---|---|
| `ab48a16` | 인프라 (API/Enum/polling/perm) |
| `7798023` | (폐기됨) 6개 라우트 + 빈 view |
| `1cb41f1` | (폐기됨) 별도 대시보드 실구현 |
| `1868b71` | (폐기됨) DeptSwitcher 통합 |
| `b305dc7` | refactor: 별도 라우트/뷰 제거 |
| `9709afe` | Step 1: status 탭 흡수 |
| `a0386ee` | Step 2: cams 탭 + 모달 흡수 |

---

## 🧰 정책 화면 구현 시 주의 (DB 협의 2026-06-12)

### thresholdDirection — **표시 안 함 (B방안)**
- `thresholdDirection`은 DB·백엔드 내부에서 비교 방향 결정에 사용
- 프론트는 응답에 들어오지 않으며, 들어오더라도 화면에 표시하지 않음
- 정책 화면은 **숫자만** 표시. 예: "경고 임계 10.0 / 위험 임계 5.0"
- "낮을수록 위험" / "높을수록 위험" 문구는 표시하지 않음

### consecutiveWindows — 2필드로 분리됨
응답·요청 모두 단일 `consecutiveWindows` 가 아니라 다음 2필드:
- `warningConsecutiveWindows`
- `criticalConsecutiveWindows`

대부분 정책은 두 값이 동일하지만 **RESOURCE_SATURATION**은 다름 (경고 5분 / 위험 3분).

```js
// 정책 수정 시 payload
updatePolicy('RESOURCE_SATURATION_RULE_V1', {
  warningThreshold: 85,
  criticalThreshold: 95,
  warningConsecutiveWindows: 5,
  criticalConsecutiveWindows: 3,
  // thresholdDirection 보내지 않음
})
```

### 정책 화면 표시 패턴 (예시)
```
FPS 저하 정책
  경고 임계: 10.0 / 위험 임계: 5.0
  연속 윈도: 경고 3회 / 위험 3회

자원 포화 정책
  경고 임계: 85% / 위험 임계: 95%
  연속 윈도: 경고 5회 / 위험 3회   ← 두 값 다름
```

---

## 📚 헬스 분석이 뭐냐 (비기술자용 한 줄)

> **장애 나기 *전에* 추세를 보여줘서 미리 대응할 수 있게 만드는 것.**

기존: 카메라가 죽은 *후에* 알람
예지: FPS 24 → 20 → 15 → 10 (임계) → 5 (장애) 하강 곡선의 *세 번째* 지점에서 "곧 임계 도달" 알림

운영자 관점: "**오늘 출동해야 하는 카메라 우선순위 결정 도구**"
