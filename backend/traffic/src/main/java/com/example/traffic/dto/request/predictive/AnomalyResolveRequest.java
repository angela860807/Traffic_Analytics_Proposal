package com.example.traffic.dto.request.predictive;

import com.example.traffic.common.enums.SuspectedCause;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class AnomalyResolveRequest {

    @NotNull
    private SuspectedCause confirmedCause;

    @NotBlank
    private String resolutionNote;
}
