package com.example.traffic.controller;

import com.example.traffic.dto.request.DetectionRequest;
import com.example.traffic.dto.response.CommonResponse;
import com.example.traffic.dto.response.DetectionResponse;
import com.example.traffic.service.DetectionLogService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "Detection Log API", description = "AI 탐지 로그 관리 및 조회")
@RestController
@RequestMapping("/api/v1/detection-logs")
@RequiredArgsConstructor
public class DetectionLogController {

    private final DetectionLogService detectionLogService;

    @Operation(summary = "AI 탐지 데이터 처리", description = "AI 서버로부터 받은 데이터를 검증하고 저장합니다.")
    @PostMapping
    public CommonResponse<Long> processDetection(@RequestBody DetectionRequest request) {
        Long logId = detectionLogService.processDetection(request);
        return CommonResponse.success(logId, "탐지 데이터가 성공적으로 처리되었습니다.");
    }

    @Operation(summary = "최신 탐지 로그 조회", description = "최근 발생한 탐지 로그 100건을 조회합니다.")
    @GetMapping
    public CommonResponse<List<DetectionResponse>> getRecentLogs() {
        List<DetectionResponse> logs = detectionLogService.getRecentLogs();
        return CommonResponse.success(logs);
    }

    @Operation(summary = "탐지 로그 필터링 검색", description = "차량번호 또는 구역 ID로 로그를 검색합니다.")
    @GetMapping("/search")
    public CommonResponse<List<DetectionResponse>> getFilteredLogs(
            @RequestParam(required = false) String plateNumber,
            @RequestParam(required = false) Long zoneId) {
        List<DetectionResponse> logs = detectionLogService.getFilteredLogs(plateNumber, zoneId);
        return CommonResponse.success(logs);
    }
}