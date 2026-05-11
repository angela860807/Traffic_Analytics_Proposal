package com.example.traffic.service;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.domain.HourlyTrafficStat;
import com.example.traffic.domain.TrafficAnalysisIndex;
import com.example.traffic.domain.VehicleFlowEvent;
import com.example.traffic.domain.Zone;
import com.example.traffic.dto.request.TrafficStatSearchRequest;
import com.example.traffic.dto.response.TrafficStatResponse;
import com.example.traffic.repository.HourlyTrafficStatRepository;
import com.example.traffic.repository.TrafficAnalysisIndexRepository;
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

    // 목록에 있는 실제 파일명으로 주입받습니다.
    private final HourlyTrafficStatRepository hourlyTrafficStatRepository;
    private final VehicleFlowEventRepository vehicleFlowEventRepository;
    private final TrafficAnalysisIndexRepository trafficAnalysisIndexRepository;


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

        // 1. [핵심 수정] 이전 분석 지점(lastLogId) 확인
        // 정의서 3.3절: 중복 분석 방지를 위해 마지막 기록을 먼저 찾습니다.
        TrafficAnalysisIndex index = trafficAnalysisIndexRepository.findTopByOrderByIdDesc()
                .orElseGet(() -> TrafficAnalysisIndex.builder()
                        .lastSeq(0L)
                        .lastLogId(0L)
                        .lastLogTime(null)
                        .build());

        Long lastSeq = index.getLastSeq() != null ? index.getLastSeq() : 0L;


        // 2. 분석 대상 데이터 조회 (앞서 수정한 레포지토리 메서드 활용)
        // 정의서 3.3절: lastLogId 이후의 데이터만 가져와서 분석합니다.
        List<VehicleFlowEvent> eventsForAnalysis = vehicleFlowEventRepository.findEventsForAnalysis(
                zone, start, end, lastSeq);

        if (eventsForAnalysis.isEmpty()) return; // 분석할 신규 데이터가 없으면 종료

        // 3. 지표 계산 (정의서 3.3절 분석 항목)
        long currentInCount = eventsForAnalysis.stream().filter(e -> e.getFlowDirection() == Direction.IN).count();
        long currentOutCount = eventsForAnalysis.stream().filter(e -> e.getFlowDirection() == Direction.OUT).count();

        Double avgSpeed = eventsForAnalysis.stream()
                .mapToDouble(e -> e.getSpeed() != null ? e.getSpeed().doubleValue() : 0.0)
                .average().orElse(0.0);

        Double avgStayTime = eventsForAnalysis.stream()
                .mapToDouble(e -> e.getStayTime() != null ? e.getStayTime() : 0.0)
                .average().orElse(0.0);

        // 4. 중복 차량 수 계산 (정의서 3.6절)
        long totalUniqueVehicles = vehicleFlowEventRepository.countUniqueVehicles(zone, start, end);
        int duplicateCount = (int) ((currentInCount + currentOutCount) - totalUniqueVehicles);
        duplicateCount = Math.max(0, duplicateCount);

        // 5. 혼잡도 점수 산출 (정의서 3.7절)
        Double congestionScore = calculateCongestionScore((int)(currentInCount + currentOutCount), avgSpeed);

        // 6. 새로운 마지막 로그 ID 파악
        VehicleFlowEvent lastEvent = eventsForAnalysis.get(eventsForAnalysis.size() - 1);

        Long newLastLogId = lastEvent.getSourceDetectionLog() != null
                ? lastEvent.getSourceDetectionLog().getLogId()
                : null;



        // 7. 엔티티 저장 또는 갱신
        HourlyTrafficStat stat = hourlyTrafficStatRepository.findByZoneZoneIdAndStatDateAndStatHour(
                        zone.getZoneId(), statDate, statHour)
                .orElseGet(() -> HourlyTrafficStat.builder()
                        .zone(zone)
                        .statDate(statDate)
                        .statHour(statHour)
                        .build());

        // 수정된 엔티티 메서드 호출
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

        index.update(
                lastEvent.getFlowEventId(),
                newLastLogId,
                lastEvent.getEventAt()
        );

        trafficAnalysisIndexRepository.save(index);


    }

    private Double calculateCongestionScore(int totalCount, Double avgSpeed) {
        if (totalCount == 0) return 0.0;
        // 예시: 속도가 낮고 차량수가 많을수록 점수 상승
        double score = (totalCount * 2.0) + (100 - avgSpeed);
        return Math.min(100.0, Math.max(0.0, score));
    }
}
