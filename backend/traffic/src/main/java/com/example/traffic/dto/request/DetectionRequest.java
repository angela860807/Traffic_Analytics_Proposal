package com.example.traffic.dto.request;

import com.example.traffic.common.enums.DetectionType;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
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

    @NotBlank(message = "인식된 번호판은 필수입니다.")
    private String plateNumber;

    @NotNull(message = "신뢰도 점수는 필수입니다.")
    @DecimalMin(value = "0.0", message = "신뢰도는 0.0 이상이어야 합니다.")
    @DecimalMax(value = "1.0", message = "신뢰도는 1.0 이하여야 합니다.")
    private Double confidenceScore;

    @NotBlank(message = "이미지 경로는 필수입니다.")
    private String imagePath; // 저장/추적용 물리 경로

    private String imageUrl; // Vue 화면 표시용 URL 추가

    @NotNull(message = "탐지 시각은 필수입니다.")
    private LocalDateTime detectedAt;

    @NotNull(message = "탐지 유형은 필수입니다.")
    private DetectionType detectionType;
}