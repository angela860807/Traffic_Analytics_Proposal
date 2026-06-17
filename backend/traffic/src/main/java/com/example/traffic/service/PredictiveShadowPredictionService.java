package com.example.traffic.service;

import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.common.enums.DetectorOperatingMode;
import com.example.traffic.domain.Camera;
import com.example.traffic.domain.DetectorVersion;
import com.example.traffic.domain.ModelPredictionLog;
import com.example.traffic.dto.response.predictive.DetectionEvaluationResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.repository.DetectorVersionRepository;
import com.example.traffic.repository.ModelPredictionLogRepository;
import com.example.traffic.util.PredictiveTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class PredictiveShadowPredictionService {

    private final ModelPredictionLogRepository modelPredictionLogRepository;
    private final DetectorVersionRepository detectorVersionRepository;
    private final CameraRepository cameraRepository;

    @Transactional
    public int saveShadowCandidates(DetectionEvaluationResponse response, DataSourceType dataSource) {
        if (response == null || response.getShadowCandidates() == null || response.getShadowCandidates().isEmpty()) {
            return 0;
        }

        DetectorVersion detectorVersion = findDetectorVersion(response.getDetector());
        LocalDateTime evaluatedAt = PredictiveTimeUtils.toLocalDateTime(response.getEvaluatedAt());
        int savedCount = 0;

        for (DetectionEvaluationResponse.ShadowCandidate candidate : response.getShadowCandidates()) {
            if (candidate == null || candidate.getCameraId() == null) {
                continue;
            }
            if (DetectorOperatingMode.ACTIVE.equals(candidate.getOperatingMode())) {
                throw new BusinessException("ACTIVE detector result must not be handled as shadow candidate.", HttpStatus.CONFLICT);
            }
            if (modelPredictionLogRepository.existsByCamera_CameraIdAndDetectorVersion_IdAndEvaluatedAt(
                    candidate.getCameraId(), detectorVersion.getId(), evaluatedAt)) {
                continue;
            }

            Camera camera = cameraRepository.findById(candidate.getCameraId())
                    .orElseThrow(() -> new BusinessException("Camera not found: " + candidate.getCameraId(), HttpStatus.NOT_FOUND));

            ModelPredictionLog log = ModelPredictionLog.builder()
                    .camera(camera)
                    .detectorVersion(detectorVersion)
                    .evaluatedAt(evaluatedAt)
                    .inputWindowFrom(PredictiveTimeUtils.toLocalDateTime(candidate.getInputWindowFrom()))
                    .inputWindowTo(PredictiveTimeUtils.toLocalDateTime(candidate.getInputWindowTo()))
                    .anomalyScore(candidate.getAnomalyScore())
                    .warningThreshold(candidate.getWarningThreshold())
                    .criticalThreshold(candidate.getCriticalThreshold())
                    .predictedAnomaly(candidate.isPredictedAnomaly())
                    .predictedSeverity(candidate.getPredictedSeverity())
                    .featureSchemaVersion(candidate.getFeatureSchemaVersion())
                    .topFeaturesJson(toTopFeaturesJson(candidate.getTopFeatures()))
                    .dataSource(dataSource)
                    .build();

            modelPredictionLogRepository.save(log);
            savedCount++;
        }

        return savedCount;
    }

    private DetectorVersion findDetectorVersion(DetectionEvaluationResponse.Detector detector) {
        if (detector == null || detector.getName() == null || detector.getVersion() == null) {
            throw new BusinessException("Detector information is missing.", HttpStatus.BAD_REQUEST);
        }
        return detectorVersionRepository.findByDetectorNameAndVersion(detector.getName(), detector.getVersion())
                .orElseThrow(() -> new BusinessException(
                        "Detector version not found: " + detector.getName() + " " + detector.getVersion(),
                        HttpStatus.NOT_FOUND));
    }

    private List<Object> toTopFeaturesJson(List<DetectionEvaluationResponse.TopFeature> topFeatures) {
        if (topFeatures == null) {
            return List.of();
        }
        return topFeatures.stream()
                .map(feature -> {
                    Map<String, Object> value = new LinkedHashMap<>();
                    value.put("featureName", feature.getFeatureName());
                    value.put("featureValue", feature.getFeatureValue());
                    return (Object) value;
                })
                .toList();
    }
}
