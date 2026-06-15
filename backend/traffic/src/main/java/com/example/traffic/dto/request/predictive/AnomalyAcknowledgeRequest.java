package com.example.traffic.dto.request.predictive;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class AnomalyAcknowledgeRequest {

    @NotBlank
    private String note;
}
