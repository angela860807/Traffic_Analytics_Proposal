package com.example.traffic.dto.response.predictive;

import com.example.traffic.common.enums.DetectionMethod;
import com.example.traffic.common.enums.DetectorOperatingMode;
import lombok.Builder;
import lombok.Getter;

import java.util.List;

@Getter
@Builder
public class DetectorHealthResponse {
    private final String status;
    private final List<Detector> detectors;

    @Getter
    @Builder
    public static class Detector {
        private final String name;
        private final String version;
        private final DetectionMethod method;
        private final DetectorOperatingMode operatingMode;
        private final String modelFormat;
        private final String featureSchemaVersion;
        private final boolean active;
    }
}
