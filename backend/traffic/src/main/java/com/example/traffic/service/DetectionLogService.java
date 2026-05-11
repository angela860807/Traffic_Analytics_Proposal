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

import java.math.BigDecimal;
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
    @Transactional // 클래스 레벨의 readOnly = true를 덮어씁니다.
    public Long processDetection(DetectionRequest request) {
        validateDetectionRequest(request);
        // 이제 여기서 시작되는 트랜잭션은 쓰기가 가능합니다.
        return selfProvider.getObject().saveDetectionData(request);
    }

    @Transactional
    public Long saveDetectionData(DetectionRequest request) {
        // 1. 카메라 조회
        Camera camera = cameraRepository.findByCameraCode(request.getCameraCode())
                .orElseThrow(() -> new BusinessException("미등록 카메라 코드: " + request.getCameraCode(), HttpStatus.NOT_FOUND));

        // 2. [중복 제거 로직 추가] 동일 카메라에서 5초 이내 같은 번호판이 찍혔는지 확인
        LocalDateTime fiveSecondsAgo = request.getDetectedAt().minusSeconds(5);
        boolean isDuplicate = detectionLogRepository.existsByCameraAndPlateNumberAndDetectedAtAfter(
                camera, request.getPlateNumber(), fiveSecondsAgo);

        if (isDuplicate) {
            log.info("중복된 차량 감지 제외: {}", request.getPlateNumber());
            return null; // 또는 기존 ID 반환
        }

        // 3. 차량 정보 관리
        Vehicle vehicle = vehicleService.getOrCreateVehicle(request.getPlateNumber());

        // 4. DetectionLog 생성 (엔티티의 새 필드들 반영)
        DetectionLog logEntity = DetectionLog.builder()
                .camera(camera)
                .vehicle(vehicle)
                .plateNumber(request.getPlateNumber())
                .detectionType(request.getDetectionType())
                .confidenceScore(BigDecimal.valueOf(request.getConfidenceScore()))
                .imagePath(request.getImagePath())
                .preprocessedPath(request.getPreprocessedPath()) // 엔티티와 일치시킴
                .status("PENDING") // 수집 직후 상태 설정
                .imageUrl(request.getImageUrl())
                .detectedAt(request.getDetectedAt())
                .build();

        DetectionLog savedLog = detectionLogRepository.save(logEntity);

        // 5. 흐름 이벤트 처리
        vehicleFlowEventService.processFlowEvent(savedLog, request.getSpeed(), request.getStayTime());
        savedLog.completeAnalysis(request.getPlateNumber(), BigDecimal.valueOf(request.getConfidenceScore()));

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
