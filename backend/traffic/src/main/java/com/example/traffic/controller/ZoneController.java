package com.example.traffic.controller;

import com.example.traffic.domain.Zone;
import com.example.traffic.service.ZoneService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/zones")
@RequiredArgsConstructor
public class ZoneController {

    private final ZoneService zoneService;

    // 1. 전체 구역 목록 조회
    @GetMapping
    public List<Zone> getAllZones() {
        return zoneService.findAllZones();
    }

    // 2. 특정 구역 코드(zoneCode)로 조회
    @GetMapping("/code/{zoneCode}")
    public ResponseEntity<Zone> getZoneByCode(@PathVariable String zoneCode) {
        Zone zone = zoneService.findByZoneCode(zoneCode);
        return ResponseEntity.ok(zone);
    }

    // 3. 새로운 구역 등록 (Create)
    @PostMapping
    public Zone createZone(@RequestBody Zone zone) {
        return zoneService.saveZone(zone);
    }

    // 4. 구역 정보 수정 (Update)
    @PutMapping("/{id}")
    public ResponseEntity<Zone> updateZone(@PathVariable Long id, @RequestBody Zone zoneDetails) {
        Zone updatedZone = zoneService.updateZone(id, zoneDetails);
        return ResponseEntity.ok(updatedZone);
    }

    // 5. 구역 삭제 (Delete)
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteZone(@PathVariable Long id) {
        zoneService.deleteZone(id);
        return ResponseEntity.noContent().build(); // 204 No Content 반환
    }
}