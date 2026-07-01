package com.example.traffic.dto.response;

import java.time.OffsetDateTime;
import java.util.List;

public record DemoScriptRunResponse(
        String scriptId,
        String label,
        String status,
        int exitCode,
        String dataSource,
        OffsetDateTime startedAt,
        OffsetDateTime finishedAt,
        List<String> outputLines,
        long durationSeconds
) {
}


