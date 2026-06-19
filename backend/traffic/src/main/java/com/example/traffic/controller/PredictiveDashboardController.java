package com.example.traffic.controller;

import com.example.traffic.common.enums.DataSourceType;
import com.example.traffic.common.enums.HealthStatus;
import com.example.traffic.dto.response.predictive.*;
import com.example.traffic.service.PredictiveDashboardQueryService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.OffsetDateTime;
import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/predictive")
public class PredictiveDashboardController {

    private final PredictiveDashboardQueryService predictiveDashboardQueryService;

    @GetMapping("/summary")
    public PredictiveSummaryResponse getSummary(
            @RequestParam(defaultValue = "REAL") DataSourceType dataSource) {
        return predictiveDashboardQueryService.getSummary(dataSource);
    }

    @GetMapping("/cameras")
    public PageResponse<CameraOperatingStatusResponse> getCameras(
            @RequestParam(required = false) Long zoneId,
            @RequestParam(required = false) HealthStatus healthStatus,
            @RequestParam(defaultValue = "REAL") DataSourceType dataSource,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "healthScore,asc") String sort) {
        return predictiveDashboardQueryService.getCameraStatuses(
                zoneId,
                healthStatus,
                dataSource,
                page,
                size,
                sort
        );
    }

    @GetMapping("/cameras/{cameraId}/health-history")
    public CameraHealthHistoryResponse getCameraHealthHistory(
            @PathVariable Long cameraId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) OffsetDateTime from,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) OffsetDateTime to,
            @RequestParam(defaultValue = "REAL") DataSourceType dataSource) {
        return predictiveDashboardQueryService.getCameraHealthHistory(
                cameraId,
                from,
                to,
                dataSource
        );
    }

    @GetMapping("/traffic-context")
    public TrafficContextHistoryResponse getTrafficContextHistory(
            @RequestParam Long cameraId,
            @RequestParam Long zoneId,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) OffsetDateTime from,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) OffsetDateTime to,
            @RequestParam(defaultValue = "REAL") DataSourceType dataSource) {
        return predictiveDashboardQueryService.getTrafficContextHistory(
                cameraId,
                zoneId,
                from,
                to,
                dataSource
        );
    }

    @GetMapping("/policies")
    public List<AnomalyPolicyResponse> getPolicies(
            @RequestParam(required = false) Boolean enabled) {
        return predictiveDashboardQueryService.getPolicies(enabled);
    }
}
