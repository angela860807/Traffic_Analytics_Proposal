package com.example.traffic.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "hourly_traffic_stats")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class HourlyTrafficStat {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "hourly_stat_id")
    private Long statId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "zone_id", nullable = false)
    private Zone zone;

    @Column(nullable = false)
    private LocalDate statDate;

    @Column(nullable = false)
    private Integer statHour;

    @Column(nullable = false)
    private Integer inCount;

    @Column(nullable = false)
    private Integer outCount;

    @Column(nullable = false)
    private Integer totalCount;

    @Column(precision = 5, scale = 2, nullable = false)
    private Double averageSpeed;

    @Column(precision = 5, scale = 2, nullable = false)
    private Double congestionScore;

    @Column(precision = 10, scale = 2, nullable = false)
    private Double averageStayTime;

    @Column(nullable = false)
    private Integer duplicateVehicleCount;

    @Column(nullable = false)
    private Long lastLogId;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public HourlyTrafficStat(Zone zone, LocalDate statDate, Integer statHour,
                             Integer inCount, Integer outCount, Double averageSpeed,
                             Double congestionScore, Double averageStayTime,
                             Integer duplicateVehicleCount, Long lastLogId) {
        this.zone = zone;
        this.statDate = statDate;
        this.statHour = statHour;
        this.inCount = (inCount != null) ? inCount : 0;
        this.outCount = (outCount != null) ? outCount : 0;

        // ★ 필독: totalCount 계산 로직 추가
        this.totalCount = this.inCount + this.outCount;

        this.averageSpeed = (averageSpeed != null) ? averageSpeed : 0.0;
        this.congestionScore = (congestionScore != null) ? congestionScore : 0.0;
        this.averageStayTime = (averageStayTime != null) ? averageStayTime : 0.0;
        this.duplicateVehicleCount = (duplicateVehicleCount != null) ? duplicateVehicleCount : 0;
        this.lastLogId = (lastLogId != null) ? lastLogId : 0L;
        this.createdAt = LocalDateTime.now();
    }

    public void updateStats(Integer inCount, Integer outCount, Double averageSpeed,
                            Double congestionScore, Double averageStayTime,
                            Integer duplicateVehicleCount, Long lastLogId) {
        this.inCount = inCount;
        this.outCount = outCount;
        this.totalCount = inCount + outCount; // 토탈 자동 갱신
        this.averageSpeed = averageSpeed;
        this.congestionScore = congestionScore;
        this.averageStayTime = averageStayTime;
        this.duplicateVehicleCount = duplicateVehicleCount;
        this.lastLogId = lastLogId; // 어디까지 분석했는지 기록
    }
}
