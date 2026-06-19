package com.example.traffic.dto.request.predictive;

import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.common.enums.HealthStatus;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class CameraOperatingSearchRequest {
    private Long zoneId;
    private HealthStatus healthStatus;
    private DataSourceType dataSource = DataSourceType.REAL;
    @Min(0)
    private int page = 0;
    @Min(1)
    @Max(100)
    private int size = 20;
    private String sort = "healthScore,asc";
}
