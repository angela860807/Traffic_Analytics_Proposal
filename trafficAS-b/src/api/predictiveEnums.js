// 예지보전 모듈 Enum 상수 — 백엔드 계약 (API 계약서 §2-4) 1:1 일치
// 응답에서 알 수 없는 값이 와도 화면이 깨지지 않도록 fallback 헬퍼 제공

export const DataSource = Object.freeze({
  REAL: 'REAL',
  OPEN_DATA: 'OPEN_DATA',
  SIMULATED: 'SIMULATED',
  FAULT_INJECTED: 'FAULT_INJECTED',
  MOCK: 'MOCK',
})

export const QualityStatus = Object.freeze({
  COMPLETE: 'COMPLETE',
  PARTIAL: 'PARTIAL',
  INSUFFICIENT: 'INSUFFICIENT',
})

export const TargetType = Object.freeze({
  CAMERA: 'CAMERA',
})

export const DetectionMethod = Object.freeze({
  RULE: 'RULE',
  ROBUST_Z_SCORE: 'ROBUST_Z_SCORE',
  TREND_PROJECTION: 'TREND_PROJECTION',
  CROSS_VALIDATION: 'CROSS_VALIDATION',
  LSTM_AUTOENCODER: 'LSTM_AUTOENCODER',
})

export const DetectorOperatingMode = Object.freeze({
  ACTIVE: 'ACTIVE',
  SHADOW: 'SHADOW',
  EXPERIMENTAL: 'EXPERIMENTAL',
})

export const AnomalyType = Object.freeze({
  CAMERA_OFFLINE: 'CAMERA_OFFLINE',
  FPS_DEGRADATION: 'FPS_DEGRADATION',
  FRAME_DROP_DEGRADATION: 'FRAME_DROP_DEGRADATION',
  LATENCY_DEGRADATION: 'LATENCY_DEGRADATION',
  BLUR_DEGRADATION: 'BLUR_DEGRADATION',
  OCR_QUALITY_DEGRADATION: 'OCR_QUALITY_DEGRADATION',
  RESOURCE_SATURATION: 'RESOURCE_SATURATION',
  NETWORK_INSTABILITY: 'NETWORK_INSTABILITY',
})

export const Severity = Object.freeze({
  WARNING: 'WARNING',
  CRITICAL: 'CRITICAL',
})

export const AnomalyStatus = Object.freeze({
  OPEN: 'OPEN',
  ACKNOWLEDGED: 'ACKNOWLEDGED',
  RECOVERED: 'RECOVERED',
  RESOLVED: 'RESOLVED',
  DISMISSED: 'DISMISSED',
})

export const TicketPriority = Object.freeze({
  P1: 'P1',
  P2: 'P2',
  P3: 'P3',
})

export const TicketStatus = Object.freeze({
  OPEN: 'OPEN',
  ASSIGNED: 'ASSIGNED',
  IN_PROGRESS: 'IN_PROGRESS',
  RESOLVED: 'RESOLVED',
  CLOSED: 'CLOSED',
})

export const HealthStatus = Object.freeze({
  NORMAL: 'NORMAL',
  DEGRADED: 'DEGRADED',
  CRITICAL: 'CRITICAL',
  OFFLINE: 'OFFLINE',
  BASELINE_LEARNING: 'BASELINE_LEARNING',
  INSUFFICIENT_DATA: 'INSUFFICIENT_DATA',
})

export const BaselineStatus = Object.freeze({
  READY: 'READY',
  LEARNING: 'LEARNING',
})

// 한글 라벨
export const HEALTH_STATUS_LABEL = {
  NORMAL: '정상',
  DEGRADED: '저하',
  CRITICAL: '위험',
  OFFLINE: '오프라인',
  BASELINE_LEARNING: '기준선 학습 중',
  INSUFFICIENT_DATA: '데이터 부족',
}

export const SEVERITY_LABEL = {
  WARNING: '경고',
  CRITICAL: '심각',
}

export const ANOMALY_STATUS_LABEL = {
  OPEN: '미처리',
  ACKNOWLEDGED: '확인됨',
  RECOVERED: '복구됨',
  RESOLVED: '해결됨',
  DISMISSED: '오탐 종료',
}

export const TICKET_STATUS_LABEL = {
  OPEN: '대기',
  ASSIGNED: '배정',
  IN_PROGRESS: '진행 중',
  RESOLVED: '해결',
  CLOSED: '종결',
}

export const ANOMALY_TYPE_LABEL = {
  CAMERA_OFFLINE: '카메라 오프라인',
  FPS_DEGRADATION: 'FPS 저하',
  FRAME_DROP_DEGRADATION: '프레임 손실 증가',
  LATENCY_DEGRADATION: '지연시간 증가',
  BLUR_DEGRADATION: '흐림 증가',
  OCR_QUALITY_DEGRADATION: 'OCR 품질 저하',
  RESOURCE_SATURATION: '리소스 과부하',
  NETWORK_INSTABILITY: '네트워크 불안정',
}

export const DETECTION_METHOD_LABEL = {
  RULE: '룰 기반',
  ROBUST_Z_SCORE: '통계 (z-score)',
  TREND_PROJECTION: '추세 예측',
  CROSS_VALIDATION: '교차 검증',
  LSTM_AUTOENCODER: 'LSTM AutoEncoder',
}

export const DATA_SOURCE_LABEL = {
  REAL: '실데이터',
  OPEN_DATA: '공개데이터',
  SIMULATED: '시뮬레이션',
  FAULT_INJECTED: '장애 주입',
  MOCK: '목업',
}

// 알 수 없는 enum 값이 응답에 와도 화면 깨지지 않게 fallback
export function safeEnum(value, allowed, fallback) {
  if (value && Object.prototype.hasOwnProperty.call(allowed, value)) return value
  return fallback
}

export function labelOf(map, value, fallback = '—') {
  return (value && map[value]) || fallback
}
