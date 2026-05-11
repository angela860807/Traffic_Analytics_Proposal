package com.example.traffic.service;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.domain.DetectionLog;
import com.example.traffic.domain.VehicleFlowEvent;
import com.example.traffic.dto.response.FlowEventResponse;
import com.example.traffic.repository.VehicleFlowEventRepository;
import com.example.traffic.repository.ZoneRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Slf4j
@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class VehicleFlowEventService {

    private final VehicleFlowEventRepository flowEventRepository;
    private final ZoneRepository zoneRepository;

    /**
     * [수정 가이드 4번 반영] 차량 통과 이력 조회 로직 이관
     * 서비스 레이어에서 DTO 변환까지 완료하여 컨트롤러로 전달합니다.
     */
    public List<FlowEventResponse> getVehicleHistory(Long vehicleId) {
        return flowEventRepository.findByVehicleIdWithDetails(vehicleId).stream()
                .map(FlowEventResponse::from)
                .toList();
    }

    /**
     * [핵심 로직] 탐지 로그를 분석하여 실시간 교통 흐름 이벤트 확정
     */
    @Transactional // ★ 이 부분을 반드시 추가해야 INSERT가 가능합니다!
    public FlowEventResponse processFlowEvent(DetectionLog currentLog, Double speed, Long stayTime) {
        // 1. 중복 감지 체크 (10초 이내 동일 차량 + 동일 구역)[cite: 5, 6]
        LocalDateTime windowTime = currentLog.getDetectedAt().minusSeconds(10);

        boolean isDuplicate = flowEventRepository.existsByVehicleAndZoneAndEventAtAfter(
                currentLog.getVehicle(),
                currentLog.getCamera().getZone(),
                windowTime
        );

        if (isDuplicate) {

            log.info("중복 감지 스킵: 차량번호 {}는 최근 10초 내에 동일 구역에서 이미 처리되었습니다.",
                    currentLog.getPlateNumber());
            return null;
        }

        // 2. 흐름 유형 판단[cite: 6]
        Direction direction = currentLog.getCamera().getDirectionType();

        // TODO: 만약 direction == BOTH 라면, 추가적인 알고리즘(궤적 분석 등)을 통해
        // 실제 IN/OUT을 확정 짓는 로직을 여기에 확장할 수 있음

        // 3. VehicleFlowEvent 엔티티 생성 및 저장[cite: 2, 6]
        VehicleFlowEvent flowEvent = VehicleFlowEvent.builder()
                .vehicle(currentLog.getVehicle())
                .camera(currentLog.getCamera())
                .zone(currentLog.getCamera().getZone())
                .flowDirection(direction)
                .eventAt(currentLog.getDetectedAt())
                .sourceDetectionLog(currentLog)
                .speed(speed != null ? BigDecimal.valueOf(speed) : null)
                .stayTime(stayTime)
                .build();

        VehicleFlowEvent savedEvent = flowEventRepository.save(flowEvent);

        return FlowEventResponse.from(savedEvent);
    }

    /**
     * [구역별 통계 수치 조회] 특정 시간대 특정 구역의 유입/유출량 확인
     */
    public long getFlowCount(Long zoneId, Direction direction, LocalDateTime start, LocalDateTime end) {
        com.example.traffic.domain.Zone zone = zoneRepository.findById(zoneId)
                .orElseThrow(() -> new IllegalArgumentException("해당 구역을 찾을 수 없습니다."));

        // 지적하신 대로 start, end를 인자로 넣어 쿼리가 정상 작동하게 합니다[cite: 3, 5]
        return flowEventRepository.countByZoneAndFlowDirectionAndEventAtBetween(
                zone, direction, start, end);
    }
}
