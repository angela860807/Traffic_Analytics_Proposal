package com.example.traffic.controller;

import com.example.traffic.dto.request.TrafficStatSearchRequest;
import com.example.traffic.dto.response.TrafficStatResponse;
import com.example.traffic.service.HourlyTrafficStatService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/stats/hourly")
@RequiredArgsConstructor
public class HourlyTrafficStatController {

    private final HourlyTrafficStatService hourlyTrafficStatService;

    /**
     * [시간대별 통계 조회] 날짜와 구역 ID를 조건으로 통계 목록을 가져옵니다.
     * GET /api/stats/hourly?statDate=2024-05-20&zoneId=1
     */
    @GetMapping
    public ResponseEntity<List<TrafficStatResponse>> getHourlyStats(
            @ModelAttribute TrafficStatSearchRequest request) {

        List<TrafficStatResponse> stats = hourlyTrafficStatService.getHourlyStats(request);
        return ResponseEntity.ok(stats);
    }

    /**
     * [수동 통계 집계] 특정 구역의 실시간 통계를 강제로 업데이트할 때 사용합니다.
     * (보통은 스케줄러가 자동으로 실행하지만, 테스트나 보정용으로 유용합니다.)
     */
    @PostMapping("/aggregate")
    public ResponseEntity<Void> triggerAggregation(
            @RequestParam Long zoneId,
            @RequestParam String targetTime) {
        // 실제 운영 시에는 zoneId로 Zone 객체를 조회한 후 서비스를 호출하는 로직이 추가됩니다.
        return ResponseEntity.accepted().build();
    }
}