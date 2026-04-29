package com.example.traffic.controller;

import com.example.traffic.domain.Camera;
import com.example.traffic.service.CameraService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/cameras")
@RequiredArgsConstructor
public class CameraController {

    private final CameraService cameraService;

    // 1. 전체 카메라 목록 조회
    @GetMapping
    public List<Camera> getAllCameras() {
        return cameraService.findAllCameras();
    }

    // 2. 특정 구역의 카메라 목록 조회
    @GetMapping("/zone/{zoneId}")
    public List<Camera> getCamerasByZone(@PathVariable Long zoneId) {
        return cameraService.findCamerasByZone(zoneId);
    }

    // 3. 새로운 카메라 등록 (Create)
    @PostMapping
    public Camera createCamera(@RequestBody Camera camera) {
        return cameraService.saveCamera(camera);
    }

    // 4. 카메라 정보 수정 (Update)
    @PutMapping("/{id}")
    public ResponseEntity<Camera> updateCamera(@PathVariable Long id, @RequestBody Camera cameraDetails) {
        Camera updatedCamera = cameraService.updateCamera(id, cameraDetails);
        return ResponseEntity.ok(updatedCamera);
    }

    // 5. 카메라 삭제 (Delete)
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCamera(@PathVariable Long id) {
        cameraService.deleteCamera(id);
        return ResponseEntity.noContent().build(); // 204 No Content 반환
    }
}