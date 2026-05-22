package com.example.traffic.dto.request;

import com.example.traffic.common.enums.ViolationStatus;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class SpeedViolationStatusRequest {

    @NotNull
    private ViolationStatus violationStatus;

    private String reason;

    private String memo;

    private String reviewer;
}
