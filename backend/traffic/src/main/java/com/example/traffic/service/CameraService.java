package com.example.traffic.service;

import com.example.traffic.domain.Camera;
import com.example.traffic.domain.Zone;
import com.example.traffic.dto.request.CameraSaveRequest;
import com.example.traffic.dto.request.CameraUpdateRequest;
import com.example.traffic.dto.response.CameraResponse;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.repository.ZoneRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class CameraService {

    private final CameraRepository cameraRepository;
    private final ZoneRepository zoneRepository;

    /**
     * [카메라 등록] 구역 확인 및 코드 중복 체크 후 상세 정보 반환[cite: 2, 12, 25]
     */
    @Transactional
    public CameraResponse saveCamera(CameraSaveRequest request) { // Long -> CameraResponse로 변경 추천[cite: 25]
        Zone zone = zoneRepository.findById(request.getZoneId())
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 구역입니다."));

        cameraRepository.findByCameraCode(request.getCameraCode())
                .ifPresent(c -> { throw new IllegalStateException("이미 등록된 카메라 코드입니다."); });

        Camera camera = Camera.builder()
                .zone(zone)
                .cameraCode(request.getCameraCode())
                .cameraName(request.getCameraName())
                .streamUrl(request.getStreamUrl())
                .directionType(request.getDirectionType())
                .build();

        Camera savedCamera = cameraRepository.save(camera);
        return CameraResponse.from(savedCamera); // 등록 후 즉시 DTO 반환[cite: 25]
    }

    /**
     * [정보 수정] 엔티티 파라미터 순서 (name, code, url, direction, active) 준수[cite: 2, 19]
     */
    @Transactional
    public void updateCamera(Long cameraId, CameraUpdateRequest request) {
        Camera camera = cameraRepository.findById(cameraId)
                .orElseThrow(() -> new IllegalArgumentException("해당 카메라를 찾을 수 없습니다."));

        // cameraCode는 고유값이므로 DTO에 없으며, 기존 값을 유지하여 업데이트[cite: 2, 19]
        camera.update(
                request.getCameraName(),
                camera.getCameraCode(),
                request.getStreamUrl(),
                request.getDirectionType(),
                request.getIsActive()
        );
    }

    /**
     * [목록 조회] N+1 문제를 방지하려면 레포지토리에서 Fetch Join 고려 필요[cite: 2, 25]
     */
    public List<CameraResponse> findByZone(Long zoneId) {
        return cameraRepository.findByZoneZoneId(zoneId).stream()
                .map(CameraResponse::from)
                .toList();
    }

    public CameraResponse getCamera(Long cameraId) {
        return cameraRepository.findById(cameraId)
                .map(CameraResponse::from)
                .orElseThrow(() -> new IllegalArgumentException("해당 카메라가 없습니다."));
    }
}