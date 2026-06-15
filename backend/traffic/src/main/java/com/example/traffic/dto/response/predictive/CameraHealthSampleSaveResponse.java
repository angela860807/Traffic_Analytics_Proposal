package com.example.traffic.dto.response.predictive;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class CameraHealthSampleSaveResponse {
    private final Long sampleId;
    private final boolean created;
}
