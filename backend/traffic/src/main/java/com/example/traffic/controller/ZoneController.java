package com.example.traffic.controller;

import com.example.traffic.dto.request.ZoneSaveRequest;
import com.example.traffic.dto.request.ZoneUpdateRequest;
import com.example.traffic.dto.response.ZoneResponse;
import com.example.traffic.service.ZoneService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/zones")
@RequiredArgsConstructor
public class ZoneController {

    private final ZoneService zoneService;

    @PostMapping
    public ResponseEntity<ZoneResponse> createZone(@RequestBody @Valid ZoneSaveRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(zoneService.saveZone(request));
    }

    @GetMapping
    public ResponseEntity<List<ZoneResponse>> getAllZones() {
        return ResponseEntity.ok(zoneService.findAllZones());
    }

    @PutMapping("/{zoneId}")
    public ResponseEntity<Void> updateZone(
            @PathVariable Long zoneId,
            @RequestBody @Valid ZoneUpdateRequest request) {
        zoneService.updateZone(zoneId, request);
        return ResponseEntity.ok().build();
    }
}