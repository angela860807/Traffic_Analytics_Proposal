package com.example.traffic.service;

import com.example.traffic.common.enums.DetectionLogStatus;
import com.example.traffic.domain.Camera;
import com.example.traffic.domain.DetectionAnalysisResult;
import com.example.traffic.domain.DetectionLog;
import com.example.traffic.domain.Vehicle;
import com.example.traffic.dto.request.DetectionRequest;
import com.example.traffic.dto.response.DetectionResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.repository.DetectionLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
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
    private final DetectionAnalysisResultService detectionAnalysisResultService;
    private final VehicleFlowEventService vehicleFlowEventService;

    @Transactional
    public DetectionResponse processDetection(DetectionRequest request) {
        validateDetectionRequest(request);
        return saveDetectionData(request);
    }

    @Transactional
    public DetectionResponse saveDetectionData(DetectionRequest request) {
        Camera camera = cameraRepository.findByCameraCode(request.getCameraCode())
                .orElseThrow(() -> new BusinessException("Unknown camera code: " + request.getCameraCode(), HttpStatus.NOT_FOUND));

        DetectionLog savedLog = detectionLogRepository.save(DetectionLog.builder()
                .camera(camera)
                .imagePath(request.getImagePath())
                .imageUrl(request.getImageUrl())
                .detectedAt(request.getDetectedAt())
                .build());

        DetectionLogStatus resultStatus = resolveResultStatus(request, savedLog);
        DetectionAnalysisResult analysisResult =
                detectionAnalysisResultService.saveAnalysisResult(savedLog, request, resultStatus);

        if (resultStatus == DetectionLogStatus.FLOW_EVENT_CREATED) {
            Vehicle vehicle = vehicleService.getOrCreateVehicle(request.getPlateNumber());
            vehicleFlowEventService.processFlowEvent(savedLog, analysisResult, vehicle);
        }

        return DetectionResponse.of(savedLog, analysisResult);
    }

    private void validateDetectionRequest(DetectionRequest request) {
        if (request.getCameraCode() == null || request.getCameraCode().isBlank() ||
                request.getImagePath() == null || request.getImagePath().isBlank() ||
                request.getDetectedAt() == null) {
            throw new BusinessException("Required detection payload value is missing.", HttpStatus.BAD_REQUEST);
        }

        if (request.getConfidenceScore() != null &&
                (request.getConfidenceScore() < 0.0 || request.getConfidenceScore() > 1.0)) {
            throw new BusinessException("Confidence score must be between 0.0 and 1.0.", HttpStatus.BAD_REQUEST);
        }

        if (request.getStatus() != DetectionLogStatus.OCR_FAILED && !hasPlateNumber(request)) {
            throw new BusinessException("Detection without a plate number must be saved as OCR_FAILED.", HttpStatus.BAD_REQUEST);
        }
    }

    private DetectionLogStatus resolveResultStatus(DetectionRequest request, DetectionLog savedLog) {
        if (request.getStatus() == DetectionLogStatus.OCR_FAILED) {
            return DetectionLogStatus.OCR_FAILED;
        }
        if (request.getStatus() == DetectionLogStatus.DUPLICATE_SKIPPED) {
            return DetectionLogStatus.DUPLICATE_SKIPPED;
        }

        Vehicle vehicle = vehicleService.getOrCreateVehicle(request.getPlateNumber());
        return vehicleFlowEventService.hasRecentDuplicate(vehicle, savedLog)
                ? DetectionLogStatus.DUPLICATE_SKIPPED
                : DetectionLogStatus.FLOW_EVENT_CREATED;
    }

    private boolean hasPlateNumber(DetectionRequest request) {
        return request.getPlateNumber() != null && !request.getPlateNumber().isBlank();
    }

    public List<DetectionResponse> getRecentLogs() {
        return detectionLogRepository.findTop100ByOrderByDetectedAtDesc().stream()
                .map(log -> DetectionResponse.of(log, detectionAnalysisResultService.findLatestByLogId(log.getLogId()).orElse(null)))
                .toList();
    }

    public List<DetectionResponse> getFilteredLogs(String plateNumber, Long zoneId) {
        if (plateNumber != null && !plateNumber.isBlank()) {
            return detectionAnalysisResultService.findByPlateNumber(plateNumber).stream()
                    .map(result -> DetectionResponse.of(result.getDetectionLog(), result))
                    .toList();
        }

        if (zoneId != null) {
            return detectionLogRepository.findByCamera_Zone_ZoneIdOrderByDetectedAtDesc(zoneId).stream()
                    .map(log -> DetectionResponse.of(log, detectionAnalysisResultService.findLatestByLogId(log.getLogId()).orElse(null)))
                    .toList();
        }

        return getRecentLogs();
    }
}
