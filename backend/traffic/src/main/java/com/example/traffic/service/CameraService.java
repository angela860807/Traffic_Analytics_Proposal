package com.example.traffic.service;

import com.example.traffic.domain.Camera;
import com.example.traffic.repository.CameraRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class CameraService {

    private final CameraRepository cameraRepository;

    public List<Camera> findAllCameras() {
        return cameraRepository.findAll();
    }

    public List<Camera> findCamerasByZone(Long zoneId) {
        return cameraRepository.findByZoneZoneId(zoneId);
    }
}
