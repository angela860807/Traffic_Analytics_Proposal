package com.example.traffic.dto.response;

import com.example.traffic.common.enums.ViolationStatus;
import com.example.traffic.domain.DetectionAnalysisResult;
import com.example.traffic.domain.SpeedViolation;
import com.example.traffic.domain.SpeedViolationReview;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class SpeedViolationResponse {

    private final Long violationId;
    private final Long flowEventId;
    private final Long vehicleId;
    private final Long cameraId;
    private final String cameraName;
    private final String plateNumber;
    private final Double measuredSpeed;
    private final Double speedLimit;
    private final String violationImagePath;
    private final Double confidenceScore;
    private final String plateCropImagePath;
    private final String plateCropImageUrl;
    private final ViolationStatus violationStatus;
    private final Boolean reviewedManually;
    private final ViolationStatus latestReviewStatus;
    private final String latestReviewReason;
    private final String latestReviewMemo;
    private final String latestReviewedBy;
    private final LocalDateTime latestReviewedAt;
    private final LocalDateTime violatedAt;
    private final LocalDateTime createdAt;

    public static SpeedViolationResponse from(SpeedViolation violation) {
        return from(violation, null);
    }

    public static SpeedViolationResponse from(SpeedViolation violation, SpeedViolationReview latestReview) {
        DetectionAnalysisResult analysisResult = violation.getFlowEvent().getSourceAnalysisResult();
        return SpeedViolationResponse.builder()
                .violationId(violation.getViolationId())
                .flowEventId(violation.getFlowEvent().getFlowEventId())
                .vehicleId(violation.getVehicle().getVehicleId())
                .cameraId(violation.getCamera().getCameraId())
                .cameraName(violation.getCamera().getCameraName())
                .plateNumber(violation.getPlateNumber())
                .measuredSpeed(violation.getMeasuredSpeed().doubleValue())
                .speedLimit(violation.getSpeedLimit().doubleValue())
                .violationImagePath(violation.getViolationImagePath())
                .confidenceScore(analysisResult != null && analysisResult.getConfidenceScore() != null
                        ? analysisResult.getConfidenceScore().doubleValue()
                        : null)
                .plateCropImagePath(analysisResult != null ? analysisResult.getPlateCropImagePath() : null)
                .plateCropImageUrl(analysisResult != null ? analysisResult.getPlateCropImageUrl() : null)
                .violationStatus(violation.getViolationStatus())
                .reviewedManually(latestReview != null)
                .latestReviewStatus(latestReview != null ? latestReview.getToStatus() : null)
                .latestReviewReason(latestReview != null ? latestReview.getReason() : null)
                .latestReviewMemo(latestReview != null ? latestReview.getMemo() : null)
                .latestReviewedBy(latestReview != null ? latestReview.getReviewedBy() : null)
                .latestReviewedAt(latestReview != null ? latestReview.getReviewedAt() : null)
                .violatedAt(violation.getViolatedAt())
                .createdAt(violation.getCreatedAt())
                .build();
    }
}
