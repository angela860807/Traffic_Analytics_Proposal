package com.example.traffic.service;

import com.example.traffic.common.enums.ViolationStatus;
import com.example.traffic.domain.Camera;
import com.example.traffic.domain.SpeedViolation;
import com.example.traffic.domain.Vehicle;
import com.example.traffic.domain.VehicleFlowEvent;
import com.example.traffic.dto.request.SpeedViolationCreateRequest;
import com.example.traffic.dto.response.SpeedViolationResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.repository.SpeedViolationRepository;
import com.example.traffic.repository.VehicleRepository;
import com.example.traffic.repository.VehicleFlowEventRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class SpeedViolationService {

    private final SpeedViolationRepository speedViolationRepository;
    private final VehicleRepository vehicleRepository;
    private final CameraRepository cameraRepository;
    private final VehicleFlowEventRepository vehicleFlowEventRepository;

    @Transactional
    public SpeedViolationResponse createViolation(SpeedViolationCreateRequest request) {
        if (request.getMeasuredSpeed() <= request.getSpeedLimit()) {
            throw new BusinessException("Measured speed must exceed speed limit.", HttpStatus.BAD_REQUEST);
        }

        SpeedViolation existingViolation = speedViolationRepository
                .findByFlowEvent_FlowEventId(request.getFlowEventId())
                .orElse(null);
        if (existingViolation != null) {
            existingViolation.getFlowEvent().updateSpeed(existingViolation.getMeasuredSpeed());
            return SpeedViolationResponse.from(existingViolation);
        }

        VehicleFlowEvent flowEvent = vehicleFlowEventRepository.findById(request.getFlowEventId())
                .orElseThrow(() -> new BusinessException("Flow event not found: "
                        + request.getFlowEventId(), HttpStatus.NOT_FOUND));

        Camera camera = cameraRepository.findByCameraCode(request.getCameraCode())
                .orElseThrow(() -> new BusinessException("Unknown camera code: "
                        + request.getCameraCode(), HttpStatus.NOT_FOUND));

        validateFlowEventMatchesRequest(flowEvent, camera, request);

        SpeedViolation violation = SpeedViolation.builder()
                .flowEvent(flowEvent)
                .vehicle(flowEvent.getVehicle())
                .camera(camera)
                .plateNumber(request.getPlateNumber())
                .measuredSpeed(BigDecimal.valueOf(request.getMeasuredSpeed()))
                .speedLimit(BigDecimal.valueOf(request.getSpeedLimit()))
                .violationImagePath(request.getViolationImagePath())
                .violationStatus(ViolationStatus.UNPROCESSED)
                .violatedAt(request.getViolatedAt())
                .build();

        flowEvent.updateSpeed(violation.getMeasuredSpeed());
        return SpeedViolationResponse.from(speedViolationRepository.save(violation));
    }

    private void validateFlowEventMatchesRequest(VehicleFlowEvent flowEvent,
                                                 Camera camera,
                                                 SpeedViolationCreateRequest request) {
        if (!flowEvent.getVehicle().getPlateNumber().equals(request.getPlateNumber())) {
            throw new BusinessException("Plate number does not match flow event vehicle.",
                    HttpStatus.BAD_REQUEST);
        }

        if (!flowEvent.getCamera().getCameraCode().equals(camera.getCameraCode())) {
            throw new BusinessException("Camera code does not match flow event camera.",
                    HttpStatus.BAD_REQUEST);
        }
    }

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
