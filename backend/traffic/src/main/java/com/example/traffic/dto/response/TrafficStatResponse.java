package com.example.traffic.dto.response;

import com.example.traffic.domain.HourlyTrafficStat;
import lombok.Builder;
import lombok.Getter;

import java.time.LocalDate;

@Getter
@Builder
public class TrafficStatResponse {
    private final String zoneName;
    private final LocalDate statDate;
    private final Integer statHour;
    private final Integer inCount;
    private final Integer outCount;
    private final Integer totalCount;
    private final Double averageSpeed;
    private final Double congestionScore;
    private final Double averageStayTime;
    private final Integer duplicateCount;

    public static TrafficStatResponse from(HourlyTrafficStat stat) {
        return TrafficStatResponse.builder()
                .zoneName(stat.getZone().getZoneName())
                .statDate(stat.getStatDate())
                .statHour(stat.getStatHour())
                .inCount(stat.getInCount())
                .outCount(stat.getOutCount())
                .totalCount(stat.getTotalCount())
                .averageSpeed(stat.getAverageSpeed() != null ? stat.getAverageSpeed().doubleValue() : null)
                .congestionScore(stat.getCongestionScore() != null ? stat.getCongestionScore().doubleValue() : null)
                .averageStayTime(stat.getAverageStayTime() != null ? stat.getAverageStayTime().doubleValue() : null)
                .duplicateCount(stat.getDuplicateVehicleCount())
                .build();
    }
}
