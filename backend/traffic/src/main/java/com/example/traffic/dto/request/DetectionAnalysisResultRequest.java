package com.example.traffic.dto.request;

import com.example.traffic.common.enums.DetectionLogStatus;
import com.example.traffic.common.enums.DetectionType;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class DetectionAnalysisResultRequest {
    private String plateNumber;
    private Double confidenceScore;
    private DetectionType detectionType;
    private DetectionLogStatus status;
    private String plateCropImagePath;
    private String plateCropImageUrl;
    private String ocrImagePath;
    private String ocrImageUrl;
}