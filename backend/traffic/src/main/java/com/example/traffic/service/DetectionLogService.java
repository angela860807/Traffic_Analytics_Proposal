package com.example.traffic.service;

import com.example.traffic.domain.Camera;
import com.example.traffic.domain.DetectionLog;
import com.example.traffic.domain.Vehicle;
import com.example.traffic.dto.request.DetectionRequest;
import com.example.traffic.dto.response.DetectionResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.repository.DetectionLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
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
    public Long processDetection(DetectionRequest request) {
        // 1. 피드백 2-3: 필수 응답값 null 검증 (검증은 트랜잭션 밖에서 수행)
        validateDetectionRequest(request);

        // 2. 피드백 2-1: 실제 DB 저장은 별도의 트랜잭션 메서드로 호출
        return selfProvider.getObject().saveDetectionData(request);
    }

    @Transactional
    public Long saveDetectionData(DetectionRequest request) {
        LocalDateTime duplicateWindow = request.getDetectedAt().minusSeconds(2);
        boolean isDuplicateLog = detectionLogRepository.existsByPlateNumberAndDetectedAtAfter(
                request.getPlateNumber(),
                duplicateWindow
        );

        if (isDuplicateLog) {
            log.info("중복된 탐지 로그 요청(2초 이내)입니다. 스킵합니다. 차량번호: {}", request.getPlateNumber());
            return -1L; // 중복임을 나타내는 마커값 반환[cite: 10, 15]
        }

        Camera camera = cameraRepository.findById(request.getCameraId())
                .orElseThrow(() -> new BusinessException("미등록 카메라입니다. ID: " + request.getCameraId(), HttpStatus.NOT_FOUND));

        Vehicle vehicle = vehicleService.getOrCreateVehicle(request.getPlateNumber());

        DetectionLog log = DetectionLog.builder()
                .camera(camera)
                .vehicle(vehicle)
                .plateNumber(request.getPlateNumber())
                .confidenceScore(java.math.BigDecimal.valueOf(request.getConfidenceScore()))
                .imagePath(request.getImagePath())
                .detectedAt(request.getDetectedAt())
                .build();

        DetectionLog savedLog = detectionLogRepository.save(log);
        vehicleFlowEventService.processFlowEvent(savedLog);

        return savedLog.getLogId();
    }

    /**
     * 피드백 2-3 반영: AI 응답 값 null 검증 로직
     */
    private void validateDetectionRequest(DetectionRequest request) {
        if (request.getCameraId() == null || request.getPlateNumber() == null ||
                request.getConfidenceScore() == null || request.getDetectedAt() == null) {

            throw new BusinessException("AI 분석 응답 필수 값이 누락되었습니다.", HttpStatus.BAD_GATEWAY);
        }
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