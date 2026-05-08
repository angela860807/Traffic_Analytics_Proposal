package com.example.traffic.service;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.domain.HourlyTrafficStat;
import com.example.traffic.domain.Zone;
import com.example.traffic.dto.request.TrafficStatSearchRequest;
import com.example.traffic.dto.response.TrafficStatResponse;
import com.example.traffic.repository.HourlyTrafficStatRepository;
import com.example.traffic.repository.VehicleFlowEventRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class HourlyTrafficStatService {

    // 목록에 있는 실제 파일명으로 주입받습니다.
    private final HourlyTrafficStatRepository hourlyTrafficStatRepository;
    private final VehicleFlowEventRepository vehicleFlowEventRepository;

    /**
     * [조회] 사용자님이 만드신 13개 DTO 중 TrafficStatResponse를 사용해 데이터를 반환합니다.[cite: 7, 8]
     */
    public List<TrafficStatResponse> getHourlyStats(TrafficStatSearchRequest request) {
        List<HourlyTrafficStat> stats;

        if (request.getZoneId() != null) {
            // 특정 구역 조회 시[cite: 6, 7]
            stats = hourlyTrafficStatRepository.findByZoneZoneIdAndStatDateOrderByStatHourAsc(
                    request.getZoneId(), request.getStatDate());
        } else {
            // 날짜별 전체 조회 시[cite: 6, 7]
            stats = hourlyTrafficStatRepository.findByStatDateOrderByStatHourAsc(request.getStatDate());
        }

        return stats.stream()
                .map(TrafficStatResponse::from) // TrafficStatResponse.java의 from 메서드 호출[cite: 8]
                .toList();
    }

    /**
     * [집계] 통계 데이터를 생성하거나 업데이트합니다.[cite: 5, 6]
     */
    @Transactional
    public void aggregateHourlyStats(Zone zone, LocalDateTime targetTime) {
        LocalDate statDate = targetTime.toLocalDate();
        int statHour = targetTime.getHour();

        LocalDateTime start = targetTime.withMinute(0).withSecond(0).withNano(0);
        LocalDateTime end = targetTime.withMinute(59).withSecond(59).withNano(999999999);

        // VehicleFlowEventRepository를 통해 IN/OUT 집계
        int inCount = (int) vehicleFlowEventRepository.countByZoneAndFlowDirectionAndEventAtBetween(
                zone, Direction.IN, start, end);
        int outCount = (int) vehicleFlowEventRepository.countByZoneAndFlowDirectionAndEventAtBetween(
                zone, Direction.OUT, start, end);

        // HourlyTrafficStatRepository 사용[cite: 5, 6]
        HourlyTrafficStat stat = hourlyTrafficStatRepository.findByZoneZoneIdAndStatDateAndStatHour(
                        zone.getZoneId(), statDate, statHour)
                .orElseGet(() -> HourlyTrafficStat.builder()
                        .zone(zone)
                        .statDate(statDate)
                        .statHour(statHour)
                        .build());

        stat.updateCounts(inCount, outCount); // HourlyTrafficStat_7.java의 메서드[cite: 5]
        hourlyTrafficStatRepository.save(stat);
    }
}