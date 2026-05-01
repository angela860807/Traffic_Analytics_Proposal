package com.example.traffic.controller;

import com.example.traffic.dto.request.DetectionRequest;
import com.example.traffic.dto.response.DetectionResponse;
import com.example.traffic.service.DetectionLogService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/logs")
@RequiredArgsConstructor
public class DetectionLogController {

    private final DetectionLogService detectionLogService;

    @GetMapping
    public ResponseEntity<List<DetectionResponse>> getLogs(
            @RequestParam(required = false) String plateNumber,
            @RequestParam(required = false) Long zoneId) {
        // Service에 해당 필터 로직을 추가하여 호출
        return ResponseEntity.ok(detectionLogService.getFilteredLogs(plateNumber, zoneId));
    }

    /**
     * [AI 탐지 결과 수신] NPU/AI 서버로부터 데이터를 받는 엔드포인트
     */
    @PostMapping
    public ResponseEntity<Long> receiveDetection(@RequestBody @Valid DetectionRequest request) {
        Long logId = detectionLogService.processDetection(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(logId);
    }

    /**
     * [최신 탐지 현황 조회] 실시간 모니터링용
     */
    @GetMapping("/recent")
    public ResponseEntity<List<DetectionResponse>> getRecentLogs() {
        return ResponseEntity.ok(detectionLogService.getRecentLogs());
    }
}
