package com.example.traffic.service;

import com.example.traffic.domain.Camera;
import com.example.traffic.domain.DetectionLog;
import com.example.traffic.domain.Vehicle;
import com.example.traffic.dto.request.DetectionRequest;
import com.example.traffic.dto.response.DetectionResponse;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.repository.DetectionLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class DetectionLogService {

    private final DetectionLogRepository detectionLogRepository;
    private final CameraRepository cameraRepository;
    private final VehicleService vehicleService;
    private final VehicleFlowEventService vehicleFlowEventService;

    /**
     * [탐지 프로세스] AI 탐지 데이터를 처리하여 차량 식별 및 흐름 분석 수행
     */
    @Transactional
    public Long processDetection(DetectionRequest request) {
        // 1. 카메라 확인 (연관 관계를 위해 필수)[cite: 17]
        Camera camera = cameraRepository.findById(request.getCameraId())
                .orElseThrow(() -> new IllegalArgumentException("미등록 카메라입니다. ID: " + request.getCameraId()));

        // 2. 차량 확인 및 자동 등록[cite: 16, 17]
        Vehicle vehicle = vehicleService.getOrCreateVehicle(request.getPlateNumber());

        // 3. 탐지 로그 빌드 및 저장[cite: 7, 17]
        DetectionLog log = DetectionLog.builder()
                .camera(camera)
                .vehicle(vehicle)
                .plateNumber(request.getPlateNumber())
                .confidenceScore(request.getConfidenceScore() != null ?
                        java.math.BigDecimal.valueOf(request.getConfidenceScore()) : null)
                .imagePath(request.getImagePath())
                .detectedAt(request.getDetectedAt())
                .build();

        DetectionLog savedLog = detectionLogRepository.save(log);

        // 4. 즉시 흐름 분석 호출 (이벤트 중복 제거 및 IN/OUT 판별)[cite: 17]
        vehicleFlowEventService.processFlowEvent(savedLog);

        return savedLog.getLogId();
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