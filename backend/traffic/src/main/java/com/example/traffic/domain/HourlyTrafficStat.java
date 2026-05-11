package com.example.traffic.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
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

    @Column(nullable = false, columnDefinition = "integer default 0")
    private Integer inCount;

    @Column(nullable = false, columnDefinition = "integer default 0")
    private Integer outCount;

    @Column(nullable = false, columnDefinition = "integer default 0")
    private Integer totalCount;

    @Column(nullable = false, columnDefinition = "numeric(5,2) default 0.00")
    private BigDecimal averageSpeed;

    @Column(nullable = false, columnDefinition = "numeric(5,2) default 0.00")
    private BigDecimal congestionScore;

    @Column(nullable = false, columnDefinition = "numeric(10,2) default 0.00")
    private BigDecimal averageStayTime;

    @Column(nullable = false, columnDefinition = "integer default 0")
    private Integer duplicateVehicleCount;

    @Column(nullable = false, columnDefinition = "bigint default 0")
    private Long lastLogId;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder
    public HourlyTrafficStat(Zone zone, LocalDate statDate, Integer statHour,
                             Integer inCount, Integer outCount, BigDecimal averageSpeed,
                             BigDecimal congestionScore, BigDecimal averageStayTime,
                             Integer duplicateVehicleCount, Long lastLogId) {
        this.zone = zone;
        this.statDate = statDate;
        this.statHour = statHour;
        this.inCount = (inCount != null) ? inCount : 0;
        this.outCount = (outCount != null) ? outCount : 0;

        // ★ 필독: totalCount 계산 로직 추가
        this.totalCount = this.inCount + this.outCount;

        this.averageSpeed = (averageSpeed != null) ? averageSpeed : BigDecimal.ZERO;
        this.congestionScore = (congestionScore != null) ? congestionScore : BigDecimal.ZERO;
        this.averageStayTime = (averageStayTime != null) ? averageStayTime : BigDecimal.ZERO;
        this.duplicateVehicleCount = (duplicateVehicleCount != null) ? duplicateVehicleCount : 0;
        this.lastLogId = (lastLogId != null) ? lastLogId : 0L;
        this.createdAt = LocalDateTime.now();
    }

    public void updateStats(Integer inCount, Integer outCount, BigDecimal averageSpeed,
                            BigDecimal congestionScore, BigDecimal averageStayTime,
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
