package com.example.traffic.controller;

import com.example.traffic.dto.request.VehicleStatusRequest;
import com.example.traffic.dto.response.VehicleResponse;
import com.example.traffic.service.VehicleService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/vehicles")
@RequiredArgsConstructor
public class VehicleController {

    private final VehicleService vehicleService;

    /**
     * [차량 상세 정보 조회]
     */
    @GetMapping("/{vehicleId}")
    public ResponseEntity<VehicleResponse> getVehicle(@PathVariable Long vehicleId) {
        return ResponseEntity.ok(vehicleService.getVehicle(vehicleId));
    }

    /**
     * [차량 상태 변경] (예: ACTIVE -> WANTED)[cite: 14]
     */
    @PatchMapping("/{vehicleId}/status")
    public ResponseEntity<Void> updateStatus(
            @PathVariable Long vehicleId,
            @RequestBody @Valid VehicleStatusRequest request) {
        vehicleService.updateVehicleStatus(vehicleId, request);
        return ResponseEntity.ok().build();
    }
}