package com.example.traffic.etc;

import com.example.traffic.domain.Zone;
import com.example.traffic.repository.ZoneRepository;
import com.example.traffic.service.HourlyTrafficStatService;
import lombok.RequiredArgsConstructor;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.List;

@Component
@RequiredArgsConstructor
public class TrafficStatScheduler {

    private final HourlyTrafficStatService hourlyTrafficStatService;
    private final ZoneRepository zoneRepository;

    /**
     * 매 시각 0분 0초에 실행 (예: 13:00에는 12:00~12:59 데이터 집계)
     */
    @Scheduled(cron = "0 0 * * * *")
    public void runHourlyAggregation() {
        LocalDateTime targetTime = LocalDateTime.now().minusHours(1); // 직전 시간대[cite: 6]
        List<Zone> zones = zoneRepository.findAll();

        for (Zone zone : zones) {
            hourlyTrafficStatService.aggregateHourlyStats(zone, targetTime); // 서비스 호출[cite: 6]
        }
    }
}
