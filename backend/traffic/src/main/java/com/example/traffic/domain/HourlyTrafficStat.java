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

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Builder // 다른 엔티티와 일관성을 위해 추가
    public HourlyTrafficStat(Zone zone, LocalDate statDate, Integer statHour, Integer inCount, Integer outCount) {
        this.zone = zone;
        this.statDate = statDate;
        this.statHour = statHour;
        this.inCount = (inCount != null) ? inCount : 0;
        this.outCount = (outCount != null) ? outCount : 0;
        this.totalCount = this.inCount + this.outCount;
        this.createdAt = LocalDateTime.now();
    }

    // 통계 갱신 로직 (더하기 방식으로 수정하는 것이 실무적일 수 있음)
    public void updateCounts(Integer inCount, Integer outCount) {
        this.inCount = inCount;
        this.outCount = outCount;
        this.totalCount = inCount + outCount;
    }
}
