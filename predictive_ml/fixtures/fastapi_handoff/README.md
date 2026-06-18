# FastAPI 인계용 Fixture

이 폴더는 FastAPI 담당자가 `predictive_ml` 패키지를 연동할 때 참고할 요청/응답 예시입니다.

AI 패키지 내부는 Python dataclass와 snake_case 필드를 사용합니다. FastAPI adapter에서는 API 계약서 기준의 camelCase JSON을 명시적으로 dataclass 입력으로 변환하고, detector 결과도 다시 camelCase JSON 응답으로 변환해야 합니다.

## 파일 목록

| 파일 | 용도 |
|---|---|
| `camera_health_rule_warning_request.json` | `POST /internal/v1/anomaly-detection/camera-health/evaluate` Rule Detector 요청 예시 |
| `camera_health_rule_warning_response.json` | Rule Detector 예상 응답 예시 |
| `camera_degradation_critical_request.json` | 기준선과 최근 추세를 포함한 악화 탐지 요청 예시 |
| `camera_degradation_critical_response.json` | robust z-score + trend projection 예상 응답 예시 |
| `lstm_shadow_critical_request.json` | LSTM-AE SHADOW 추론용 30분 sequence 요청 예시 |
| `lstm_shadow_critical_response.json` | LSTM-AE SHADOW 예상 응답 예시 |

## Adapter 연동 메모

- FastAPI는 카메라 상태 Rule 평가에서 `detect_rules()`를 호출합니다.
- FastAPI는 기준선/추세 기반 악화 평가에서 `detect_degradation()`을 호출합니다.
- FastAPI는 LSTM-AE SHADOW 추론에서 `predict_anomaly()`를 호출합니다.
- LSTM-AE 결과는 반드시 `shadowCandidates`에만 담아 반환합니다.
- SHADOW 결과만으로는 `AnomalyEvent`나 `MaintenanceTicket`을 생성하지 않습니다.
- SHADOW 추론 런타임 의존성은 `torch`, `numpy`, `scikit-learn`입니다.
- 모델 경로는 `TAS_PM_LSTM_AE_MODEL_DIR` 환경변수로 변경할 수 있습니다.

## 주의사항

- JSON 필드명과 enum 값은 API 계약서와 DB enum에 맞춘 값이므로 한글로 변경하지 않습니다.
- 예시 응답의 수치는 2026-06-18 런타임 검증에서 확인한 대표 케이스를 기준으로 작성했습니다.
- FastAPI 담당자는 이 fixture를 그대로 응답으로 고정하지 말고, adapter 변환 테스트와 계약 확인용으로 사용하면 됩니다.
