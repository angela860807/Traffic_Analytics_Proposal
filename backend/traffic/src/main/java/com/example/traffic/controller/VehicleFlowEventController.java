package com.example.traffic.controller;

import com.example.traffic.common.enums.Direction;
import com.example.traffic.dto.response.CommonResponse;
import com.example.traffic.dto.response.FlowEventResponse;
import com.example.traffic.service.VehicleFlowEventService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/flow-events")
@RequiredArgsConstructor
public class VehicleFlowEventController {

    private final VehicleFlowEventService flowEventService;

    /**
     * [구역별 유입/유출 카운트][cite: 3, 5, 7]
     * GET /api/flow-events/stats/count?zoneId=1&direction=IN&start=2024-01-01T00:00:00&end=2024-01-01T23:59:59
     */
    @GetMapping("/stats/count")
    public ResponseEntity<Long> getFlowCount(
            @RequestParam Long zoneId,
            @RequestParam Direction direction,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime end) {

        long count = flowEventService.getFlowCount(zoneId, direction, start, end);
        return ResponseEntity.ok(count);
    }

    /**
     * [차량 통과 이력 조회] 특정 차량이 어디를 지나갔는지 확인
     */
    @GetMapping("/vehicle/{vehicleId}")
    public ResponseEntity<CommonResponse<List<FlowEventResponse>>> getVehicleHistory(@PathVariable Long vehicleId) {
        // 서비스에서 DTO 변환까지 마친 리스트를 받아옵니다.
        List<FlowEventResponse> history = flowEventService.getVehicleHistory(vehicleId);
        return ResponseEntity.ok(CommonResponse.success(history, "차량 통과 이력 조회 성공"));
    }
}