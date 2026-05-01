package com.example.traffic.service;

import com.example.traffic.domain.Zone;
import com.example.traffic.dto.request.ZoneSaveRequest;
import com.example.traffic.dto.request.ZoneUpdateRequest;
import com.example.traffic.dto.response.ZoneResponse;
import com.example.traffic.repository.ZoneRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class ZoneService {

    private final ZoneRepository zoneRepository;

    @Transactional
    public ZoneResponse saveZone(ZoneSaveRequest request) { // 반환 타입 변경
        validateDuplicateZone(request.getZoneCode());
        Zone zone = Zone.builder()
                .zoneCode(request.getZoneCode())
                .zoneName(request.getZoneName())
                .zoneType(request.getZoneType())
                .build();
        return ZoneResponse.from(zoneRepository.save(zone)); // 저장 후 즉시 DTO 반환
    }

    @Transactional
    public void updateZone(Long zoneId, ZoneUpdateRequest request) {
        Zone zone = zoneRepository.findById(zoneId)
                .orElseThrow(() -> new IllegalArgumentException("해당 구역이 없습니다."));

        // 엔티티 update 파라미터 순서 준수
        zone.update(
                request.getZoneName(),
                zone.getZoneCode(),
                request.getZoneType(),
                request.getIsActive()
        );
    }

    public List<ZoneResponse> findAllZones() {
        return zoneRepository.findAll().stream()
                .map(ZoneResponse::from)
                .toList(); // Collectors.toList() 대신 최신 문법 사용
    }

    private void validateDuplicateZone(String zoneCode) {
        zoneRepository.findByZoneCode(zoneCode)
                .ifPresent(z -> { throw new IllegalStateException("이미 존재하는 구역 코드입니다."); });
    }
}