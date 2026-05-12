package com.example.traffic.service;

import com.example.traffic.common.enums.DetectionLogStatus;
import com.example.traffic.common.enums.DetectionType;
import com.example.traffic.domain.DetectionAnalysisResult;
import com.example.traffic.domain.DetectionLog;
import com.example.traffic.dto.request.DetectionRequest;
import com.example.traffic.repository.DetectionAnalysisResultRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class DetectionAnalysisResultService {

    private final DetectionAnalysisResultRepository detectionAnalysisResultRepository;

    @Transactional
    public DetectionAnalysisResult saveAnalysisResult(DetectionLog detectionLog,
                                                      DetectionRequest request,
                                                      DetectionLogStatus status) {
        DetectionAnalysisResult result = DetectionAnalysisResult.builder()
                .detectionLog(detectionLog)
                .attemptNo(1)
                .processorType("FASTAPI_OCR")
                .status(status)
                .plateNumber(request.getPlateNumber())
                .detectionType(resolveDetectionType(request))
                .confidenceScore(toBigDecimal(request.getConfidenceScore()))
                .plateCropImagePath(request.getPlateCropImagePath())
                .plateCropImageUrl(request.getPlateCropImageUrl())
                .ocrImagePath(request.getOcrImagePath())
                .ocrImageUrl(request.getOcrImageUrl())
                .processedAt(LocalDateTime.now())
                .build();

        return detectionAnalysisResultRepository.save(result);
    }

    public Optional<DetectionAnalysisResult> findLatestByLogId(Long logId) {
        return detectionAnalysisResultRepository.findFirstByDetectionLog_LogIdOrderByAttemptNoDesc(logId);
    }

    public List<DetectionAnalysisResult> findByPlateNumber(String plateNumber) {
        return detectionAnalysisResultRepository.findByPlateNumberOrderByCreatedAtDesc(plateNumber);
    }

    private DetectionType resolveDetectionType(DetectionRequest request) {
        return request.getDetectionType() != null ? request.getDetectionType() : DetectionType.VEHICLE;
    }

    private BigDecimal toBigDecimal(Double value) {
        return value != null ? BigDecimal.valueOf(value) : null;
    }
}
