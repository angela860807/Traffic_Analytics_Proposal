package com.example.traffic.controller;

import com.example.traffic.domain.DetectionLog;
import com.example.traffic.service.DetectionLogService;
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

    // 1. 전체 탐지 로그 조회
    @GetMapping
    public List<DetectionLog> getAllLogs() {
        return detectionLogService.findAllLogs();
    }

    // 2. 특정 카메라별 로그 조회
    @GetMapping("/camera/{cameraId}")
    public List<DetectionLog> getLogsByCamera(@PathVariable Long cameraId) {
        return detectionLogService.findLogsByCamera(cameraId);
    }

    // 3. 로그 등록
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public DetectionLog createLog(@RequestBody DetectionLog log) {
        return detectionLogService.saveLog(log);
    }

    // 4. 특정 로그 삭제 (오탐 데이터 정리용)
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteLog(@PathVariable Long id) {
        detectionLogService.deleteLog(id);
        return ResponseEntity.noContent().build();
    }
}
