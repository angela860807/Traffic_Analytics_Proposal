package com.example.traffic.controller;

import com.example.traffic.common.enums.ViolationStatus;
import com.example.traffic.dto.response.CommonResponse;
import com.example.traffic.dto.response.SpeedViolationResponse;
import com.example.traffic.service.SpeedViolationService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/speed-violations")
@RequiredArgsConstructor
public class SpeedViolationController {

    private final SpeedViolationService speedViolationService;

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
}
