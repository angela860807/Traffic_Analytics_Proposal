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

    // 1. 전체 조회
    public List<Camera> findAllCameras() {
        return cameraRepository.findAll();
    }

    // 2. 구역별 조회
    public List<Camera> findCamerasByZone(Long zoneId) {
        return cameraRepository.findByZoneZoneId(zoneId);
    }

    // 3. 카메라 등록 (Create)
    @Transactional
    public Camera saveCamera(Camera camera) {
        return cameraRepository.save(camera);
    }

    // 4. 카메라 수정 (Update)
    @Transactional
    public Camera updateCamera(Long id, Camera cameraDetails) {
        Camera camera = cameraRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("해당 카메라가 없습니다. id=" + id));

        // 데이터 업데이트 (Dirty Checking 활용)
        camera.update(cameraDetails.getCameraName(),
                cameraDetails.getCameraCode(),
                cameraDetails.getStreamUrl(),
                cameraDetails.getDirectionType(),
                cameraDetails.isActive());

        return camera;
    }

    // 5. 카메라 삭제 (Delete)
    @Transactional
    public void deleteCamera(Long id) {
        Camera camera = cameraRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("해당 카메라가 없습니다. id=" + id));
        cameraRepository.delete(camera);
    }
}