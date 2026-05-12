package com.example.traffic.dto.request;

import com.example.traffic.common.enums.DetectionType;
import com.example.traffic.common.enums.DetectionLogStatus;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Getter
@NoArgsConstructor
public class DetectionRequest {

    @NotBlank(message = "카메라 코드는 필수입니다.")
    private String cameraCode;
    @NotBlank(message = "이미지 경로는 필수입니다.")
    private String imagePath;
    private String imageUrl;
    @NotNull(message = "탐지 시각은 필수입니다.")
    private LocalDateTime detectedAt;

    // [Part 2: DetectionAnalysisResult용 - 분석 결과]
    private String plateNumber;
    private Double confidenceScore;
    private String plateCropImagePath;
    private String plateCropImageUrl;
    private String ocrImagePath;
    private String ocrImageUrl;
    private DetectionType detectionType;
    private DetectionLogStatus status;
}
