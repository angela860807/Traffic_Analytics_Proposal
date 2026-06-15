package com.example.traffic.dto.request.predictive;

import com.example.traffic.common.enums.DataSourceType;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.OffsetDateTime;

@Getter
@NoArgsConstructor
public class TrafficContextSearchRequest {
    @NotNull
    private Long cameraId;
    @NotNull
    private Long zoneId;
    @NotNull
    private OffsetDateTime from;
    @NotNull
    private OffsetDateTime to;
    private DataSourceType dataSource = DataSourceType.REAL;
}
