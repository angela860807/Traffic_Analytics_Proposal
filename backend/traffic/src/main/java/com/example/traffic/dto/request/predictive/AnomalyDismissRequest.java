package com.example.traffic.dto.request.predictive;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class AnomalyDismissRequest {

    @NotBlank
    private String reason;
}
