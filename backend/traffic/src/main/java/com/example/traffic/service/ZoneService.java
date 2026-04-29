package com.example.traffic.service;

import com.example.traffic.domain.Zone;
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

    // 1. 전체 구역 조회
    public List<Zone> findAllZones() {
        return zoneRepository.findAll();
    }

    // 2. 구역 코드(zoneCode)로 조회 (추가하신 기능 활용)
    public Zone findByZoneCode(String zoneCode) {
        return zoneRepository.findByZoneCode(zoneCode)
                .orElseThrow(() -> new IllegalArgumentException("해당 구역 코드가 없습니다. code=" + zoneCode));
    }

    // 3. 구역 등록 (Create)
    @Transactional
    public Zone saveZone(Zone zone) {
        return zoneRepository.save(zone);
    }

    // 4. 구역 수정 (Update)
    @Transactional
    public Zone updateZone(Long id, Zone zoneDetails) {
        Zone zone = zoneRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("해당 구역이 없습니다. id=" + id));

        // Zone 엔티티에 추가한 update 메서드 호출
        // isActive() 게터 명칭 주의!
        zone.update(
                zoneDetails.getZoneName(),
                zoneDetails.getZoneCode(),
                zoneDetails.getZoneType(),
                zoneDetails.isActive()
        );

        return zone;
    }

    // 5. 구역 삭제 (Delete)
    @Transactional
    public void deleteZone(Long id) {
        Zone zone = zoneRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("해당 구역이 없습니다. id=" + id));
        zoneRepository.delete(zone);
    }
}