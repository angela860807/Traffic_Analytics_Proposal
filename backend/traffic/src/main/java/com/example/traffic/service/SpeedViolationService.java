package com.example.traffic.service;

import com.example.traffic.common.enums.ViolationStatus;
import com.example.traffic.domain.Camera;
import com.example.traffic.domain.Vehicle;
import com.example.traffic.dto.response.SpeedViolationResponse;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.repository.SpeedViolationRepository;
import com.example.traffic.repository.VehicleRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class SpeedViolationService {

    private final SpeedViolationRepository speedViolationRepository;
    private final VehicleRepository vehicleRepository;
    private final CameraRepository cameraRepository;

    public List<SpeedViolationResponse> getVehicleViolations(Long vehicleId) {
        Vehicle vehicle = vehicleRepository.findById(vehicleId)
                .orElseThrow(() -> new IllegalArgumentException("Vehicle not found."));

        return speedViolationRepository.findByVehicleOrderByViolatedAtDesc(vehicle).stream()
                .map(SpeedViolationResponse::from)
                .toList();
    }

    public List<SpeedViolationResponse> getCameraViolations(Long cameraId) {
        Camera camera = cameraRepository.findById(cameraId)
                .orElseThrow(() -> new IllegalArgumentException("Camera not found."));

        return speedViolationRepository.findByCameraOrderByViolatedAtDesc(camera).stream()
                .map(SpeedViolationResponse::from)
                .toList();
    }

    public List<SpeedViolationResponse> getStatusViolations(ViolationStatus violationStatus) {
        return speedViolationRepository.findByViolationStatusOrderByViolatedAtDesc(violationStatus).stream()
                .map(SpeedViolationResponse::from)
                .toList();
    }

    public List<SpeedViolationResponse> getViolationsBetween(LocalDateTime start, LocalDateTime end) {
        return speedViolationRepository.findByViolatedAtBetweenOrderByViolatedAtDesc(start, end).stream()
                .map(SpeedViolationResponse::from)
                .toList();
    }

    public long countViolationsBetween(LocalDateTime start, LocalDateTime end) {
        return speedViolationRepository.countByViolatedAtBetween(start, end);
    }
}
