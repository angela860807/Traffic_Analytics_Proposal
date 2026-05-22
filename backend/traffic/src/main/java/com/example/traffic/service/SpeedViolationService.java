package com.example.traffic.service;

import com.example.traffic.common.enums.ViolationStatus;
import com.example.traffic.domain.Camera;
import com.example.traffic.domain.SpeedViolation;
import com.example.traffic.domain.SpeedViolationReview;
import com.example.traffic.domain.Vehicle;
import com.example.traffic.domain.VehicleFlowEvent;
import com.example.traffic.dto.request.SpeedViolationCreateRequest;
import com.example.traffic.dto.request.SpeedViolationStatusRequest;
import com.example.traffic.dto.response.SpeedViolationResponse;
import com.example.traffic.etc.BusinessException;
import com.example.traffic.repository.CameraRepository;
import com.example.traffic.repository.SpeedViolationRepository;
import com.example.traffic.repository.SpeedViolationReviewRepository;
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
    private final SpeedViolationReviewRepository speedViolationReviewRepository;
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
            return toResponse(existingViolation);
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
        return toResponse(speedViolationRepository.save(violation));
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
                .map(this::toResponse)
                .toList();
    }

    public List<SpeedViolationResponse> getCameraViolations(Long cameraId) {
        Camera camera = cameraRepository.findById(cameraId)
                .orElseThrow(() -> new IllegalArgumentException("Camera not found."));

        return speedViolationRepository.findByCameraOrderByViolatedAtDesc(camera).stream()
                .map(this::toResponse)
                .toList();
    }

    public List<SpeedViolationResponse> getStatusViolations(ViolationStatus violationStatus) {
        return speedViolationRepository.findByViolationStatusOrderByViolatedAtDesc(violationStatus).stream()
                .map(this::toResponse)
                .toList();
    }

    public List<SpeedViolationResponse> getAllViolations() {
        return speedViolationRepository.findAllByOrderByViolatedAtDesc().stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional
    public SpeedViolationResponse updateViolationStatus(Long violationId,
                                                        SpeedViolationStatusRequest request) {
        SpeedViolation violation = speedViolationRepository.findById(violationId)
                .orElseThrow(() -> new BusinessException("Speed violation not found: "
                        + violationId, HttpStatus.NOT_FOUND));

        ViolationStatus fromStatus = violation.getViolationStatus();
        violation.updateStatus(request.getViolationStatus());

        SpeedViolationReview review = SpeedViolationReview.builder()
                .speedViolation(violation)
                .fromStatus(fromStatus)
                .toStatus(request.getViolationStatus())
                .reason(request.getReason())
                .memo(request.getMemo())
                .reviewedBy(request.getReviewer())
                .build();
        speedViolationReviewRepository.save(review);

        return SpeedViolationResponse.from(violation, review);
    }

    public List<SpeedViolationResponse> getViolationsBetween(LocalDateTime start, LocalDateTime end) {
        if (start == null && end == null) {
            return getAllViolations();
        }
        if (start == null || end == null) {
            throw new BusinessException("Both start and end query parameters are required when filtering by date.",
                    HttpStatus.BAD_REQUEST);
        }
        return speedViolationRepository.findByViolatedAtBetweenOrderByViolatedAtDesc(start, end).stream()
                .map(this::toResponse)
                .toList();
    }

    public long countViolationsBetween(LocalDateTime start, LocalDateTime end) {
        return speedViolationRepository.countByViolatedAtBetween(start, end);
    }

    private SpeedViolationResponse toResponse(SpeedViolation violation) {
        SpeedViolationReview latestReview = speedViolationReviewRepository
                .findFirstBySpeedViolationOrderByReviewedAtDescReviewIdDesc(violation)
                .orElse(null);
        return SpeedViolationResponse.from(violation, latestReview);
    }
}
