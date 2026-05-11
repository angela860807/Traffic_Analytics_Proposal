package com.example.traffic.repository;

import com.example.traffic.domain.HourlyTrafficStat;
import org.springframework.data.jpa.repository.JpaRepository;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

public interface HourlyTrafficStatRepository extends JpaRepository<HourlyTrafficStat, Long> {
    // 특정 구역의 특정 날짜/시간 통계 데이터 찾기
    Optional<HourlyTrafficStat> findByZoneZoneIdAndStatDateAndStatHour(Long zoneId, LocalDate statDate, Integer statHour);

    // 특정 구역의 일일 통계 목록 조회 (차트용)[cite: 4, 8]
    List<HourlyTrafficStat> findByZoneZoneIdAndStatDateOrderByStatHourAsc(Long zoneId, LocalDate statDate);

    // 특정 날짜의 모든 구역 통계 목록을 시간순으로 조회
    List<HourlyTrafficStat> findByStatDateOrderByStatHourAsc(LocalDate statDate);

    Optional<HourlyTrafficStat> findFirstByZoneZoneIdOrderByStatDateDescStatHourDesc(Long zoneId);
}