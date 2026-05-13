package com.example.traffic.controller;

import com.example.traffic.dto.request.CameraSaveRequest;
import com.example.traffic.dto.request.CameraUpdateRequest;
import com.example.traffic.dto.response.CameraResponse;
import com.example.traffic.service.CameraService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/cameras")
@RequiredArgsConstructor
public class CameraController {

    private final CameraService cameraService;

    /**
     * [카메라 등록]
     * POST /api/cameras
     */
    @PostMapping
    public ResponseEntity<CameraResponse> createCamera(@RequestBody @Valid CameraSaveRequest request) {
        // 서비스에서 CameraResponse를 반환하도록 수정된 로직 반영
        CameraResponse response = cameraService.saveCamera(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * [카메라 상세 조회]
     * GET /api/cameras/{cameraId}
     */
    @GetMapping("/{cameraId}")
    public ResponseEntity<CameraResponse> getCamera(@PathVariable Long cameraId) {
        CameraResponse response = cameraService.getCamera(cameraId);
        return ResponseEntity.ok(response);
    }

    /**
     * [특정 구역의 카메라 목록 조회]
     * GET /api/cameras?zoneId=1
     */
    @GetMapping
    public ResponseEntity<List<CameraResponse>> getCamerasByZone(@RequestParam Long zoneId) {
        List<CameraResponse> responses = cameraService.findByZone(zoneId);
        return ResponseEntity.ok(responses);
    }

    /**
     * [카메라 정보 수정]
     * PUT /api/cameras/{cameraId}
     */
    @PutMapping("/{cameraId}")
    public ResponseEntity<Void> updateCamera(
            @PathVariable Long cameraId,
            @RequestBody @Valid CameraUpdateRequest request) {
        cameraService.updateCamera(cameraId, request);
        return ResponseEntity.ok().build();
    }
}