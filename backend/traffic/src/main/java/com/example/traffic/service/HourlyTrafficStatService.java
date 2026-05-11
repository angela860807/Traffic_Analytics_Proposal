package com.example.traffic.service;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.domain.HourlyTrafficStat;
import com.example.traffic.domain.VehicleFlowEvent;
import com.example.traffic.domain.Zone;
import com.example.traffic.dto.request.TrafficStatSearchRequest;
import com.example.traffic.dto.response.TrafficStatResponse;
import com.example.traffic.repository.HourlyTrafficStatRepository;
import com.example.traffic.repository.VehicleFlowEventRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class HourlyTrafficStatService {

    private final HourlyTrafficStatRepository hourlyTrafficStatRepository;
    private final VehicleFlowEventRepository vehicleFlowEventRepository;

    public List<TrafficStatResponse> getHourlyStats(TrafficStatSearchRequest request) {
        List<HourlyTrafficStat> stats;

        if (request.getZoneId() != null) {
            stats = hourlyTrafficStatRepository.findByZoneZoneIdAndStatDateOrderByStatHourAsc(
                    request.getZoneId(), request.getStatDate());
        } else {
            stats = hourlyTrafficStatRepository.findByStatDateOrderByStatHourAsc(request.getStatDate());
        }

        return stats.stream()
                .map(TrafficStatResponse::from)
                .toList();
    }

    @Transactional
    public void aggregateHourlyStats(Zone zone, LocalDateTime targetTime) {
        LocalDate statDate = targetTime.toLocalDate();
        int statHour = targetTime.getHour();

        LocalDateTime start = targetTime.withMinute(0).withSecond(0).withNano(0);
        LocalDateTime end = targetTime.withMinute(59).withSecond(59).withNano(999999999);

        List<VehicleFlowEvent> eventsForAnalysis = vehicleFlowEventRepository.findEventsForAnalysis(
                zone, start, end);

        if (eventsForAnalysis.isEmpty()) {
            return;
        }

        long currentInCount = eventsForAnalysis.stream()
                .filter(e -> e.getFlowDirection() == Direction.IN)
                .count();
        long currentOutCount = eventsForAnalysis.stream()
                .filter(e -> e.getFlowDirection() == Direction.OUT)
                .count();

        Double avgSpeed = eventsForAnalysis.stream()
                .mapToDouble(e -> e.getSpeed() != null ? e.getSpeed().doubleValue() : 0.0)
                .average()
                .orElse(0.0);

        Double avgStayTime = eventsForAnalysis.stream()
                .mapToDouble(e -> e.getStayTime() != null ? e.getStayTime() : 0.0)
                .average()
                .orElse(0.0);

        long totalUniqueVehicles = vehicleFlowEventRepository.countUniqueVehicles(zone, start, end);
        int duplicateCount = (int) ((currentInCount + currentOutCount) - totalUniqueVehicles);
        duplicateCount = Math.max(0, duplicateCount);

        Double congestionScore = calculateCongestionScore((int) (currentInCount + currentOutCount), avgSpeed);

        VehicleFlowEvent lastEvent = eventsForAnalysis.get(eventsForAnalysis.size() - 1);
        Long newLastLogId = lastEvent.getSourceDetectionLog() != null
                ? lastEvent.getSourceDetectionLog().getLogId()
                : null;

        HourlyTrafficStat stat = hourlyTrafficStatRepository.findByZoneZoneIdAndStatDateAndStatHour(
                        zone.getZoneId(), statDate, statHour)
                .orElseGet(() -> HourlyTrafficStat.builder()
                        .zone(zone)
                        .statDate(statDate)
                        .statHour(statHour)
                        .build());

        stat.updateStats(
                (int) currentInCount,
                (int) currentOutCount,
                BigDecimal.valueOf(avgSpeed),
                BigDecimal.valueOf(congestionScore),
                BigDecimal.valueOf(avgStayTime),
                duplicateCount,
                newLastLogId
        );

        hourlyTrafficStatRepository.save(stat);
    }

    private Double calculateCongestionScore(int totalCount, Double avgSpeed) {
        if (totalCount == 0) {
            return 0.0;
        }

        double score = (totalCount * 2.0) + (100 - avgSpeed);
        return Math.min(100.0, Math.max(0.0, score));
    }
}
