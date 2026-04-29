package com.example.traffic.controller;

import com.example.traffic.domain.Camera;
import com.example.traffic.service.CameraService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/cameras")
@RequiredArgsConstructor
public class CameraController {

    private final CameraService cameraService;

    @GetMapping
    public List<Camera> getAllCameras() {
        return cameraService.findAllCameras();
    }

    public List<Camera> getCamerasByZone(@PathVariable Long zoneId) {
        return cameraService.findCamerasByZone(zoneId);
    }
}
