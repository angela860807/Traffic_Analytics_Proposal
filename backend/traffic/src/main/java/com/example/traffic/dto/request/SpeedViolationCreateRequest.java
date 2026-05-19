package com.example.traffic.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Getter
@NoArgsConstructor
public class SpeedViolationCreateRequest {

    @NotNull
    private Long flowEventId;

    @NotBlank
    private String plateNumber;

    @NotBlank
    private String cameraCode;

    @NotNull
    @Positive
    private Double measuredSpeed;

    @NotNull
    @Positive
    private Double speedLimit;

    private String violationImagePath;

    private String violationImageUrl;

    @NotNull
    private LocalDateTime violatedAt;
}
