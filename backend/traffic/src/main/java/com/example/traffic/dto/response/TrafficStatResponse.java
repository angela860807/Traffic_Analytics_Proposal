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
    private final Double averageSpeed;      // 평균 속도
    private final Double congestionScore;   // 혼잡도 점수
    private final Double averageStayTime;   // 평균 체류 시간
    private final Integer duplicateCount;   // 중복 차량 수

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
