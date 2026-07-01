package com.example.traffic.dto.request;

import jakarta.validation.constraints.Pattern;

public record DemoScriptRunRequest(
        @Pattern(regexp = "REAL|OPEN_DATA|SIMULATED|FAULT_INJECTED|MOCK", message = "지원하지 않는 데이터 소스입니다.")
        String dataSource
) {
}
