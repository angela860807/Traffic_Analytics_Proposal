package com.example.traffic.controller;

import com.example.traffic.common.enums.ViolationStatus;
import com.example.traffic.dto.request.SpeedViolationCreateRequest;
import com.example.traffic.dto.request.SpeedViolationStatusRequest;
import com.example.traffic.dto.response.CommonResponse;
import com.example.traffic.dto.response.SpeedViolationResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.service.SpeedViolationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/speed-violations")
@RequiredArgsConstructor
public class SpeedViolationController {

    private final SpeedViolationService speedViolationService;

    @Value("${app.api.internal-key}")
    private String internalApiKey;

    @PostMapping
    public ResponseEntity<CommonResponse<SpeedViolationResponse>> createViolation(
            @RequestHeader(value = "X-Internal-Api-Key", required = false) String apiKey,
            @Valid @RequestBody SpeedViolationCreateRequest request) {
        validateInternalApiKey(apiKey);

        SpeedViolationResponse response = speedViolationService.createViolation(request);
        return ResponseEntity.ok(CommonResponse.success(response, "Speed violation record saved."));
    }

    @GetMapping("/vehicle/{vehicleId}")
    public ResponseEntity<CommonResponse<List<SpeedViolationResponse>>> getVehicleViolations(
            @PathVariable Long vehicleId) {
        List<SpeedViolationResponse> violations = speedViolationService.getVehicleViolations(vehicleId);
        return ResponseEntity.ok(CommonResponse.success(violations, "속도위반 차량 이력 조회 성공"));
    }

    @GetMapping("/camera/{cameraId}")
    public ResponseEntity<CommonResponse<List<SpeedViolationResponse>>> getCameraViolations(
            @PathVariable Long cameraId) {
        List<SpeedViolationResponse> violations = speedViolationService.getCameraViolations(cameraId);
        return ResponseEntity.ok(CommonResponse.success(violations, "카메라별 속도위반 이력 조회 성공"));
    }

    @GetMapping("/status/{violationStatus}")
    public ResponseEntity<CommonResponse<List<SpeedViolationResponse>>> getStatusViolations(
            @PathVariable ViolationStatus violationStatus) {
        List<SpeedViolationResponse> violations = speedViolationService.getStatusViolations(violationStatus);
        return ResponseEntity.ok(CommonResponse.success(violations, "상태별 속도위반 이력 조회 성공"));
    }

    @PatchMapping("/{violationId}/status")
    public ResponseEntity<CommonResponse<SpeedViolationResponse>> updateViolationStatus(
            @PathVariable Long violationId,
            @Valid @RequestBody SpeedViolationStatusRequest request) {
        SpeedViolationResponse response = speedViolationService.updateViolationStatus(violationId, request);
        return ResponseEntity.ok(CommonResponse.success(response, "Speed violation status updated."));
    }

    @GetMapping
    public ResponseEntity<CommonResponse<List<SpeedViolationResponse>>> getViolationsBetween(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {
        List<SpeedViolationResponse> violations = speedViolationService.getViolationsBetween(start, end);
        return ResponseEntity.ok(CommonResponse.success(violations, "기간별 속도위반 이력 조회 성공"));
    }

    @GetMapping("/stats/count")
    public ResponseEntity<Long> countViolationsBetween(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {
        long count = speedViolationService.countViolationsBetween(start, end);
        return ResponseEntity.ok(count);
    }

    private void validateInternalApiKey(String apiKey) {
        if (apiKey == null) {
            throw new BusinessException("API Key is missing.", HttpStatus.UNAUTHORIZED);
        }
        if (!internalApiKey.equals(apiKey)) {
            throw new BusinessException("Invalid API Key.", HttpStatus.FORBIDDEN);
        }
    }
}
