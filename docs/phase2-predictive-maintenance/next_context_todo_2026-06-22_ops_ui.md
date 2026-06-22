# Next Context TODO - `/admin/ops` Predictive Ops UI

작성일: 2026-06-22

## 1. 현재 반영된 상태

- `/admin/ops` 이상 목록 선택 컨텍스트를 목록 근처로 이동했다.
- 우선조치 이상 상세 카드는 `문제 장비`, `인지된 문제`를 상단에 크게 표시한다.
- `MTTA`, `MTTR` KPI는 `평균 응답 시간`, `평균 복구 시간`으로 한국어화했다.
- 상태 배지 영역은 12칸 그리드로 정리했다.
  - 데스크톱 기준 `이상 상태`, `정비 상태`, `탐지 방식`, `우선순위`, `탐지기`가 `2 + 2 + 2 + 2 + 4` 비율로 한 줄을 채운다.
- `조치 판단 지표`는 `시계열 판단 근거 요약`으로 변경했다.
- 판단 근거는 `핵심 원인`과 `보조 근거`로 구분한다.
- 상세 카드에 `기준선 학습 -> 최근 관측 -> 예측/조치 시점` 흐름을 추가했다.
- 지표별 시계열 흐름은 그래프 없이 텍스트 요약만 표시한다.
  - `관측 시각`
  - `낮아질수록 위험` 또는 `높아질수록 위험`
  - `과거 기준`
  - `최근 관측`
  - `조치 기준선`
- 프론트 모델에 `sampledAt`, `metricScore`, `context`, `baseline`을 포함했다.

## 2. 남은 TODO

### 2-1. UI 확인

- [ ] 사용자가 직접 frontend build 후 `/admin/ops`를 확인한다.
- [ ] 상세 카드의 상태 배지 폭, 글자 크기, 말줄임이 데스크톱 화면에서 자연스러운지 확인한다.
- [ ] 좁은 화면에서 상태 배지, 시계열 흐름, 판단 근거 요약이 겹치지 않는지 확인한다.
- [ ] `시계열 판단 근거 요약` 문구가 발표/시연 맥락에서 직관적인지 확인한다.
- [ ] 목록 선택 컨텍스트가 목록과 상세 카드의 연결성을 충분히 보완하는지 운영자 관점에서 확인한다.

### 2-2. API 계약 검토

- [ ] 이상 이벤트 상세 응답에 최근 N개 시계열 샘플을 추가할지 결정한다.
  - 현재 상세 카드는 `baseline`, `sampledAt`, `observedValue`, `thresholdValue` 기반의 요약만 표시한다.
  - 실제 sparkline이 필요하면 API 계약에 `series: [{ sampledAt, value }]` 또는 bucket 요약 필드가 필요하다.
- [ ] 기준선 기간, 최근 관측 시각, 예측/조치 시점이 실제 운영 데이터에서 모두 채워지는지 E2E로 확인한다.
- [ ] `sampledAt`이 없는 evidence에 대한 fallback 문구가 충분히 자연스러운지 확인한다.

### 2-3. 후속 고도화

- [ ] SHADOW LSTM AutoEncoder 결과는 운영 판단과 혼동되지 않게 별도 비교 영역으로 유지한다.
- [ ] 실제 시계열 샘플 API가 추가되면 현재 텍스트 요약 아래에 sparkline을 선택적으로 붙일지 재검토한다.
- [ ] 담당자 후보 API와 정비 변경 이력 API가 운영 DB seed에서도 정상 동작하는지 확인한다.
- [ ] `USER` 역할이 정비 담당자 후보와 assign API에서 모두 차단되는지 통합 확인한다.

### 2-4. 새 PC 시연 준비

- [ ] 외부 PC에서 Docker로 처음 실행할 때는 DB volume이 비어 있으므로 시연 데이터를 다시 주입한다.
  - `docker compose up -d --build`는 서비스 이미지와 빈 PostgreSQL volume을 준비하는 단계다.
  - `data.sql`은 기본 zone/camera/admin 계정 정도만 넣는다.
  - 예지보전 이상 이벤트와 정비 티켓은 상태 샘플을 넣고 FastAPI 평가가 돌아야 생성된다.
- [ ] 새 PC에서 예지보전 시연을 할 때는 아래 CSV 주입 절차를 준비한다.

```powershell
docker compose up -d --build

.\tools\predictive_demo\import_health_samples.ps1 `
  -CsvPath "tools\predictive_demo\camera-health-rule-trigger-samples.csv" `
  -BaseUrl "http://localhost:8080" `
  -InternalApiKey "traffic-ai-internal-key-2026"
```

- [ ] 새 DB에서 migration/seed 재현성을 별도로 확인한다.
  - 현재 프로젝트는 migration 파일을 보관하지만 자동 migration runner가 명확히 켜져 있지 않고, `spring.jpa.hibernate.ddl-auto=update`와 `data.sql`에 일부 의존한다.
  - 시연 전 `detector_versions`, `anomaly_policies`, `camera_health_samples`, `anomaly_events`, `maintenance_tickets` row 존재 여부를 확인한다.
- [ ] YOLO/OCR 과속탐지 시연 여부를 결정한다.
  - 예지보전 UI만 시연하면 기존 YOLO/OCR 영상 업로드 명령은 필수 아님.
  - 기존 실시간 영상분석, 번호판 OCR, 과속 위반 저장까지 같이 보여줄 때만 `fastapi-server/scripts/pretty_stream_video_file.js` 또는 `stream_video_file.py` 계열 명령이 필요하다.
  - 예지보전은 현재 `tools/predictive_demo/import_health_samples.ps1`로 카메라 상태 시계열 샘플을 주입하는 방식이 더 안정적이다.
- [ ] 외부 PC에 `fastapi-server/models/best.pt`가 포함되어 있는지 확인한다.
  - compose는 `./fastapi-server/models:/app/models:ro`를 마운트한다.
  - YOLO/OCR 영상분석을 같이 시연하려면 모델 파일과 테스트 영상 파일도 외부 PC에 있어야 한다.

## 3. 확인 명령

빌드는 사용자가 직접 수행한다. 다음 명령은 빌드 없이 검증할 때 사용한다.

```powershell
cd C:\Users\user\Desktop\Traffic_Analytics_Proposal\trafficAS-b

npm test -- --run tests/predictiveApi.test.js tests/usePredictivePerm.test.js

node -e "const fs=require('fs'); const { parse, compileTemplate }=require('@vue/compiler-sfc'); const file='src/views/admin/OpsView.vue'; const source=fs.readFileSync(file,'utf8'); const parsed=parse(source,{filename:file}); if(parsed.errors.length){console.error(parsed.errors); process.exit(1);} const tpl=compileTemplate({source:parsed.descriptor.template.content,filename:file,id:'ops'}); if(tpl.errors.length){console.error(tpl.errors); process.exit(1);} console.log('OpsView.vue SFC parse ok');"

cd C:\Users\user\Desktop\Traffic_Analytics_Proposal
git diff --check
```

## 4. 관련 문서

- `docs/phase2-predictive-maintenance/merge_workflow_troubleshooting_2026-06-18.md`
- `docs/phase2-predictive-maintenance/병합_검증_작업정리_2026-06-21.md`
- `docs/phase2-predictive-maintenance/03_API_계약서.md`
- `docs/phase2-predictive-maintenance/03_API_계약서_ver2 (1).md`

## 5. 커밋 메시지 후보

```text
Improve predictive ops detail readability and time-series evidence summary
```
