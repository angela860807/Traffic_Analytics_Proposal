package com.example.traffic.service;

import com.example.traffic.common.enums.*;
import com.example.traffic.domain.*;
import com.example.traffic.dto.response.predictive.DetectionEvaluationResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.*;
import com.example.traffic.util.PredictiveTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.format.DateTimeFormatter;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class PredictiveAnomalyEventIngestionService {

    private static final List<AnomalyEventStatus> ACTIVE_STATUSES = List.of(
            AnomalyEventStatus.OPEN,
            AnomalyEventStatus.ACKNOWLEDGED,
            AnomalyEventStatus.RECOVERED
    );

    private final PredictiveAnomalyCandidateGuardService candidateGuardService;
    private final AnomalyEventRepository anomalyEventRepository;
    private final AnomalyEventEvidenceRepository evidenceRepository;
    private final AnomalyPolicyRepository anomalyPolicyRepository;
    private final DetectorVersionRepository detectorVersionRepository;
    private final CameraRepository cameraRepository;
    private final MaintenanceTicketRepository maintenanceTicketRepository;
    private final JdbcTemplate jdbcTemplate;

    @Transactional
    public int saveActiveCandidates(
            DetectionEvaluationResponse response,
            DataSourceType dataSource
    ) {
        List<DetectionEvaluationResponse.Candidate> candidates =
                candidateGuardService.getActiveCandidatesForEventProcessing(response);
        if (candidates.isEmpty()) {
            return 0;
        }

        DetectorVersion detectorVersion = findDetectorVersion(response.getDetector());
        int savedCount = 0;
        for (DetectionEvaluationResponse.Candidate candidate : candidates) {
            AnomalyEvent event = saveOrRefreshEvent(
                    candidate,
                    detectorVersion,
                    dataSource,
                    PredictiveTimeUtils.toLocalDateTime(response.getEvaluatedAt())
            );
            saveEvidence(event, candidate.getEvidence());
            createCriticalMaintenanceTicketIfNeeded(event, candidate, PredictiveTimeUtils.toLocalDateTime(response.getEvaluatedAt()));
            savedCount++;
        }
        return savedCount;
    }

    private AnomalyEvent saveOrRefreshEvent(
            DetectionEvaluationResponse.Candidate candidate,
            DetectorVersion detectorVersion,
            DataSourceType dataSource,
            LocalDateTime detectedAt
    ) {
        Camera camera = cameraRepository.findById(candidate.getCameraId())
                .orElseThrow(() -> new BusinessException(
                        "Camera not found: " + candidate.getCameraId(),
                        HttpStatus.NOT_FOUND
                ));
        AnomalyPolicy policy = anomalyPolicyRepository.findByPolicyCode(candidate.getPolicyCode())
                .or(() -> fallbackPolicyCode(candidate.getPolicyCode())
                        .flatMap(anomalyPolicyRepository::findByPolicyCode))
                .orElseThrow(() -> new BusinessException(
                        "Anomaly policy not found: " + candidate.getPolicyCode(),
                        HttpStatus.NOT_FOUND
                ));

        return anomalyEventRepository
                .findFirstByTargetCamera_CameraIdAndAnomalyTypeAndStatusInOrderByLastDetectedAtDesc(
                        candidate.getCameraId(),
                        candidate.getAnomalyType(),
                        ACTIVE_STATUSES
                )
                .map(existing -> {
                    existing.refreshDetection(
                            candidate.getSeverity(),
                            candidate.getAnomalyScore(),
                            detectedAt,
                            candidate.getTrend() != null ? candidate.getTrend().getSlope() : null,
                            candidate.getTrend() != null ? candidate.getTrend().getConfidence() : null,
                            candidate.getTrend() != null ? candidate.getTrend().getPredictionHorizonMinutes() : null,
                            candidate.getTrend() != null
                                    ? PredictiveTimeUtils.toLocalDateTime(candidate.getTrend().getProjectedThresholdCrossingAt())
                                    : null,
                            toSuspectedCauseJson(candidate.getSuspectedCauses())
                    );
                    return existing;
                })
                .orElseGet(() -> anomalyEventRepository.save(AnomalyEvent.builder()
                        .targetType(AnomalyTargetType.CAMERA)
                        .targetCamera(camera)
                        .anomalyType(candidate.getAnomalyType())
                        .severity(candidate.getSeverity())
                        .status(AnomalyEventStatus.OPEN)
                        .detectionMethod(detectorVersion.getDetectionMethod())
                        .dataSource(dataSource)
                        .policy(policy)
                        .detectorVersion(detectorVersion)
                        .anomalyScore(candidate.getAnomalyScore())
                        .trendSlope(candidate.getTrend() != null ? candidate.getTrend().getSlope() : null)
                        .trendConfidence(candidate.getTrend() != null ? candidate.getTrend().getConfidence() : null)
                        .predictionHorizonMinutes(candidate.getTrend() != null
                                ? candidate.getTrend().getPredictionHorizonMinutes() : null)
                        .projectedThresholdCrossingAt(candidate.getTrend() != null
                                ? PredictiveTimeUtils.toLocalDateTime(candidate.getTrend().getProjectedThresholdCrossingAt())
                                : null)
                        .suspectedCausesJson(toSuspectedCauseJson(candidate.getSuspectedCauses()))
                        .firstDetectedAt(detectedAt)
                        .lastDetectedAt(detectedAt)
                        .build()));
    }

    private void saveEvidence(
            AnomalyEvent event,
            List<DetectionEvaluationResponse.Evidence> evidenceItems
    ) {
        if (evidenceItems == null || evidenceItems.isEmpty()) {
            return;
        }
        for (DetectionEvaluationResponse.Evidence evidence : evidenceItems) {
            evidenceRepository.save(AnomalyEventEvidence.builder()
                    .anomalyEvent(event)
                    .metricName(evidence.getMetricName())
                    .observedValue(evidence.getObservedValue())
                    .baselineValue(evidence.getBaselineValue())
                    .thresholdValue(evidence.getThresholdValue())
                    .metricScore(evidence.getMetricScore())
                    .unit(evidence.getUnit())
                    .sampledAt(PredictiveTimeUtils.toLocalDateTime(evidence.getSampledAt()))
                    .contextJson(evidence.getContext() != null ? evidence.getContext() : Map.of())
                    .build());
        }
    }

    private DetectorVersion findDetectorVersion(DetectionEvaluationResponse.Detector detector) {
        if (detector == null || detector.getName() == null || detector.getVersion() == null) {
            throw new BusinessException("Detector information is missing.", HttpStatus.BAD_REQUEST);
        }
        return detectorVersionRepository.findByDetectorNameAndVersion(detector.getName(), detector.getVersion())
                .orElseThrow(() -> new BusinessException(
                        "Detector version not found: " + detector.getName() + " " + detector.getVersion(),
                        HttpStatus.NOT_FOUND
                ));
    }

    private List<Object> toSuspectedCauseJson(List<SuspectedCause> suspectedCauses) {
        if (suspectedCauses == null) {
            return List.of();
        }
        return suspectedCauses.stream()
                .map(Enum::name)
                .map(value -> (Object) value)
                .toList();
    }

    private java.util.Optional<String> fallbackPolicyCode(String policyCode) {
        if (policyCode != null && policyCode.endsWith("_ROBUST_ZSCORE_V1")) {
            return java.util.Optional.of("CAMERA_ROBUST_ZSCORE_V1");
        }
        return java.util.Optional.empty();
    }

    private void createCriticalMaintenanceTicketIfNeeded(
            AnomalyEvent event,
            DetectionEvaluationResponse.Candidate candidate,
            LocalDateTime detectedAt
    ) {
        if (candidate.getSeverity() != AnomalySeverity.CRITICAL) {
            return;
        }
        if (maintenanceTicketRepository.findByAnomalyEvent_Id(event.getId()).isPresent()) {
            return;
        }

        maintenanceTicketRepository.save(MaintenanceTicket.builder()
                .anomalyEvent(event)
                .ticketNumber(nextTicketNumber(detectedAt))
                .priority(MaintenancePriority.P1)
                .status(MaintenanceStatus.OPEN)
                .dueAckAt(detectedAt.plusMinutes(15))
                .dueStartAt(detectedAt.plusHours(1))
                .actionNote("Auto-created from predictive anomaly event: " + candidate.getAnomalyType())
                .build());
    }

    private String nextTicketNumber(LocalDateTime detectedAt) {
        Long sequence = jdbcTemplate.queryForObject(
                "SELECT nextval('maintenance_ticket_number_seq')",
                Long.class
        );
        return "MNT-%s-%04d".formatted(
                detectedAt.format(DateTimeFormatter.BASIC_ISO_DATE),
                sequence != null ? sequence : 0L
        );
    }
}
