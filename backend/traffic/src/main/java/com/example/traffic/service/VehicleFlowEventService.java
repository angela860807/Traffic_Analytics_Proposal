package com.example.traffic.service;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.domain.DetectionAnalysisResult;
import com.example.traffic.domain.DetectionLog;
import com.example.traffic.domain.Vehicle;
import com.example.traffic.domain.VehicleFlowEvent;
import com.example.traffic.dto.response.FlowEventResponse;
import com.example.traffic.repository.VehicleFlowEventRepository;
import com.example.traffic.repository.ZoneRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Slf4j
@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class VehicleFlowEventService {

    private final VehicleFlowEventRepository flowEventRepository;
    private final ZoneRepository zoneRepository;
    private final TrafficAnalysisIndexService trafficAnalysisIndexService;

    public List<FlowEventResponse> getVehicleHistory(Long vehicleId) {
        return flowEventRepository.findByVehicleIdWithDetails(vehicleId).stream()
                .map(FlowEventResponse::from)
                .toList();
    }

    public boolean hasRecentDuplicate(Vehicle vehicle, DetectionLog detectionLog) {
        LocalDateTime windowTime = detectionLog.getDetectedAt().minusSeconds(10);
        return flowEventRepository.existsByVehicleAndZoneAndEventAtBetween(
                vehicle,
                detectionLog.getCamera().getZone(),
                windowTime,
                detectionLog.getDetectedAt()
        );
    }

    public Optional<VehicleFlowEvent> findRecentDuplicate(Vehicle vehicle, DetectionLog detectionLog) {
        LocalDateTime windowTime = detectionLog.getDetectedAt().minusSeconds(10);
        return flowEventRepository.findFirstByVehicleAndZoneAndEventAtBetweenOrderByEventAtDesc(
                vehicle,
                detectionLog.getCamera().getZone(),
                windowTime,
                detectionLog.getDetectedAt()
        );
    }

    @Transactional
    public FlowEventResponse processFlowEvent(DetectionLog detectionLog,
                                              DetectionAnalysisResult analysisResult,
                                              Vehicle vehicle) {
        if (hasRecentDuplicate(vehicle, detectionLog)) {
            log.info("Duplicate detection skipped. plateNumber={}", analysisResult.getPlateNumber());
            return null;
        }

        Direction direction = detectionLog.getCamera().getDirectionType();
        VehicleFlowEvent flowEvent = VehicleFlowEvent.builder()
                .vehicle(vehicle)
                .camera(detectionLog.getCamera())
                .zone(detectionLog.getCamera().getZone())
                .flowDirection(direction)
                .eventAt(detectionLog.getDetectedAt())
                .sourceDetectionLog(detectionLog)
                .sourceAnalysisResult(analysisResult)
                .build();

        VehicleFlowEvent savedEvent = flowEventRepository.save(flowEvent);
        trafficAnalysisIndexService.updateCheckpoint(
                savedEvent.getZone(),
                savedEvent.getFlowEventId(),
                savedEvent.getSourceDetectionLog().getLogId(),
                savedEvent.getEventAt()
        );

        return FlowEventResponse.from(savedEvent);
    }

    public long getFlowCount(Long zoneId, Direction direction, LocalDateTime start, LocalDateTime end) {
        com.example.traffic.domain.Zone zone = zoneRepository.findById(zoneId)
                .orElseThrow(() -> new IllegalArgumentException("Zone not found."));

        return flowEventRepository.countByZoneAndFlowDirectionAndEventAtBetween(
                zone, direction, start, end);
    }
}
