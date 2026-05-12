package com.example.traffic.service;

import com.example.traffic.common.enums.DetectionLogStatus;
import com.example.traffic.domain.Camera;
import com.example.traffic.domain.DetectionLog;
import com.example.traffic.domain.Vehicle;
import com.example.traffic.dto.request.DetectionRequest;
import com.example.traffic.dto.response.DetectionResponse;
import com.example.traffic.dto.response.FlowEventResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.repository.DetectionLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Slf4j
@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class DetectionLogService {

    private final DetectionLogRepository detectionLogRepository;
    private final CameraRepository cameraRepository;
    private final VehicleService vehicleService;
    private final VehicleFlowEventService vehicleFlowEventService;
    private final ObjectProvider<DetectionLogService> selfProvider;

    /**
     * [개선된 프로세스] 검증과 저장을 분리하고 Null 체크 강화
     */
    @Transactional // 클래스 레벨의 readOnly = true를 덮어씁니다.
    public Long processDetection(DetectionRequest request) {
        validateDetectionRequest(request);
        // 이제 여기서 시작되는 트랜잭션은 쓰기가 가능합니다.
        return selfProvider.getObject().saveDetectionData(request);
    }

    @Transactional
    public Long saveDetectionData(DetectionRequest request) {
        // 1. [규약 반영] cameraId 대신 cameraCode로 카메라 엔티티 조회
        Camera camera = cameraRepository.findByCameraCode(request.getCameraCode())
                .orElseThrow(() -> new BusinessException("미등록 카메라 코드입니다: " + request.getCameraCode(), HttpStatus.NOT_FOUND));

        DetectionLogStatus requestedStatus = resolveRequestedStatus(request);
        Vehicle vehicle = hasPlateNumber(request)
                ? vehicleService.getOrCreateVehicle(request.getPlateNumber())
                : null;

        // 3. DetectionLog 생성 및 저장
        DetectionLog logEntity = DetectionLog.builder()
                .camera(camera)
                .vehicle(vehicle)
                .plateNumber(request.getPlateNumber())
                .detectionType(request.getDetectionType())
                .confidenceScore(java.math.BigDecimal.valueOf(request.getConfidenceScore()))
                .imagePath(request.getImagePath())
                .imageUrl(request.getImageUrl())
                .detectedAt(request.getDetectedAt())
                .status(requestedStatus)
                .build();

        DetectionLog savedLog = detectionLogRepository.save(logEntity);

        if (requestedStatus == DetectionLogStatus.OCR_FAILED ||
                requestedStatus == DetectionLogStatus.DUPLICATE_SKIPPED) {
            return savedLog.getLogId();
        }

        // 4. [규약 반영] 조회한 Camera의 directionType 기준으로 흐름 이벤트 처리
        FlowEventResponse flowEvent = vehicleFlowEventService.processFlowEvent(savedLog);
        if (flowEvent == null) {
            savedLog.markDuplicateSkipped();
        } else {
            savedLog.markFlowEventCreated();
        }

        return savedLog.getLogId();
    }

    /**
     * [통합 규격 반영] 필수 값 검증 로직 (cameraCode로 변경)
     */
    private void validateDetectionRequest(DetectionRequest request) {
        if (request.getCameraCode() == null || request.getCameraCode().isBlank() ||
                request.getConfidenceScore() == null || request.getDetectedAt() == null ||
                request.getDetectionType() == null) {

            throw new BusinessException("AI 서버 전송 데이터 중 필수 값이 누락되었습니다.", HttpStatus.BAD_REQUEST);
        }

        // 신뢰도 점수 범위 추가 검증
        if (request.getConfidenceScore() < 0.0 || request.getConfidenceScore() > 1.0) {
            throw new BusinessException("신뢰도 점수는 0.0에서 1.0 사이여야 합니다.", HttpStatus.BAD_REQUEST);
        }

        DetectionLogStatus requestedStatus = resolveRequestedStatus(request);

        if (requestedStatus != DetectionLogStatus.OCR_FAILED && !hasPlateNumber(request)) {
            throw new BusinessException("번호판 없는 탐지 로그는 OCR_FAILED 상태로만 저장할 수 있습니다.", HttpStatus.BAD_REQUEST);
        }
    }

    private DetectionLogStatus resolveRequestedStatus(DetectionRequest request) {
        return request.getStatus() != null ? request.getStatus() : DetectionLogStatus.RECEIVED;
    }

    private boolean hasPlateNumber(DetectionRequest request) {
        return request.getPlateNumber() != null && !request.getPlateNumber().isBlank();
    }

    /**
     * [최신 로그 조회] 대시보드용 상위 100건 반환[cite: 17]
     */
    public List<DetectionResponse> getRecentLogs() {
        // Tip: 실제 운영 시에는 detectionLogRepository에서 fetch join을 사용하여
        // Camera와 Zone을 한 번에 가져오는 메서드를 사용하는 것이 좋습니다.
        return detectionLogRepository.findTop100ByOrderByDetectedAtDesc().stream()
                .map(DetectionResponse::from)
                .toList();
    }

    /**
     * [조건별 로그 검색] 차량번호 또는 구역별로 필터링된 로그 목록을 반환합니다.
     */
    public List<DetectionResponse> getFilteredLogs(String plateNumber, Long zoneId) {

        // 1. 차량 번호판 검색 조건이 있는 경우
        if (plateNumber != null && !plateNumber.isEmpty()) {
            return detectionLogRepository.findByPlateNumberOrderByDetectedAtDesc(plateNumber).stream()
                    .map(DetectionResponse::from)
                    .toList();
        }

        // 2. 구역 ID 검색 조건이 있는 경우 (레포지토리의 새 메서드 호출)
        if (zoneId != null) {
            return detectionLogRepository.findByCamera_Zone_ZoneIdOrderByDetectedAtDesc(zoneId).stream()
                    .map(DetectionResponse::from)
                    .toList();
        }

        // 3. 아무 조건도 없으면 최신 100건 반환
        return getRecentLogs();
    }
}
